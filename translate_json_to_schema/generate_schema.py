import json


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


class GenerateSchema:

    def __init__(self, data):
        self.data = data
        self.data_json_schema = {}

    def generate(self):
        """Determina qual tipo de valor gerar com base nos parâmetros."""

        value_type = self.data.get("type")

        print("value_type", value_type)

        generate_type = {
            "integer": self._generate_integer,
            "float": self._generate_float,
            "enum": self._generate_enum,
            "string": self._generate_string,
            "date": self._generate_date,
            "array": self._generate_array,
            "bool": self._generate_bool,
            "object": self._generate_object,
        }

        if value_type in generate_type.keys():
            return generate_type[value_type]()
        else:
            raise ValueError(f"Tipo desconhecido: {value_type}")

    def _generate_object(self):
        data = {"type": "object"}

    def _generate_integer(self, parameters):
        data = self._generate_number(parameters, type=int)
        data["type"] = "integer"
        return data

    def _generate_number(self, parameters, type=float):
        data = {"type": "number"}
        properties = {
            "minimum": {"name": "minimum", "type": (type)},
            "maximum": {"name": "minimum", "type": (type)},
            "exclusiveMinimum": {"name": "exclusiveMinimum", "type": (type)},
            "exclusiveMaximum": {"name": "exclusiveMaximum", "type": (type)},
            "multipleOf": {"name": "multipleOf", "type": (type)},
        }

        for key, value in properties.items():
            for name in value["name"]:
                if name in parameters:
                    if isinstance(parameters["name"], value["type"]):
                        data[key] = parameters[name]
                    # elif isinstance(parameters["name"], dict) and

        return data

    def _generate_string(self, parameters):

        properties = {
            "minLength": {"name": ["minLength"]},
            "maxLength": {"name": ["maxLength"]},
            "pattern": {"name": ["pattern"]},
            "format": {
                "name": ["format"],
                "values": [
                    "email",
                    "date",
                    "date-time",
                    "uri",
                    "hostname",
                    "ipv4",
                    "ipv6",
                ],
            },
            "const": {"name": ["const", "default"]},
            "enum": {"name": ["enum"]},
        }

        data = {"type": "string"}

        for key, value in properties.items():
            for name in value["name"]:
                if name in parameters:
                    data[key] = parameters[name]

        return data
