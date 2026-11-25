import os
import cv2
import torch

from flask import (
    Flask,
    render_template,
    request,
    Response
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

MODEL_PATH = "artifacts/model_trainer/best.pt"

model = torch.hub.load(
    "yolov5",
    "custom",
    path=MODEL_PATH,
    source="local"
)

video_path = None


@app.route("/")
def home():

    return render_template(
        "video.html"
    )


@app.route("/upload", methods=["POST"])
def upload():

    global video_path

    if "video" not in request.files:
        return "No video uploaded"

    video = request.files["video"]

    if video.filename == "":
        return "No video selected"

    video_path = os.path.join(
        UPLOAD_FOLDER,
        video.filename
    )

    video.save(video_path)

    return render_template(
        "video.html",
        start_stream=True
    )


def generate_frames():

    global video_path

    cap = cv2.VideoCapture(
        video_path
    )

    while True:

        success, frame = cap.read()

        if not success:
            break

        results = model(frame)

        annotated_frame = results.render()[0]

        _, buffer = cv2.imencode(
            ".jpg",
            annotated_frame
        )

        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes +
            b"\r\n"
        )

    cap.release()


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype=
        "multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=8081
    )