import json
import os
import shutil

PART = "L1S1"
PATH = f'~/Movies/{PART}/frames'
MODEL = "pretrained_models/film_net/Style/saved_model"

def load_config():
    with open(f"config/{PART}.json") as f:
        return json.load(f)

def _create_frame(
    _start_index,
    _end_index,
    _name
):
    exit_code = os.system(
        f'python -m eval.interpolator_test '
        f'--frame1 {PATH}/{PART}_{_start_index}.png '
        f'--frame2 {PATH}/{PART}_{_end_index}.png '
        f'--model_path {MODEL} '
        f'--output_frame {PATH}/{PART}_{_name}.png'
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
    tmp_dir = f'{PATH}/{PART}_{_start_index}_{_frame_no}_tmp'

    # make temp_dir
    os.makedirs(tmp_dir)

    # copy frame1 and frame2
    shutil.copyfile(
        f'{PATH}/{PART}_{_start_index}.png',
        f'{tmp_dir}/{PART}_{_start_index}.png'
    )
    shutil.copyfile(
        f'{PATH}/{PART}_{_end_index}.png',
        f'{tmp_dir}/{PART}_{_end_index}.png'
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
    for i, new_frame in enumerate(get_tmp_frames(out_frames_path)[1:-1]):
        os.rename(
            new_frame,
            f'{PATH}/{PART}_{_start_index[:-5]}_000{2+i}.png'
        )

    # remove temp dir
    shutil.rmtree(tmp_dir)

config = load_config()
for instruction in config:
    start = instruction["start"]
    end = instruction["end"]
    step = instruction["step"]
    print(f'Processing {start}/{end} with p: {step}')
    for i in range(int(start), int(end)):
        print(f'Index: {str(int(i)).zfill(4)}')
        if int(step) == 3:
            print("Middle frame")
            _create_frame(
                f'{str(int(i)).zfill(4)}_0001',
                f'{str(int(i+1)).zfill(4)}_0001',
                f'{str(int(i)).zfill(4)}_0003'
            )
            print("First frame")
            _create_frame(
                f'{str(int(i)).zfill(4)}_0001',
                f'{str(int(i)).zfill(4)}_0003',
                f'{str(int(i)).zfill(4)}_0002'
            )
            print("Last frame")
            _create_frame(
                f'{str(int(i)).zfill(4)}_0003',
                f'{str(int(i + 1)).zfill(4)}_0001',
                f'{str(int(i)).zfill(4)}_0004'
            )
        elif int(step) in [5, 7]:
            _create_frames(
                f'{str(int(i)).zfill(4)}_0001',
                f'{str(int(i + 1)).zfill(4)}_0001',
                int(step)
            )
        else:
            raise Exception(f'Not supported: {step}')
