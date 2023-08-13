import os
import cv2

PART = "L1S1"
PATH = f'~/Movies/{PART}/frames'

def get_images():
    files = os.listdir(PATH)
    files.sort()
    return [
        os.path.join(PATH, img) for img in files if img.endswith(".png")
    ]

def save_video(_image_files):
    frame = cv2.imread(os.path.join(PATH, _image_files[0]))
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
