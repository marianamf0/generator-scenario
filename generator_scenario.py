import os
import json
import copy
import operator
import random
import locale
import numpy as np
from faker import Faker
from jsonschema import validate, RefResolver
from generate_schema import GenerateSchema


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_scenario(output, data_folder="debug_data", name="scenario"):
    """
    Save the output data to a local folder as a JSON file.

    Args:
        output (dict): The output data to be saved.
        data_folder (str, optional): The local directory path where the file is located. Defaults to "debug_data".
    """

    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)

    with open(
        os.path.join(data_folder, f"{name}.json"), "w", encoding="utf-8"
    ) as outfile:
        json.dump(output, outfile, indent=4)


class DistributionGenerator:
    def generate(self, parameters):
        dict_distribution = {
            "normal": self._generate_normal_distribution,
            "uniforme": self._generate_uniform_distribution,
            "exponencial": self._generate_exponential_distribution,
            "triangular": self._generate_triangular_distribution,
            "binomial": self._generate_binomial_distribution,
        }

        distribution_type = parameters.get("distribution", "uniforme")

        if distribution_type in dict_distribution.keys():
            return dict_distribution[distribution_type](parameters)
        else:
            raise ValueError(f"Distribuição desconhecida: {distribution_type}")

    def _generate_normal_distribution(self, parameters):
        mean = parameters.get("mean", 0)
        sigma = parameters.get("sigma", 1)

        return random.gauss(mean, sigma)

    def _generate_uniform_distribution(self, parameters):
        min_val = parameters.get("minimum", 0)
        max_val = parameters.get("maximum", 1)

        return random.uniform(min_val, max_val)

    def _generate_exponential_distribution(self, parameters):
        lambd = parameters.get("lambda", 1)  # Taxa lambda
        return random.expovariate(lambd)

    def _generate_triangular_distribution(self, parameters):
        min_val = parameters.get("minimum", -np.inf)
        max_val = parameters.get("maximum", np.inf)
        mode = parameters.get("mode", (min_val + max_val) / 2)

        return random.triangular(min_val, max_val, mode)

    def _generate_binomial_distribution(self, parameters):
        n = parameters.get("n", 10)  # Número de tentativas
        p = parameters.get("p", 0.5)  # Probabilidade de sucesso
        return np.random.binomial(n, p)


class EvaluateDependecies:
    def evaluate(self, properties):
        dict_dependecies = {
            "consequence": self._evaluate_consequence,
            "condicional": self._evaluate_condicional,
            "calculation": self._evaluate_calculation,
        }
        while "dependencies" in properties:

            dependecies = properties["dependencies"]

            print("dependecies", dependecies)
            type_dependencies = dependecies["type"]

            print("type_dependencies", type_dependencies)

            if type_dependencies in dict_dependecies.keys():
                properties = dict_dependecies[type_dependencies](
                    copy.deepcopy(properties)
                )
            else:
                raise ValueError(f"Tipo desconhecido: {type_dependencies}")

        return properties

    def _evaluate_consequence(self, properties):
        parameters = properties["dependencies"]["properties"]
        del properties["dependencies"]

        for key, value in parameters.items():
            if "name" in value and "path" in value:
                properties[key] = value["value"]
            else:
                properties[key] = value

        return properties

    def _evaluate_condicional(self, properties):
        condition = properties["dependencies"]["condition"]

        if self.evaluate_condition(condition):
            return condition["propertiesTrue"]
        else:
            return condition["propertiesFalse"]

    def evaluate_condition(self, condition):
        parameter = condition["parameter"]["value"]
        parameter2 = condition["parameter2"]
        operator = self.get_operator(condition["operator"])

        if isinstance(parameter2, list) and not isinstance(parameter, list):
            return any(operator(parameter, value) for value in parameter2)

        return operator(parameter, parameter2)

    def get_operator(self, operator_str: str):
        dict_operator = {
            "<=": operator.le,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "==": operator.eq,
            "!=": operator.ne,
            "in": operator.contains,
        }
        if operator_str in dict_operator.keys():
            return dict_operator[operator_str]
        else:
            raise ValueError("Operador inválido")

    def _evaluate_calculation(self, properties):
        dependecie = properties["dependencies"]

        for parameter in dependecie["parameters"]:
            self._evaluate_operation(properties, parameter)

        del properties["dependencies"]
        return properties

    def _evaluate_operation(self, properties, parameters):
        name_propertie = self.get_parameter(parameters, "propertie")
        value_paramater = self.get_parameter(parameters, "parameter")
        value_paramater2 = self.get_parameter(parameters, "parameter2")
        offset = self.get_parameter(parameters, "offset")
        operator = self.get_math_operator(parameters["operation"])

        properties[name_propertie] = (
            operator(value_paramater, value_paramater2) + offset
        )

    def get_parameter(self, obj, name):
        if isinstance(obj.get(name, 0), dict):
            return obj[name]["value"]
        return obj.get(name, 0)

    def get_math_operator(self, operator_str: str):
        dict_operator = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "//": operator.floordiv,
            "%": operator.mod,
            "**": operator.pow,
        }
        if operator_str in dict_operator.keys():
            return dict_operator[operator_str]
        else:
            raise ValueError("Operador inválido")


class ValueGenerator:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
        self.fake = Faker()
        self.distribution_generator = DistributionGenerator()

    def generate(self, parameters):
        """Determina qual tipo de valor gerar com base nos parâmetros."""

        print("parameters")
        print(parameters)

        self.parameters = parameters
        value_type = self._choosing_type(self.parameters.get("type"))

        generate_type = {
            "integer": self._generate_integer,
            "number": self._generate_number,
            "enum": self._generate_enum,
            "string": self._generate_string,
            "date": self._generate_date,
            "array": self._generate_array,
            "boolean": self._generate_bool,
        }

        if value_type == "null":
            return None

        if value_type in generate_type.keys():
            return generate_type[value_type]()
        else:
            raise ValueError(f"Tipo desconhecido: {value_type}")

    def _generate_number(self):
        minimum_value = self.parameters.get("minimum", None)
        maximum_value = self.parameters.get("maximum", None)
        value = self.distribution_generator.generate(self.parameters)

        if minimum_value:
            value = max(minimum_value, value)

        if maximum_value:
            value = min(maximum_value, value)

        return value

    def _generate_integer(self):
        """Gera um número inteiro baseado na distribuição especificada."""
        return round(self._generate_number())

    def _choosing_type(self, value_type):
        if isinstance(value_type, list):
            return random.choice(value_type)
        return value_type

    def _generate_enum(self):
        """Gera um valor aleatório a partir de uma lista de opções."""
        values = self.parameters.get("value", self.parameters.get("enum", []))
        probabilities = self.parameters.get("probabilities", [])
        if not values:
            raise ValueError("A lista de valores para 'enum' está vazia.")

        if not probabilities:
            probabilities = [1.0 / len(values)] * len(values)

        if len(values) != len(probabilities):
            raise ValueError("O número de valores e probabilidades não corresponde.")

        return random.choices(values, weights=probabilities)[0]

    def _generate_string(self):
        if "format" in self.parameters:
            format = {
                "email": self.fake.email,
                "date": self.fake.date,
            }
            return format[self.parameters["format"]]()
        elif "enum" in self.parameters:
            return self._generate_enum()

        return self.fake.word()

    def _generate_date(self):
        format = self.parameters.get("format", "YYYY-MM-DD")
        return self.fake.date(pattern=format)

    def _generate_array(self):
        array_length = self.parameters.get(
            "lengthItems", self.parameters.get("minItems", 1)
        )
        item_type = self.parameters.get("items", {})
        return [self.generate(item_type) for _ in range(array_length)]

    def _generate_bool(self):
        return random.choice([True, False])


class ScenarioGeneration:

    def __init__(self, input_data: dict, default_scenario: dict, config_scenario: dict):
        self.list_parameters = []
        self.generator = ValueGenerator()
        self.dependencies = EvaluateDependecies()
        self.config_scenario = config_scenario
        self.default_scenario = default_scenario
        self.schema = GenerateSchema(config_scenario).schema

        if input_data is not None:
            self.number_scenario = input_data.get("numScenario", 1)
            self.parameters = input_data.get("parameters", [])

        if self.default_scenario is None:
            self.default_scenario = self.generate_scenario(self.config_scenario)
            print("default_scenario")
            print(json.dumps(self.default_scenario, indent=2))
            self.validate_schema(self.default_scenario)

        self.list_parameters = []

    def generate_scenario(self, object_scenario, path=[], data={}):
        properties = object_scenario["properties"]
        required_key = object_scenario.get("required", [])
        for key in required_key:
            key_type = properties[key]["type"]
            key_properties = properties[key]

            if isinstance(key_type, list) and "object" in key_type:
                key_properties = self.replace_dependencies(key_properties, data)
                key_properties = self.dependencies.evaluate(key_properties)
                key_type = key_properties["type"]

            if key_type == "object":
                self.generate_scenario(key_properties, path + [key], data)

            elif [key, path + [key]] not in self.list_parameters:
                item = self.get_value(path + [key], data, return_value=False)
                item[key] = self.generate_parameter(key_properties, path + [key], data)

            self.list_parameters.append([key, path + [key]])

        return data

    def generate_parameter(self, parameter, path, data={}):
        properties = copy.deepcopy(parameter)
        properties = self.replace_dependencies(properties, data)
        properties = self.dependencies.evaluate(properties)

        return self.generator.generate(properties)

    def get_parameter(self, list_path):
        parameter = self.config_scenario["properties"]

        for path in list_path:
            parameter = parameter[path]
            if parameter["type"] == "object":
                parameter = parameter["properties"]

        return parameter

    def get_value(self, list_path, data, return_value: bool = True):
        if isinstance(list_path, str):
            list_path = list_path.split(".")

        item = data
        for key in list_path[:-1]:
            item = item.setdefault(key, {})

        if return_value:
            return item[list_path[-1]]
        return item

    def replace_dependencies(self, dependencies, data_values):
        if isinstance(dependencies, dict):
            name = dependencies.get("name", None)
            path = dependencies.get("path", "")
            if name and path:
                if [name, path.split(".")] not in self.list_parameters:
                    parameter = self.get_parameter(path.split("."))
                    data = self.get_value(path, data_values, return_value=False)
                    data[name] = self.generate_parameter(parameter, data_values)
                    self.list_parameters.append([name, path.split(".")])

                value = self.get_value(dependencies["path"], data_values)
                dependencies["value"] = value
            else:
                for key in dependencies:
                    dependencies[key] = self.replace_dependencies(
                        dependencies[key], data_values
                    )
            return dependencies
        elif isinstance(dependencies, list):
            data_list = []
            for item in dependencies:
                data_list.append(self.replace_dependencies(item, data_values))
            return data_list

        return dependencies

    # def make_properties(self, properties):
    #     for key, value in properties.items():
    #         if not isinstance(value, dict):
    #             continue

    #         if "parameters" in value:
    #             name = value["parameters"]["name"]
    #             path = value["parameters"]["path"]
    #             list_path = path.split(".")
    #             depedencie_parameters = self.get_parameter(name=name, path=path)

    #             if (
    #                 bool(depedencie_parameters)
    #                 and depedencie_parameters not in self.list_parameters
    #             ):
    #                 self.generate_parameter(depedencie_parameters)

    #             item = self.get_data(list_path)
    #             properties[key] = item[list_path[-1]]

    #     return properties

    def generate_data(self):
        for parameter in self.parameters:
            if parameter not in self.list_parameters:
                self.generate_parameter(parameter)

        return self.default_scenario

    # def get_data(self, list_path):
    #     # Percorre o dicionário até o penúltimo nível, criando os níveis conforme necessário
    #     item = self.default_scenario
    #     for key in list_path[:-1]:
    #         item = item.setdefault(key, {})
    #         # Se a chave não existir, cria um dicionário vazio

    #     # Define o valor na chave final
    #     return item

    def generate(self):
        scenario = 0
        while scenario < self.number_scenario:
            self.list_parameters = []
            generated_data = self.generate_data()
            print(json.dumps(generated_data, indent=2))
            if self.validate_schema(generated_data):
                scenario += 1
                save_scenario(generated_data, name=f"scenario_{scenario}")

    def validate_schema(self, generated_data):
        return not validate(instance=generated_data, schema=self.schema)


cenario_base = load_json("cenario_base.json")
input_data = load_json("input_data.json")
schema = load_json("schema.json")

# cenario_base = load_json("cenario_base_pedido.json")
# input_data = load_json("input_data.json")
schema = load_json("schema_basicinfo_gt669.json")

generate_scenario = ScenarioGeneration(
    default_scenario=None, input_data=None, config_scenario=schema
)
# generate_scenario.generate()
