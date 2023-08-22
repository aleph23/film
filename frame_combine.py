import os
import sys
import cv2

PART = sys.argv[1]; assert len(PART) == 4, "Invalid arg"
_PATH = sys.argv[2]; assert len(_PATH) > 0, "Invalid path"
PATH = f'{_PATH}/{PART}/frames'

def get_images():
    files = os.listdir(PATH)
    files.sort()
    return [
        os.path.join(PATH, img) for img in files if img.endswith(".png")
    ]

def save_video(_image_files):
    frame = cv2.imread(_image_files[0])
    height, width, layers = frame.shape
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(f'{PATH}/{PART}.mp4', fourcc, fps, (width, height))
    for image in _image_files:
        video.write(cv2.imread(os.path.join(PATH, image)))
    cv2.destroyAllWindows()
    video.release()

image_files = get_images()
save_video(image_files)
