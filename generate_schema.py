import json


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


class GenerateSchema:
    def __init__(self, object_scenario):
        self.schema = self.generate(object_scenario)

        print(json.dumps(self.schema, indent=4))

    def generate(self, data):
        """Determina qual tipo de valor gerar com base nos parâmetros."""

        value_type = data.get("type")

        generate_type = {
            "integer": self._generate_integer,
            "number": self._generate_number,
            # "enum": self._generate_enum,
            # "string": self._generate_string,
            # "date": self._generate_date,
            "array": self._generate_array,
            "boolean": self._generate_bool,
            "object": self._generate_object,
        }

        if isinstance(value_type, list):
            return {"type": value_type}

        if value_type in generate_type.keys():
            return generate_type[value_type](data)
        else:
            raise ValueError(f"Tipo desconhecido: {value_type}")

    def _generate_object(self, data):
        data_properties = {}
        properties = data["properties"]
        for key in properties.keys():
            if key != "dependencies":
                data_properties[key] = self.generate(properties[key])

        return {
            "type": "object",
            "properties": data_properties,
            "required": data.get("required", []),
        }

    def _generate_integer(self, data):
        data_properties = self._generate_number(data, type=int)
        data_properties["type"] = "integer"

        return data_properties

    def _generate_number(self, data, type=float):
        data_properties = {"type": "number"}
        properties = [
            "minimum",
            "maximum",
            "exclusiveMinimum",
            "exclusiveMaximum",
            "multipleOf",
        ]

        for key, value in data.items():
            if key in properties and isinstance(key, type):
                data_properties[key] = value

        return data_properties

    def _generate_bool(self, data):
        return {"type": "boolean", "enum": data.get("enum", [True, False])}

    def _generate_array(self, data):
        data_properties = {"type": "array"}
        properties = [
            "maxItems",
            "minItems",
            "uniqueItems",
            "maxContains",
            "minContains",
        ]

        for key, value in data.items():
            if key in properties:
                data[key] = value

        if "lengthItems" in data:
            data_properties["minItems"] = data["lengthItems"]
            data_properties["maxItems"] = data["lengthItems"]

        return data_properties

    def add_conditional_dependency(
        self, property_name, condition_param, condition_value, true_schema, false_schema
    ):
        self.schema["properties"].setdefault(property_name, {})
        self.schema["properties"][property_name]["allOf"] = [
            {
                "if": {"properties": {condition_param: {"const": condition_value}}},
                "then": true_schema,
                "else": false_schema,
            }
        ]


schema = load_json("schema_basicinfo_gt669.json")
GenerateSchema(schema)
