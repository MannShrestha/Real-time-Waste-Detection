import os
import sys
import yaml
import zipfile
import shutil
from glob import glob

from wasteDetection.utils.main_utils import read_yaml_file
from wasteDetection.logger import logging
from wasteDetection.exception import AppException

from wasteDetection.entity.config_entity import (
    ModelTrainerConfig
)

from wasteDetection.entity.artifacts_entity import (
    ModelTrainerArtifact
)


class ModelTrainer:

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
    ):
        try:
            self.model_trainer_config = model_trainer_config

        except Exception as e:
            raise AppException(e, sys)

    def initiate_model_trainer(
        self
    ) -> ModelTrainerArtifact:

        logging.info(
            "Entered initiate_model_trainer method"
        )

        try:

            # ====================================
            # Extract Dataset
            # ====================================

            if os.path.exists("data.zip"):

                logging.info(
                    "Extracting data.zip"
                )

                with zipfile.ZipFile(
                    "data.zip",
                    "r"
                ) as zip_ref:

                    zip_ref.extractall(".")

                os.remove("data.zip")

                logging.info(
                    "Data extracted successfully"
                )

            else:

                logging.warning(
                    "data.zip not found. Assuming data is already extracted."
                )

            # ====================================
            # Read data.yaml
            # ====================================

            if not os.path.exists(
                "data.yaml"
            ):

                raise FileNotFoundError(
                    "data.yaml not found"
                )

            with open(
                "data.yaml",
                "r"
            ) as stream:

                data_yaml = yaml.safe_load(
                    stream
                )

                num_classes = data_yaml["nc"]

            logging.info(
                f"Number of classes: {num_classes}"
            )

            # ====================================
            # Create Custom YOLO Config
            # ====================================

            model_config_file_name = (
                self.model_trainer_config
                .weight_name
                .split(".")[0]
            )

            config = read_yaml_file(
                f"yolov5/models/"
                f"{model_config_file_name}.yaml"
            )

            config["nc"] = num_classes

            custom_config_path = (
                f"yolov5/models/"
                f"custom_{model_config_file_name}.yaml"
            )

            with open(
                custom_config_path,
                "w"
            ) as file:

                yaml.dump(
                    config,
                    file
                )

            logging.info(
                f"Custom config created at "
                f"{custom_config_path}"
            )

            # ====================================
            # Training
            # ====================================

            training_command = (
                f"python yolov5/train.py "
                f"--img 416 "
                f"--batch {self.model_trainer_config.batch_size} "
                f"--workers 0 "
                f"--epochs {self.model_trainer_config.no_epochs} "
                f"--data data.yaml "
                f"--cfg {custom_config_path} "
                f"--weights yolov5/{self.model_trainer_config.weight_name} "
                f"--name yolov5s_results "
                f"--exist-ok"
            )

            logging.info(
                f"Training Command : {training_command}"
            )

            status = os.system(
                training_command
            )

            if status != 0:

                raise Exception(
                    "YOLOv5 training failed."
                )

            # ====================================
            # Locate best.pt
            # ====================================

            train_runs = glob(
                "yolov5/runs/train/*"
            )

            latest_run = max(
                train_runs,
                key=os.path.getmtime
            )

            best_weights_path = os.path.join(
                latest_run,
                "weights",
                "best.pt"
            )

            logging.info(
                f"Latest run : {latest_run}"
            )

            logging.info(
                f"best.pt path : {best_weights_path}"
            )

            if not os.path.exists(
                best_weights_path
            ):

                raise FileNotFoundError(
                    f"best.pt not found at "
                    f"{best_weights_path}"
                )

            # ====================================
            # Save Model
            # ====================================

            os.makedirs(
                self.model_trainer_config.model_trainer_dir,
                exist_ok=True
            )

            final_model_path = os.path.join(
                self.model_trainer_config.model_trainer_dir,
                "best.pt"
            )

            shutil.copy(
                best_weights_path,
                final_model_path
            )

            shutil.copy(
                best_weights_path,
                "yolov5/best.pt"
            )

            logging.info(
                f"Model copied to: "
                f"{final_model_path}"
            )

            # ====================================
            # Create Artifact
            # ====================================

            model_trainer_artifact = (
                ModelTrainerArtifact(
                    trained_model_file_path=
                    final_model_path
                )
            )

            logging.info(
                f"Model Trainer Artifact : "
                f"{model_trainer_artifact}"
            )

            # ====================================
            # Cleanup
            # ====================================

            logging.info(
                "Cleaning temporary files..."
            )

            shutil.rmtree(
                "train",
                ignore_errors=True
            )

            shutil.rmtree(
                "valid",
                ignore_errors=True
            )

            if os.path.exists(
                "data.yaml"
            ):
                os.remove(
                    "data.yaml"
                )

            if os.path.exists(
                custom_config_path
            ):
                os.remove(
                    custom_config_path
                )

            logging.info(
                "Cleanup completed"
            )

            logging.info(
                "Exited initiate_model_trainer method"
            )

            return (
                model_trainer_artifact
            )

        except Exception as e:

            raise AppException(
                e,
                sys
            )