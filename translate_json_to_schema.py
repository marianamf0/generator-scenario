import json

def convert_to_json_schema(data):
    # Função recursiva para converter o JSON para o formato de JSON Schema
    def convert_properties(properties):
        schema = {}
        for key, value in properties.items():
            if isinstance(value, dict):
                if 'type' in value and value['type'] == 'object':
                    value['properties'] = convert_properties(value.get('properties', {}))
                elif 'type' in value and value['type'] == 'array':
                    value['items'] = convert_properties(value.get('items', {}))
                schema[key] = value
            elif isinstance(value, list):
                schema[key] = value
            else:
                schema[key] = value
        return schema

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": convert_properties(data["properties"]),
        "required": data["required"],
    }

    # Adicionando dependências, caso existam
    if "dependencies" in data:
        schema["dependencies"] = data["dependencies"]

    return schema


# JSON de entrada
data = {
    "type": "object",
    "properties": {
        "startYear": {
            "type": "integer",
            "minimum": 2000,
            "maximum": 2029
        },
        "endYear": {
            "type": "integer",
            "minimum": { "parameters": { "name": "startYear", "path": "startYear" }, "default": 2000 },
            "maximum": 2029
        },
        "age": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "status": {
            "type": "string",
            "enum": ["active", "inactive"]
        },
        "start_date": {
            "path": "start_date",
            "condition": [{
                "parameter1": { "name": "startYear", "path": "startYear" },
                "operator": "=",
                "parameter2": "active",
                "valueTrue": { "type": "string", "format": "date" },
                "valueFalse": None
            }]
        },
        "data": {
            "type": "array",
            "path": "data",
            "items": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100
            },
            "minItems": 3,
            "maxItems": 3
        },
        "data_2": {
            "type": "array",
            "path": "data_2",
            "lengthItems": 3,
            "items": {
                "type": "array",
                "lengthItems": 4,
                "items": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                }
            }
        },
        "product": {
            "type": "array",
            "path": "product",
            "lengthItems": 3,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100
                    },
                    "name": {
                        "type": "string"
                    }
                },
                "required": ["id", "name"]
            }
        }
    },
    "required": ["age", "email", "status", "data", "product", "startYear", "endYear", "start_date"],
    "dependencies": {
        "start_date": ["status"]
    }
}

# Gerando o JSON Schema
json_schema = convert_to_json_schema(data)

# Imprimindo o resultado
print(json.dumps(json_schema, indent=2))
