import os
import sys
import yaml
import base64

from wasteDetection.exception import AppException
from wasteDetection.logger import logging


def read_yaml_file(file_path: str) -> dict:
    """
    Read YAML file and return dictionary.
    """

    try:

        with open(file_path, "r") as yaml_file:

            logging.info(f"Reading YAML file: {file_path}")

            content = yaml.safe_load(yaml_file)

            return content

    except Exception as e:

        logging.error(str(e))

        raise AppException(e, sys) from e


def write_yaml_file(file_path: str,content: object,replace: bool = False) -> None:
    """
    Write content into YAML file.
    """

    try:

        if replace:

            if os.path.exists(file_path):
                os.remove(file_path)

        dir_path = os.path.dirname(file_path)

        if dir_path != "":
            os.makedirs(dir_path,exist_ok=True)

        with open(file_path, "w") as file:

            yaml.dump(content, file, default_flow_style=False)

        logging.info(f"YAML file written successfully: {file_path}")

    except Exception as e:

        logging.error(str(e))

        raise AppException(e, sys) from e


def decodeImage(imgstring: str,fileName: str) -> None:
    """
    Decode Base64 image and save to data folder.
    """

    try:

        os.makedirs("./data",exist_ok=True)

        imgdata = base64.b64decode(imgstring)

        file_path = os.path.join("./data", fileName)

        with open(file_path,"wb") as file:

            file.write(imgdata)

        logging.info(f"Image saved at: {file_path}")

    except Exception as e:

        logging.error(str(e))

        raise AppException(e, sys) from e


def encodeImageIntoBase64(croppedImagePath: str):
    """
    Convert image into Base64 format.
    """

    try:

        with open(croppedImagePath, "rb") as file:

            encoded_string = (base64.b64encode(file.read()))

        logging.info(f"Image encoded successfully: {croppedImagePath}")

        return encoded_string

    except Exception as e:

        logging.error(str(e))

        raise AppException(e, sys) from e