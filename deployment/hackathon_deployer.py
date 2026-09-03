"""Reusable definition generators for the Fabric Data Agent hackathon notebook."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any, Iterable

PROFILE_SCHEMA_VERSION = "1.0"
ONTOLOGY_NAMESPACE = uuid.UUID("6d54b7e0-a028-45e9-b621-276429753dd8")
SEMANTIC_MODEL_NAMESPACE = uuid.UUID("4f5c08d6-c125-42a5-a79c-c18ccb8f363f")
MEASURES_TABLE_NAME = "_Measures"


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _duplicates(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def validate_profile(profile: dict[str, Any], repo_root: str | Path | None = None) -> None:
    """Validate cross-reference rules that JSON Schema cannot express."""
    errors: list[str] = []
    if profile.get("schemaVersion") != PROFILE_SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {PROFILE_SCHEMA_VERSION!r}")

    tables = profile.get("tables", [])
    physical_tables = {table["lakehouseName"]: table for table in tables}
    model_tables = {table["modelName"]: table for table in tables}
    artifact_aliases = set(profile.get("artifacts", {}))

    for label, values in (
        ("lakehouse table", physical_tables),
        ("model table", model_tables),
    ):
        duplicate_values = _duplicates(table[f"{label.split()[0]}Name"] for table in tables)
        if duplicate_values:
            errors.append(f"Duplicate {label} names: {duplicate_values}")

    source_headers: dict[str, set[str]] = {}
    if repo_root is not None:
        import csv

        root = Path(repo_root)
        for table in tables:
            source_path = root / table["sourcePath"]
            if not source_path.is_file():
                errors.append(f"Source file does not exist: {table['sourcePath']}")
                continue
            with source_path.open("r", encoding="utf-8", newline="") as handle:
                header = next(csv.reader(handle), [])
            actual = set(header)
            expected = {column["source"] for column in table["columns"]}
            source_headers[table["lakehouseName"]] = actual
            if actual != expected:
                errors.append(
                    f"CSV/profile columns differ for {table['sourcePath']}: "
                    f"missing={sorted(actual - expected)}, extra={sorted(expected - actual)}"
                )

    all_measures: dict[str, dict[str, Any]] = {}
    for model_name, model in profile.get("semanticModels", {}).items():
        for table_name in model.get("tableNames", []):
            if table_name not in model_tables and table_name != MEASURES_TABLE_NAME:
                errors.append(f"{model_name} model references unknown table {table_name!r}")
        measure_names = [measure["name"] for measure in model.get("measures", [])]
        duplicates = _duplicates(measure_names)
        if duplicates:
            errors.append(f"Duplicate measures in {model_name}: {duplicates}")
        for measure in model.get("measures", []):
            if measure["table"] not in model.get("tableNames", []):
                errors.append(
                    f"Measure {measure['name']!r} has unknown home table "
                    f"{measure['table']!r} in {model_name}"
                )
        all_measures.update({measure["name"]: measure for measure in model.get("measures", [])})

    optimized = profile.get("semanticModels", {}).get("optimized", {})
    optimized_tables = set(optimized.get("tableNames", []))
    for relationship in profile.get("relationships", []):
        for side in ("from", "to"):
            table_name = relationship[f"{side}Table"]
            column_name = relationship[f"{side}Column"]
            if table_name not in optimized_tables:
                errors.append(f"Relationship {relationship['name']!r} references unknown table {table_name!r}")
                continue
            columns = {column["name"] for column in model_tables[table_name]["columns"]}
            if column_name not in columns:
                errors.append(
                    f"Relationship {relationship['name']!r} references unknown column "
                    f"{table_name}[{column_name}]"
                )

    for table_name, objects in profile.get("ai", {}).get("schema", {}).items():
        if table_name == MEASURES_TABLE_NAME:
            for object_name in objects:
                if object_name not in all_measures:
                    errors.append(f"AI schema object does not resolve: {table_name}[{object_name}]")
            continue
        if table_name not in model_tables:
            errors.append(f"AI schema references unknown table {table_name!r}")
            continue
        columns = {column["name"] for column in model_tables[table_name]["columns"]}
        for object_name in objects:
            if object_name not in columns and object_name not in all_measures:
                errors.append(f"AI schema object does not resolve: {table_name}[{object_name}]")

    for source in profile.get("agent", {}).get("sources", []):
        if source.get("artifact") not in artifact_aliases:
            errors.append(f"Agent source uses unknown artifact alias {source.get('artifact')!r}")
        if source.get("artifact") == "optimizedModel":
            unknown = set(source.get("objects", [])) - optimized_tables
        else:
            unknown = set(source.get("objects", [])) - set(physical_tables)
        if unknown:
            errors.append(f"Agent source {source['name']!r} references unknown objects: {sorted(unknown)}")

    ontology = profile.get("ontology", {})
    entity_names = {entity["name"] for entity in ontology.get("entities", [])}
    for entity in ontology.get("entities", []):
        table = physical_tables.get(entity["table"])
        if table is None:
            errors.append(f"Ontology entity {entity['name']!r} references unknown table {entity['table']!r}")
            continue
        columns = {column["source"] for column in table["columns"]}
        for field in ("key", "displayProperty"):
            if entity[field] not in columns:
                errors.append(f"Ontology entity {entity['name']!r} has unknown {field} {entity[field]!r}")
    for relationship in ontology.get("relationships", []):
        if relationship["from"] not in entity_names or relationship["to"] not in entity_names:
            errors.append(f"Ontology relationship {relationship['name']!r} has an unknown entity endpoint")
        table = physical_tables.get(relationship["table"])
        if table is None:
            errors.append(f"Ontology relationship {relationship['name']!r} has unknown link table")
            continue
        columns = {column["source"] for column in table["columns"]}
        for field in ("fromColumn", "toColumn"):
            if relationship[field] not in columns:
                errors.append(f"Ontology relationship {relationship['name']!r} has unknown {field}")

    if errors:
        raise ValueError("Invalid domain profile:\n- " + "\n- ".join(errors))


def _tmdl_name(value: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        return value
    return "'" + value.replace("'", "''") + "'"


def _description(value: str) -> str:
    return "\n".join(f"/// {line}" for line in value.splitlines() if line.strip())


def _semantic_model_uuid(scope: str) -> str:
    return str(uuid.uuid5(SEMANTIC_MODEL_NAMESPACE, scope))


def _render_measure(measure: dict[str, Any], lineage_scope: str) -> list[str]:
    expression = measure["expression"]
    lineage_tag = _semantic_model_uuid(f"{lineage_scope}:measure:{measure['name']}")
    lines = [f"\t{_description(measure['description'])}", f"\tmeasure {_tmdl_name(measure['name'])} = {expression}"]
    lines.append(f"\t\tlineageTag: {lineage_tag}")
    lines.append(f"\t\tformatString: {measure['formatString']}")
    return lines


def _render_column(column: dict[str, Any], lineage_scope: str) -> list[str]:
    # Tabular models represent both source dates and timestamps as dateTime.
    tmdl_type = "dateTime" if column["type"] == "date" else column["type"]
    lineage_tag = _semantic_model_uuid(f"{lineage_scope}:column:{column['name']}")
    lines = []
    if column.get("description"):
        lines.append(f"\t{_description(column['description'])}")
    lines.extend(
        [
            f"\tcolumn {_tmdl_name(column['name'])}",
            f"\t\tlineageTag: {lineage_tag}",
            f"\t\tdataType: {tmdl_type}",
            "\t\tsummarizeBy: none",
            f"\t\tsourceColumn: {column['source']}",
        ]
    )
    if column.get("hidden"):
        lines.append("\t\tisHidden")
    if column.get("formatString"):
        lines.append(f"\t\tformatString: {column['formatString']}")
    return lines


def render_table_tmdl(
    table: dict[str, Any],
    measures: list[dict[str, Any]],
    expression_name: str,
    lineage_scope: str,
) -> str:
    table_scope = f"{lineage_scope}:table:{table['modelName']}"
    lines = [
        _description(table["description"]),
        f"table {_tmdl_name(table['modelName'])}",
        f"\tlineageTag: {_semantic_model_uuid(table_scope)}",
        "",
    ]
    for measure in measures:
        lines.extend(_render_measure(measure, table_scope))
        lines.append("")
    for column in table["columns"]:
        lines.extend(_render_column(column, table_scope))
        lines.append("")
    lines.extend(
        [
            f"\tpartition {_tmdl_name(table['modelName'])} = entity",
            "\t\tmode: directLake",
            "\t\tsource",
            f"\t\t\tentityName: {table['lakehouseName']}",
            f"\t\t\texpressionSource: {_tmdl_name(expression_name)}",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_measures_table_tmdl(measures: list[dict[str, Any]], lineage_scope: str) -> str:
    """Render a blank calculated table holding every measure, decoupled from data tables."""
    table_scope = f"{lineage_scope}:table:{MEASURES_TABLE_NAME}"
    lines = [
        f"table {_tmdl_name(MEASURES_TABLE_NAME)}",
        f"\tlineageTag: {_semantic_model_uuid(table_scope)}",
        "",
    ]
    for measure in measures:
        lines.extend(_render_measure(measure, table_scope))
        lines.append("")
    lines.extend(
        [
            "\tcolumn Column1",
            f"\t\tlineageTag: {_semantic_model_uuid(f'{table_scope}:column:Column1')}",
            "\t\tdataType: int64",
            "\t\tisHidden",
            "\t\tsummarizeBy: none",
            "\t\tsourceColumn: Column1",
            "",
            f"\tpartition {_tmdl_name(MEASURES_TABLE_NAME)} = calculated",
            "\t\tmode: import",
            "\t\tsource =",
            '\t\t\tROW("Column1", 0)',
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_relationships_tmdl(profile: dict[str, Any]) -> str:
    blocks = []
    for relationship in profile.get("relationships", []):
        block = [
            f"relationship {_tmdl_name(relationship['name'])}",
            f"\tfromColumn: {_tmdl_name(relationship['fromTable'])}.{_tmdl_name(relationship['fromColumn'])}",
            f"\ttoColumn: {_tmdl_name(relationship['toTable'])}.{_tmdl_name(relationship['toColumn'])}",
        ]
        if relationship.get("crossFilter") == "bothDirections":
            block.append("\tcrossFilteringBehavior: bothDirections")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks) + "\n"


def render_semantic_model_parts(
    profile: dict[str, Any],
    model_key: str,
    workspace_id: str,
    lakehouse_id: str,
    onelake_endpoint: str = "onelake.dfs.fabric.microsoft.com",
) -> dict[str, str]:
    """Generate a complete TMDL definition without any PBIP/PBIX dependency."""
    model = profile["semanticModels"][model_key]
    table_map = {table["modelName"]: table for table in profile["tables"]}
    expression_name = "DirectLake_Source"
    source_url = f"https://{onelake_endpoint}/{workspace_id}/{lakehouse_id}"
    expression = (
        f"expression {_tmdl_name(expression_name)} =\n"
        "\tlet\n"
        f"\t\tSource = AzureStorage.DataLake(\"{source_url}\", [HierarchicalNavigation=true])\n"
        "\tin\n"
        "\t\tSource\n"
    )
    model_lines = [
        "model Model",
        f"\tculture: {profile['domain']['culture']}",
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
        f"\tsourceQueryCulture: {profile['domain']['culture']}",
        "",
        expression.rstrip(),
        "",
    ]
    model_lines.extend(f"ref table {_tmdl_name(name)}" for name in model["tableNames"])

    parts = {
        "definition.pbism": json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
                "version": "4.2",
                "settings": {"qnaEnabled": True},
            },
            separators=(",", ":"),
        ),
        "definition/database.tmdl": "database\n\tcompatibilityLevel: 1702\n\tcompatibilityMode: powerBI\n",
        "definition/model.tmdl": "\n".join(model_lines).rstrip() + "\n",
    }
    for table_name in model["tableNames"]:
        if table_name == MEASURES_TABLE_NAME:
            parts[f"definition/tables/{table_name}.tmdl"] = render_measures_table_tmdl(
                model.get("measures", []),
                f"{profile['domain']['id']}:{model_key}",
            )
            continue
        parts[f"definition/tables/{table_name}.tmdl"] = render_table_tmdl(
            table_map[table_name],
            [],
            expression_name,
            f"{profile['domain']['id']}:{model_key}",
        )
    if model.get("useRelationships") and profile.get("relationships"):
        parts["definition/relationships.tmdl"] = render_relationships_tmdl(profile)
    return parts


def render_copilot_parts(profile: dict[str, Any]) -> dict[str, str]:
    """Render Copilot parts that do not depend on semantic-model lineage tags."""
    prompts = [candidate["question"] for candidate in profile["ai"]["verifiedAnswerCandidates"]]
    return {
        "Copilot/Instructions/instructions.md": "# AI Instructions for Semantic Model\n\n" + profile["ai"]["instructions"].strip() + "\n",
        "Copilot/settings.json": json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/copilot/settings/1.0.0/schema.json",
                "indexingEnabled": True,
            },
            separators=(",", ":"),
        ),
        "Copilot/examplePrompts.json": json.dumps(
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/copilot/examplePrompts/1.0.0/schema.json",
                "prompts": prompts,
            },
            separators=(",", ":"),
        ),
    }


def _extract_lineage_tags(tmdl_parts: dict[str, str]) -> dict[str, dict[str, Any]]:
    objects: dict[str, dict[str, Any]] = {}
    declaration = re.compile(r"^\s*(table|column|measure)\s+('(?:''|[^'])+'|\S+)")
    lineage = re.compile(r"^\s*lineageTag:\s*([0-9a-fA-F-]+)\s*$")
    for path, content in tmdl_parts.items():
        if not path.startswith("definition/tables/") or not path.endswith(".tmdl"):
            continue
        current: tuple[str, str] | None = None
        table_name: str | None = None
        for line in content.splitlines():
            match = declaration.match(line)
            if match:
                kind, raw_name = match.groups()
                name = raw_name[1:-1].replace("''", "'") if raw_name.startswith("'") else raw_name
                current = (kind, name)
                if kind == "table":
                    table_name = name
                    objects.setdefault(name, {"columns": {}, "measures": {}})
                continue
            tag_match = lineage.match(line)
            if not tag_match or current is None or table_name is None:
                continue
            kind, name = current
            if kind == "table":
                objects[table_name]["id"] = tag_match.group(1)
            else:
                objects[table_name][f"{kind}s"][name] = tag_match.group(1)
    return objects


def render_copilot_schema(profile: dict[str, Any], tmdl_parts: dict[str, str]) -> str:
    """Build Copilot/schema.json from TMDL lineage tags."""
    lineage = _extract_lineage_tags(tmdl_parts)
    tables = []
    missing = []
    for table_name, visible_objects in profile["ai"]["schema"].items():
        table_lineage = lineage.get(table_name, {})
        if "id" not in table_lineage:
            missing.append(f"table {table_name}")
            continue
        visible = set(visible_objects)
        columns = []
        for column_name, object_id in table_lineage.get("columns", {}).items():
            columns.append(
                {
                    "id": object_id,
                    "name": column_name,
                    "visibility": "Visible" if column_name in visible else "Hidden",
                    "synonyms": [],
                }
            )
        measures = []
        for measure_name, object_id in table_lineage.get("measures", {}).items():
            measures.append(
                {
                    "id": object_id,
                    "name": measure_name,
                    "visibility": "Visible" if measure_name in visible else "Hidden",
                    "synonyms": [],
                }
            )
        unresolved = (
            visible
            - {item["name"] for item in columns}
            - {item["name"] for item in measures}
        )
        if unresolved:
            missing.extend(f"{table_name}[{name}]" for name in sorted(unresolved))
        tables.append(
            {
                "id": table_lineage["id"],
                "name": table_name,
                "visibility": "Visible",
                "columns": columns,
                "measures": measures,
                "hierarchies": [],
                "synonyms": [],
            }
        )
    if missing:
        raise ValueError("Missing lineage tags for: " + ", ".join(missing))
    return json.dumps(
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/copilot/schema/1.0.0/schema.json",
            "tables": tables,
        },
        separators=(",", ":"),
    )


def _base64_text(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def definition_payload(parts: dict[str, str], definition_format: str | None = None) -> dict[str, Any]:
    definition: dict[str, Any] = {
        "parts": [
            {"path": path, "payload": _base64_text(content), "payloadType": "InlineBase64"}
            for path, content in sorted(parts.items())
        ]
    }
    if definition_format:
        definition["format"] = definition_format
    return {"definition": definition}


def semantic_model_create_payload(display_name: str, parts: dict[str, str]) -> dict[str, Any]:
    payload = definition_payload(parts, "TMDL")
    payload["displayName"] = display_name
    return payload


def _stable_int(scope: str) -> str:
    value = int.from_bytes(hashlib.sha256(scope.encode("utf-8")).digest()[:8], "big")
    return str((value & ((1 << 63) - 1)) or 1)


def _stable_uuid(scope: str) -> str:
    return str(uuid.uuid5(ONTOLOGY_NAMESPACE, scope))


def _ontology_type(column_type: str) -> str:
    return {
        "string": "String",
        "int64": "BigInt",
        "double": "Double",
        "date": "DateTime",
        "dateTime": "DateTime",
        "boolean": "Boolean",
    }[column_type]


def render_ontology_parts(
    profile: dict[str, Any], workspace_id: str, lakehouse_id: str
) -> dict[str, str]:
    """Generate deterministic preview Ontology parts from the domain profile."""
    name = profile["artifacts"]["ontology"]
    physical_tables = {table["lakehouseName"]: table for table in profile["tables"]}
    entities = {entity["name"]: entity for entity in profile.get("ontology", {}).get("entities", [])}
    entity_ids = {entity_name: _stable_int(f"{profile['domain']['id']}:entity:{entity_name}") for entity_name in entities}
    property_ids: dict[tuple[str, str], str] = {}
    parts = {
        ".platform": json.dumps({"metadata": {"type": "Ontology", "displayName": name}}, separators=(",", ":")),
        "definition.json": "{}",
    }

    for entity_name, entity in entities.items():
        table = physical_tables[entity["table"]]
        properties = []
        bindings = []
        for column in table["columns"]:
            property_name = re.sub(r"[^A-Za-z0-9_-]", "", column["name"])
            if not property_name or not property_name[0].isalpha():
                property_name = "Field" + property_name
            property_id = _stable_int(f"{profile['domain']['id']}:property:{entity_name}:{column['source']}")
            property_ids[(entity_name, column["source"])] = property_id
            properties.append(
                {
                    "id": property_id,
                    "name": property_name[:26],
                    "valueType": _ontology_type(column["type"]),
                }
            )
            bindings.append({"sourceColumnName": column["source"], "targetPropertyId": property_id})
        entity_id = entity_ids[entity_name]
        entity_definition = {
            "id": entity_id,
            "namespace": "usertypes",
            "name": entity_name,
            "entityIdParts": [property_ids[(entity_name, entity["key"])]],
            "displayNamePropertyId": property_ids[(entity_name, entity["displayProperty"])],
            "namespaceType": "Custom",
            "visibility": "Visible",
            "properties": properties,
            "timeseriesProperties": [],
        }
        binding_id = _stable_uuid(f"{profile['domain']['id']}:binding:{entity_name}")
        binding = {
            "id": binding_id,
            "dataBindingConfiguration": {
                "dataBindingType": "NonTimeSeries",
                "propertyBindings": bindings,
                "sourceTableProperties": {
                    "sourceType": "LakehouseTable",
                    "workspaceId": workspace_id,
                    "itemId": lakehouse_id,
                    "sourceTableName": entity["table"],
                },
            },
        }
        parts[f"EntityTypes/{entity_id}/definition.json"] = json.dumps(entity_definition, separators=(",", ":"))
        parts[f"EntityTypes/{entity_id}/DataBindings/{binding_id}.json"] = json.dumps(binding, separators=(",", ":"))

    for relationship in profile.get("ontology", {}).get("relationships", []):
        relationship_id = _stable_int(f"{profile['domain']['id']}:relationship:{relationship['name']}")
        relationship_definition = {
            "namespace": "usertypes",
            "id": relationship_id,
            "name": relationship["name"],
            "namespaceType": "Custom",
            "source": {"entityTypeId": entity_ids[relationship["from"]]},
            "target": {"entityTypeId": entity_ids[relationship["to"]]},
        }
        context_id = _stable_uuid(f"{profile['domain']['id']}:context:{relationship['name']}")
        source_entity = entities[relationship["from"]]
        target_entity = entities[relationship["to"]]
        contextualization = {
            "id": context_id,
            "dataBindingTable": {
                "sourceType": "LakehouseTable",
                "workspaceId": workspace_id,
                "itemId": lakehouse_id,
                "sourceTableName": relationship["table"],
            },
            "sourceKeyRefBindings": [
                {
                    "sourceColumnName": relationship["fromColumn"],
                    "targetPropertyId": property_ids[(relationship["from"], source_entity["key"])],
                }
            ],
            "targetKeyRefBindings": [
                {
                    "sourceColumnName": relationship["toColumn"],
                    "targetPropertyId": property_ids[(relationship["to"], target_entity["key"])],
                }
            ],
        }
        parts[f"RelationshipTypes/{relationship_id}/definition.json"] = json.dumps(relationship_definition, separators=(",", ":"))
        parts[f"RelationshipTypes/{relationship_id}/Contextualizations/{context_id}.json"] = json.dumps(contextualization, separators=(",", ":"))
    return parts


def decode_definition_parts(payload: dict[str, Any]) -> dict[str, str]:
    return {
        part["path"]: base64.b64decode(part["payload"]).decode("utf-8")
        for part in payload["definition"]["parts"]
    }
