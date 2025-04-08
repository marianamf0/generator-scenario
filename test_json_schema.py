from jsonschema import validate

json_schema = {
    "type": "object",
    "properties": {
        "generalData": {"type": "object"},
        "basicInfo": {"type": "object"},
        "pldBounds": {"type": "boolean"},
        "filterBusiness": {"type": "string"},
        "cemigUte": {"type": "boolean"},
        "secondaryEnergy": {"type": "boolean"},
    },
    "required": ["filterBusiness", "cemigUte", "secondaryEnergy"],
    "allOf": [
        {
            "if": {
                "properties": {"filterBusiness": {"const": "Comercializadora"}},
                "required": ["filterBusiness"],
            },
            "then": {
                "properties": {"cemigUte": {"const": False}},
                "required": ["cemigUte"],
            },
        },
        {
            "if": {
                "properties": {"filterBusiness": {"const": "Comercializadora"}},
                "required": ["filterBusiness"],
            },
            "then": {
                "properties": {"secondaryEnergy": {"const": False}},
                "required": ["secondaryEnergy"],
            },
        },
    ],
}


data = {
    "filterBusiness": "Comercializadora",
    "secondaryEnergy": True,
}


validate(instance=data, schema=json_schema)
