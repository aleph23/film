import os
import glob
from pathlib import Path
import numpy as np
import tempfile
import tensorflow as tf
import mediapy
from PIL import Image
from eval import interpolator as interpolator_lib
from eval import util

_UINT8_MAX_F = float(np.iinfo(np.uint8).max)
INPUT_EXT = ['.png', '.jpg', '.jpeg']
INTERMEDIATE = f'/intermediate'

def clear_path(path: str):
    mp4_files = glob.glob(os.path.join(path, "*.mp4"))
    for file in mp4_files:
        os.remove(file)

def get_images(path: str) -> list:
    INPUT_EXT = ['.png', '.jpg', '.jpeg']
    all_files = os.listdir(path)
    image_files = [os.path.join(path, file) for file in all_files if os.path.splitext(file)[1].lower() in INPUT_EXT]

    return image_files

def predict_one(frame1, frame2, video_file, fps, times_to_interpolate, block_height, block_width):
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    interpolator = interpolator_lib.Interpolator("/pretrained_models/film_net/Style/saved_model", None, [block_height, block_width])

    assert os.path.splitext(str(frame1))[-1] in INPUT_EXT and os.path.splitext(str(frame2))[-1] in INPUT_EXT, "Please provide png, jpg or jpeg images."

    # make sure 2 images are the same size
    img1 = Image.open(str(frame1))
    img2 = Image.open(str(frame2))

    assert img1.size == img2.size, "Images must be same size"
 
    input_frames = [str(frame1), str(frame2)]

    frames = list(util.interpolate_recursively_from_files(input_frames, times_to_interpolate, interpolator))
    print('Interpolated frames generated, saving now as output video.')

    ffmpeg_path = util.get_ffmpeg_path()
    mediapy.set_ffmpeg(ffmpeg_path)
    mediapy.write_video(video_file, frames, fps=fps)


clear_path(INTERMEDIATE)

input_files = get_images('/nft/video/')
frame_sets = list(zip(input_files[:-1], input_files[1:]))

for index, (frame1, frame2) in enumerate(frame_sets):
    predict_one (frame1, frame2, f'{INTERMEDIATE}/out_{index}.mp4',30, 3, 2, 2)