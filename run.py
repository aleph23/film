import os
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

def predict(frame1, frame2, times_to_interpolate, block_height, block_width):
    print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    interpolator = interpolator_lib.Interpolator("/pretrained_models/film_net/Style/saved_model", None, [block_height, block_width])

    # Batched time.
    batch_dt = np.full(shape=(1,), fill_value=0.5, dtype=np.float32)

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
    out_path = Path(tempfile.mkdtemp()) / "out.mp4"
    mediapy.write_video(str(out_path), frames, fps=30)

    return out_path

predict ('/nft/video/frame_0000.jpg', '/nft/video/frame_0001.jpg', 3, 2, 2)