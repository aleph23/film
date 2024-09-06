import json
import os
import shutil
import sys

"""
This module processes image frames to generate interpolated frames based on configuration settings.

It loads a configuration from a JSON file and iterates through specified frame ranges to create new frames using interpolation techniques. The module includes functions for loading configurations, creating frames, and managing temporary files.

Functions:
- load_config: Loads configuration settings from a JSON file.
- _create_frame: Generates a single interpolated frame between two specified frames.
- get_tmp_frames: Retrieves and sorts temporary frame files from a specified directory.
- _create_frames: Creates multiple interpolated frames between two specified frames.

Examples:
    config = load_config()
    for instruction in config:
        start = instruction["start"]
        end = instruction["end"]
        step = instruction["step"]
        # Process frames based on the loaded configuration.
"""

PART = sys.argv[1]; assert len(PART) == 4, "Invalid arg"
_PATH = sys.argv[2]; assert len(_PATH) > 0, "Invalid path"
PATH = f'{_PATH}/{PART}/frames'
MODEL = "pretrained_models/film_net/Style/saved_model"

def load_config():
    with open("config.json") as f:
        load_config = json.load(f)
        print(load_config)
        return load_config

def _create_frame(
    _start_index,
    _end_index,
    _name
):
    """
    Generates a single interpolated frame between two specified frames and saves it to a designated path.
    This function executes an external command to create the interpolated frame using the provided frame indices and output name.

    Args:
        _start_index (str): The index of the starting frame.
        _end_index (str): The index of the ending frame.
        _name (str): The name for the output interpolated frame.

    Raises:
        AssertionError: If the interpolation command returns a non-zero exit code.

    Examples:
        _create_frame('frame_0001.png', 'frame_0005.png', 'interpolated_frame')
    """

    exit_code = os.system(
        f'python -m eval.interpolator_test '
        f'--frame1 {PATH}/{PART}{_start_index[:-5]}.png '
        f'--frame2 {PATH}/{PART}{_end_index[:-5]}.png '
        f'--model_path {MODEL} '
        f'--output_frame {PATH}/{PART}{_name}.png'
    )
    assert exit_code == 0, f'Non-zero exit code: {exit_code}'

def get_tmp_frames(_path):
    files = os.listdir(_path)
    files.sort()
    return [
        os.path.join(_path, img) for img in files if img.endswith(".png")
    ]

def _create_frames(
    _start_index,
    _end_index,
    _frame_no
):
    tmp_dir = f'{PATH}/{_start_index}_{_frame_no}_tmp'
    print(tmp_dir)
    # make temp_dir
    os.makedirs(tmp_dir)

    # copy frame1 and frame2
    print("copying "+f'{PATH}/{PART}{_start_index}.png')
    shutil.copyfile(
        f'{PATH}/{PART}{_start_index[:-5]}.png',
        f'{tmp_dir}/{PART}{_start_index}.png'
    )
    shutil.copyfile(
        f'{PATH}/{PART}{_end_index[:-5]}.png',
        f'{tmp_dir}/{PART}{_end_index}.png'
    )

    # gen intermediary frames: iterate -> {str(int(i)).zfill(4)}_000{2+i}
    interpolation_level = {
        5: 2,
        7: 3,
    }[_frame_no]
    exit_code = os.system(
        f'python -m eval.interpolator_cli '
        f'--pattern "{tmp_dir}" '
        f'--model_path {MODEL} '
        f'--times_to_interpolate {interpolation_level}'
    )
    assert exit_code == 0, f'Non-zero exit code: {exit_code}'

    # copy new frames
    out_frames_path = f'{tmp_dir}/interpolated_frames'

    os.makedirs(out_frames_path)
    for i, new_frame in enumerate(get_tmp_frames(out_frames_path)[1:-1]):
        os.rename(
            new_frame,
            f'{PATH}/{PART}{_start_index}_000{2+i}.png'
        )

    # remove temp dir
    # shutil.rmtree(tmp_dir)

config = load_config()

for instruction in config:
    start = instruction["start"]
    end = instruction["end"]
    step = instruction["step"]
    print(f'Processing {start}/{end} with p: {step}')
    for i in range(int(start), int(end)):
        print(f'Index: {PART}{str(int(i)).zfill(5)}')
        if int(step) == 3:
            print("Middle frame")
            _create_frame(
                f'{str(int(i)).zfill(5)}_0001',
                f'{str(int(i+1)).zfill(5)}_0001',
                f'{str(int(i)).zfill(5)}_0003'
            )
            print("First frame")
            _create_frame(
                f'{str(int(i)).zfill(5)}_0001',
                f'{str(int(i)).zfill(5)}_0003',
                f'{str(int(i)).zfill(5)}_0002'
            )
            print("Last frame")
            _create_frame(
                f'{str(int(i)).zfill(5)}_0003',
                f'{str(int(i + 1)).zfill(5)}_0001',
                f'{str(int(i)).zfill(5)}_0004'
            )
        elif int(step) in [5, 7]:
            _create_frames(
                f'{str(int(i)).zfill(5)}_0001',
                f'{str(int(i + 1)).zfill(5)}_0001',
                int(step)
            )
        else:
            raise Exception(f'Not supported: {step} Only 3,5,7')

