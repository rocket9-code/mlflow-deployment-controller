import ast
import re


def var_parser(placeholder):
    model_pattern = r"\[.*\]"
    model = re.search(model_pattern, placeholder)
    model_name = ast.literal_eval(model.group())[0]
    vendor_pattern = r"\..*\["
    vendor = re.search(vendor_pattern, placeholder)
    vendor_name = vendor.group().replace(".", "").replace("[", "")
    registry_pattern = r"^[a-zA-Z0-9_]*"
    registry = re.search(registry_pattern, placeholder)
    registry_name = registry.group()
    return model_name, vendor_name, registry_name


def validate_variable(placeholder):
    pattern = re.compile(r"\w+\.\w+\[\".+\"\]", re.IGNORECASE)
    return pattern.match(placeholder)
