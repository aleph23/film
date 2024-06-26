r"""A script for an interpolated fade between a stream and a single image.

Usage example:
 python3 -m frame_interpolation.eval.interpolator_test \
   --folder_in '<folderpath of the fade from images>' \
   --image_file '<image to fade to>' \
   --folder_out '<folderpath for mixed images>' \
   --fade_count <number of fade levels over the length of folder_in>
   --model_path <The filepath of the TF2 saved model to use>
"""
import os
from os import path, listdir
from typing import Sequence

from . import interpolator as interpolator_lib
from . import util
from absl import app
from absl import flags
import numpy as np
import mediapy as media

# Controls TF_CCP log level.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


_FOLDER_IN = flags.DEFINE_string(
    name='folder_in',
    default=None,
    help='The folder with source stream images.',
    required=True)
_IMAGE_FILE = flags.DEFINE_string(
    name='image_file', 
    default=None,
    help='The fixed image to fade to.',
    required=True)
_FOLDER_OUT = flags.DEFINE_string(
    name='folder_out',
    default=None,
    help='The folder for frame outputs.',
    required=True)
_FADE_COUNT = flags.DEFINE_integer(
    name='fade_count',
    default=None,
    help='Number of discrete fades over the stream length.',
    required=True)
_IMG_IDX = flags.DEFINE_integer(
    name='img_idx',
    default=0,
    help='First title index for output frame.')
_MODEL_PATH = flags.DEFINE_string(
    name='model_path',
    default=None,
    help='The path of the TF2 saved model to use.')
_ALIGN = flags.DEFINE_integer(
    name='align',
    default=64,
    help='If >1, pad the input size so it is evenly divisible by this value.')
_BLOCK_HEIGHT = flags.DEFINE_integer(
    name='block_height',
    default=1,
    help='An int >= 1, number of patches along height, '
    'patch_height = height//block_height, should be evenly divisible.')
_BLOCK_WIDTH = flags.DEFINE_integer(
    name='block_width',
    default=1,
    help='An int >= 1, number of patches along width, '
    'patch_width = width//block_width, should be evenly divisible.')
_OUTPUT_VIDEO = flags.DEFINE_boolean(
    name='output_video',
    default=False,
    help='If true, creates a video of the frames in the folder_out')

def _run_interpolator() -> None:
  """Writes interpolated frames from a given folder."""

  interpolator = interpolator_lib.Interpolator(
      model_path=_MODEL_PATH.value,
      align=_ALIGN.value,
      block_shape=[_BLOCK_HEIGHT.value, _BLOCK_WIDTH.value])
  
  # Batched time.
  batch_dt = np.full(shape=(1,), fill_value=0.5, dtype=np.float32)
  
  if not path.isdir(_FOLDER_OUT.value):
    os.mkdir(_FOLDER_OUT.value)
  if _OUTPUT_VIDEO.value:
    ffmpeg_path = util.get_ffmpeg_path()
    media.set_ffmpeg(ffmpeg_path)

  image_path_list = [f for f in listdir(_FOLDER_IN.value) if path.isfile(path.join(_FOLDER_IN.value, f))]
  image_path_list.sort()

  n_files = len(image_path_list)
  mult = float(_FADE_COUNT.value - 2)/float(n_files - 1)
  offset = 1

  # Everythong in here is reversed
  img_idx = _IMG_IDX.value + n_files - 1

  frames = list()
  if _OUTPUT_VIDEO.value:
    photo1_path = path.join(_FOLDER_IN.value, image_path_list[0])
    image_1 = util.read_image(photo1_path)
    frames.append(image_1)

  print("fixed image:", _IMAGE_FILE.value)
  image_2 = util.read_image(_IMAGE_FILE.value)
  image_batch_2 = np.expand_dims(image_2, axis=0)
   
  idx = 0
  while idx < n_files:
    print(idx+1,"/",n_files)
    
    photo1_path = path.join(_FOLDER_IN.value, image_path_list[n_files - 1 - idx]) 
    image_1 = util.read_image(photo1_path)
    image_batch_1 = np.expand_dims(image_1, axis=0)

    top_idx = _FADE_COUNT.value
    bot_idx = 0
    target_fade_idx = int(offset + mult * float(idx))

    current_fade_idx = _FADE_COUNT.value/2
    while(True):
      # Invoke the model for one mid-frame interpolation.
      mid_frame = interpolator(image_batch_1, image_batch_2, batch_dt)[0]
      current_fade_idx = int((top_idx+bot_idx)/2);
      #print(top_idx, target_fade_idx, bot_idx)
      if current_fade_idx == target_fade_idx:
        #print("C", current_fade_idx,", T", target_fade_idx)
        break
      if target_fade_idx < current_fade_idx:
        image_1 = mid_frame
        image_batch_1 = np.expand_dims(image_1, axis=0)
        top_idx = current_fade_idx
      elif target_fade_idx > current_fade_idx:
        image_2 = mid_frame
        image_batch_2 = np.expand_dims(image_2, axis=0)
        bot_idx = current_fade_idx

    mid_frame_filepath = path.join(_FOLDER_OUT.value,"img"+f"{img_idx:05d}"+".png")
    util.write_image(mid_frame_filepath, mid_frame)
    idx+=1
    img_idx-=1
    if _OUTPUT_VIDEO.value:
      frames.append(mid_frame)
   
  if _OUTPUT_VIDEO.value:
    image_2 = util.read_image(_IMAGE_FILE.value)
    frames.append(image_2)
    media.write_video(f'{_FOLDER_OUT.value}/interpolated.mp4', frames, fps=30)
    print(f'Output video saved at {_FOLDER_OUT.value}/interpolated.mp4.')
  

def main(argv: Sequence[str]) -> None:
  #print(len(argv), "arguments")
  #for i in range(len(argv)):
  #  print(i, argv[i])
   
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments. Try quoting path names.')
    
  _run_interpolator()

if __name__ == '__main__':
  app.run(main)
