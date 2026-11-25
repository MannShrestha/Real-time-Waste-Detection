import os
import time
import cv2
import torch

from collections import defaultdict

from flask import (
    Flask,
    render_template,
    request,
    Response,
    jsonify
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

MODEL_PATH = (
    "artifacts/model_trainer/best.pt"
)

model = torch.hub.load(
    "yolov5",
    "custom",
    path=MODEL_PATH,
    source="local"
)

video_path = None


dashboard_metrics = {
    "fps": 0,
    "objects": 0,
    "classes": 0,
    "inference_time": 0,
    "progress": 0
}


class_counter = defaultdict(int)


@app.route("/")
def home():

    return render_template(
        "video_dashboard.html"
    )


@app.route("/upload", methods=["POST"])
def upload():

    global video_path

    if "video" not in request.files:
        return "No Video Uploaded"

    video = request.files["video"]

    if video.filename == "":
        return "No Video Selected"

    video_path = os.path.join(
        UPLOAD_FOLDER,
        video.filename
    )

    video.save(video_path)

    return render_template(
        "video_dashboard.html",
        start_stream=True
    )


def generate_frames():

    global dashboard_metrics

    cap = cv2.VideoCapture(
        video_path
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    current_frame = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        current_frame += 1

        start_time = time.time()

        results = model(frame)

        inference_time = (
            time.time() - start_time
        ) * 1000

        annotated_frame = (
            results.render()[0]
        )

        names = (
            results.pandas()
            .xyxy[0]["name"]
            .tolist()
        )

        object_count = len(names)

        unique_classes = len(
            set(names)
        )

        for item in names:

            class_counter[item] += 1

        fps = (
            1000 / inference_time
            if inference_time > 0
            else 0
        )

        progress = int(
            (
                current_frame
                / total_frames
            ) * 100
        )

        dashboard_metrics = {
            "fps": round(fps, 1),
            "objects": object_count,
            "classes": unique_classes,
            "inference_time": round(
                inference_time,
                1
            ),
            "progress": progress
        }

        _, buffer = cv2.imencode(
            ".jpg",
            annotated_frame
        )

        frame_bytes = (
            buffer.tobytes()
        )

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

    cap.release()


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype=
        "multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/metrics")
def metrics():

    response = {

        "fps":
        dashboard_metrics["fps"],

        "objects":
        dashboard_metrics["objects"],

        "classes":
        dashboard_metrics["classes"],

        "inference_time":
        dashboard_metrics[
            "inference_time"
        ],

        "progress":
        dashboard_metrics[
            "progress"
        ]
    }

    response.update(
        class_counter
    )

    return jsonify(
        response
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8082,
        debug=True
    )