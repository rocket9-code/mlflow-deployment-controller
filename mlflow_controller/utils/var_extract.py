import ast
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler("log.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def var_parser(placeholder):
    model_pattern = r"\[.*\]"
    model = re.search(model_pattern, placeholder)
    logger.info(placeholder)
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
