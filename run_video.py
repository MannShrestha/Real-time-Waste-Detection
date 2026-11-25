from scripts.video_detection import VideoDetection

def main():

    video_path = "videos/waste.mp4"

    detector = VideoDetection()

    output_video = detector.detect_video(video_path)

    print(output_video)

if __name__ == "__main__":
    main()