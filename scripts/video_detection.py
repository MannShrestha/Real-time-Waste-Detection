import os
import shutil
import time


class VideoDetection:

    def __init__(
        self,
        model_path="artifacts/model_trainer/best.pt",
        image_size=416,
        confidence=0.25
    ):
        self.model_path = model_path
        self.image_size = image_size
        self.confidence = confidence

    def detect(self, video_path):

        if not os.path.exists(video_path):
            raise FileNotFoundError(
                f"Video not found: {video_path}"
            )

        detect_dir = "yolov5/runs/detect"

        os.makedirs(
            detect_dir,
            exist_ok=True
        )

        command = (
            f'cd yolov5 && '
            f'python detect.py '
            f'--weights ../{self.model_path} '
            f'--img {self.image_size} '
            f'--conf {self.confidence} '
            f'--source ../{video_path} '
            f'--exist-ok'
        )

        print("\nRunning YOLOv5 Detection...\n")
        print(command)

        status = os.system(command)

        if status != 0:
            raise RuntimeError(
                "YOLOv5 video detection failed"
            )

        time.sleep(2)

        folders = [
            os.path.join(detect_dir, folder)
            for folder in os.listdir(detect_dir)
            if os.path.isdir(
                os.path.join(
                    detect_dir,
                    folder
                )
            )
        ]

        if not folders:
            raise FileNotFoundError(
                "No detect output folder created."
            )

        latest_folder = max(
            folders,
            key=os.path.getmtime
        )

        output_video = os.path.join(
            latest_folder,
            os.path.basename(video_path)
        )

        if not os.path.exists(output_video):

            files = [
                os.path.join(
                    latest_folder,
                    file
                )
                for file in os.listdir(
                    latest_folder
                )
                if file.endswith(
                    (
                        ".mp4",
                        ".avi",
                        ".mov",
                        ".mkv",
                    )
                )
            ]

            if not files:
                raise FileNotFoundError(
                    "Detected video not found."
                )

            output_video = files[0]

        return output_video