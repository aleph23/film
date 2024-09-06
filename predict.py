import os
from pathlib import Path
import numpy as np
import tensorflow as tf
import tempfile
import mediapy
from PIL import Image

from eval import interpolator, util
import eval.interpolator_cli
import eval.interpolator_test

_UINT8_MAX_F = float(np.iinfo(np.uint8).max)


class Predictor:
    def __init__(self, model_path, frame1, frame2, times_to_interpolate=1):
        self.model = Path(model_path)
        self.frame1 = Path(frame1)
        self.frame2 = Path(frame2)
        self.tti = int(times_to_interpolate)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "/models/film_net/Style/saved_model")

        self.interpolator = interpolator.Interpolator(model_path, None)
        self.batch_dt = np.full(shape=(1,), fill_value=0.5, dtype=np.float32)

    @staticmethod
    def setup():
        """
        Predicts intermediate frames between frame1 and frame2 based on the provided times to interpolate.

        Args:
            frame1: The path to the first input frame (png, jpg, or jpeg image).
            frame2: The path to the second input frame (png, jpg, or jpeg image).
            tti: The number of times to interpolate.

        Returns:
            Path: The path to the output image or video with interpolated frames.

        Raises:
            AssertionError: If the input frames are not png, jpg, or jpeg images.

        """

        tf.random.set_seed(42)
        print("TensorFlow version:", tf.__version__)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "pretrained_models/film_net/Style/saved_model")
        Self.interpolator = interpolator.Interpolator(model_path, None)


    def predict(self, frame1, frame2, tti):
        INPUT_EXT = ['.png', '.jpg', '.jpeg']
        assert os.path.splitext(str(frame1))[-1] in INPUT_EXT and os.path.splitext(str(frame2))[-1] in INPUT_EXT, \
                "Please provide png, jpg or jpeg images."

        # make sure 2 images are the same size
        img1 = Image.open(str(frame1))
        img2 = Image.open(str(frame2))
        if img1.size != img2.size:
            img1 = img1.crop((0, 0, min(img1.size[0], img2.size[0]), min(img1.size[1], img2.size[1])))
            img2 = img2.crop((0, 0, min(img1.size[0], img2.size[0]), min(img1.size[1], img2.size[1])))
            frame1 = 'new_frame1.png'
            frame2 = 'new_frame2.png'
            img1.save(frame1)
            img2.save(frame2)

        if tti == 1:
            # First batched image.
            image_1 = util.read_image(str(frame1))
            image_batch_1 = np.expand_dims(image_1, axis=0)

            # Second batched image.
            image_2 = util.read_image(str(frame2))
            image_batch_2 = np.expand_dims(image_2, axis=0)

            # Invoke the model once.
            mid_frame = self.interpolator.interpolate(image_batch_1, image_batch_2, self.batch_dt)[0]
            out_path = Path(tempfile.mkdtemp()) / "out.png"
            util.write_image(str(out_path), mid_frame)
            return out_path

        input_frames = [str(frame1), str(frame2)]

        frames = list(
            util.interpolate_recursively_from_files(
                input_frames, tti, self.interpolator))
        print('Interpolated frames generated, saving now as output video.')

        ffmpeg_path = util.get_ffmpeg_path()
        mediapy.set_ffmpeg(ffmpeg_path)
        out_path = Path(tempfile.mkdtemp()) / "out.mp4"
        mediapy.write_video(str(out_path), frames, fps=24)
        return out_path

# Instantiate the Predictor class
predictor = Predictor(frame1, frame2, times_to_interpolate)

# Call the setup method to initialize the interpolator
predictor.setup()

# Use the predict method to generate intermediate frames
output_path = predictor.predict(frame1_path, frame2_path, tti)
