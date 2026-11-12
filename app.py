import os
import shutil

from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS, cross_origin

from wasteDetection.pipeline.training_pipeline import TrainPipeline
from wasteDetection.utils.main_utils import (decodeImage, encodeImageIntoBase64)
from wasteDetection.constant.application import (APP_HOST, APP_PORT)

app = Flask(__name__)
CORS(app)


class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"


@app.route("/train")
def trainRoute():

    try:

        obj = TrainPipeline()
        obj.run_pipeline()

        return "Training Successful !!"

    except Exception as e:

        return str(e)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/predict", methods=["POST"])
@cross_origin()
def predictRoute():

    try:

        image = request.json["image"]

        decodeImage(image, clApp.filename)

        # remove previous prediction results
        shutil.rmtree("yolov5/runs", ignore_errors=True)

        command = (
            "cd yolov5 && "
            "python detect.py "
            "--weights ../artifacts/model_trainer/best.pt "
            "--img 416 "
            "--conf 0.25 "
            "--source ../data/inputImage.jpg"
        )

        print(f"\nRunning Command:\n{command}\n")

        status = os.system(command)

        if status != 0:

            return jsonify(
                {
                    "error": "Detection failed"
                }
            )

        output_image_path = (
            "yolov5/runs/detect/exp/inputImage.jpg"
        )

        if not os.path.exists(output_image_path):

            return jsonify(
                {
                    "error": "Prediction output image not found"
                }
            )

        opencodedbase64 = encodeImageIntoBase64(output_image_path)

        result = {
            "image": opencodedbase64.decode(
                "utf-8"
            )
        }

        return jsonify(result)

    except Exception as e:

        print(e)

        return jsonify(
            {
                "error": str(e)
            }
        )


@app.route("/live", methods=["GET"])
@cross_origin()
def predictLive():

    try:

        command = (
            "cd yolov5 && "
            "python detect.py "
            "--weights ../artifacts/model_trainer/best.pt "
            "--img 416 "
            "--conf 0.25 "
            "--source 0"
        )

        print(command)

        os.system(command)

        return "Camera Started !!"

    except Exception as e:

        print(e)

        return str(e)


if __name__ == "__main__":

    clApp = ClientApp()

    app.run(
        host=APP_HOST,
        port=APP_PORT,
        debug=True
    )