import os
import json
import warnings
import pathlib
from ruamel.yaml import YAML
from jsonschema import Draft7Validator
from schema_merge.schema_merger import DeepmergeStrategy

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../schema/general_schema.json")
EXTENSION_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../schema/extension_schema.json")

MERGED_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../schema/merged_schema.json")


ryaml = YAML(typ='safe')

validator = None
with open(SCHEMA_PATH, "r") as fs:
    try:
        base_schema = json.load(fs)
    except Exception as e:
        raise Exception("JSON schema read failed:" + SCHEMA_PATH + " " + str(e))

with open(EXTENSION_SCHEMA_PATH, "r") as fs:
    try:
        extension_schema = json.load(fs)
    except Exception as e:
        raise Exception("JSON schema read failed:" + EXTENSION_SCHEMA_PATH + " " + str(e))

merge_strategy = DeepmergeStrategy()
merged_schema = merge_strategy.merge(base_schema, extension_schema, True, MERGED_SCHEMA_PATH)
validator = Draft7Validator(merged_schema)


def validate(json_object: object) -> bool:
    """
    Validates the given json configuration object using the cell type annotation schema.

    Returns:
    :param json_object: configuration object
    :return: True if object is valid, False otherwise.
    """
    is_valid = True

    if not validator.is_valid(json_object):
        es = validator.iter_errors(json_object)
        for e in es:
            warnings.warn(str(e.message))
            is_valid = False

    return is_valid


def load_json_data(file_path: str) -> dict:
    """
    Reads the json data object from the given path.
    :param file_path: path to the json file
    :return: data object (List of data column config items)
    """
    with open(file_path, "r") as fs:
        try:
            return json.load(fs)
        except Exception as e:
            raise Exception("JSON read failed:" + file_path + " " + str(e))


def load_yaml_data(file_path: str) -> dict:
    """
    Reads the data object from the given path.
    :param file_path: path to the yaml file
    :return: data object (List of data column config items)
    """
    with open(file_path, "r") as fs:
        try:
            return ryaml.load(fs)
        except Exception as e:
            raise Exception("Yaml read failed:" + file_path + " " + str(e))


def load_data(file_path: str) -> dict:
    """
    Reads the data object from the given path.
    :param file_path: path to the data file
    :return: data object (List of data column config items)
    """
    file_extension = pathlib.Path(file_path).suffix
    if file_extension == ".json":
        return load_json_data(file_path)
    elif file_extension == ".yaml" or file_extension == ".yml":
        return load_yaml_data(file_path)
    else:
        raise Exception("Given data file extension is not supported. "
                        "Try a json or yaml file instead of :" + file_path)


def validate_file(file_path: str) -> bool:
    """
    Read the configuration object from the given path and validates it.
    :param file_path: path to the json file
    :return: True if object is valid, False otherwise.
    """
    return validate(load_data(file_path))


def validate_json_str(json_str: str) -> bool:
    """
    Validates the given json string.

    Returns:
    :param json_str: string representation of a json object
    :return: True if object is valid, False otherwise.
    """
    return validate(json.loads(json_str))
