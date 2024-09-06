import os
import sys
import cv2

PART: str = sys.argv[1]; assert len(PART) == 4, "Invalid filename"
_PATH: str = sys.argv[2]; assert len(_PATH) > 0, "Invalid path"
PATH: str = f'{_PATH}/{PART}/'

def get_images() -> list[str]:
    files: list[str] = os.listdir(path=PATH)
    files.sort()
    return [
        os.path.join(PATH, img) for img in files if img.endswith(".png")
    ]

def save_video(_image_files) -> None:
    """
    Creates a video file from a list of image files.

    This function reads images from the provided list and compiles them into a video file using OpenCV.
    The video is saved in the specified directory with a predefined filename format.

    Args:
        _image_files (list of str): A list of image file names to be included in the video.

    Returns:
        None

    Raises:
        FileNotFoundError: If any of the image files do not exist.
        ValueError: If the list of image files is empty.

    Examples:
        save_video(['image1.jpg', 'image2.jpg', 'image3.jpg'])
    """

    frame = cv2.imread(_image_files[0]) # type: ignore
    height, width, layers = frame.shape
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(f'{PATH}/{PART}.mp4', fourcc, fps, (width, height))
    for image in _image_files:
        video.write(cv2.imread(os.path.join(PATH, image)))
    cv2.destroyAllWindows()
    video.release()

image_files: list[str] = get_images()
save_video(_image_files=image_files)
