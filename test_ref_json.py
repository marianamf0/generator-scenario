import json
import os
from pathlib import Path
from jsonschema import RefResolver


def get_absolute_path(path_schema) -> str:
    """
    returns absolute path of schema
    Args:
        path_schema (str): relative path of schema
    Return:
        (absolute_path): absolute path of schema
    """
    path = Path(path_schema)
    return f"{path.absolute().as_uri()}/"


# Função para carregar JSON de um arquivo
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Caminho base onde os arquivos JSON estão armazenados
base_path = "gt669"

# Nome do arquivo principal
main_file = "main.json"

# Carregar o JSON principal
main_json = load_json(os.path.join(base_path, main_file))

# Criar um Resolvedor de Referências
resolver = RefResolver(base_uri=get_absolute_path(base_path), referrer=main_json)


# Resolver referências dentro do JSON
def resolve_refs(obj):
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref_url = obj["$ref"]
            with resolver.resolving(ref_url) as resolved:
                return resolved
        else:
            return {k: resolve_refs(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_refs(item) for item in obj]
    return obj


# Resolver referências no JSON principal
resolved_json = resolve_refs(main_json)

# Exibir o JSON resultante
print(json.dumps(resolved_json, indent=4, ensure_ascii=False))
