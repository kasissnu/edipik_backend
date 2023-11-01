import os
import cv2
import argparse
import numpy as np
from PIL import Image
from .exposure import ExposureCorrection
from .colour_correction import ColorCorrection
from .contrast_correction import Adjustment
from .WBAugmenter.WBEmulator import WBEmulator as wbAug


def pipeline(img):

    # enhanced_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # wb_correct = wbAug.WBEmulator()
    # I = Image.fromarray(enhanced_img)
    # out_dir = "results"  # output directory
    # os.makedirs(out_dir, exist_ok=True)
    # images, wb_pf = wb_correct.generateWbsRGB(I)
    # index = wb_pf.index("_T_AS")

    # cont_bright = Adjustment(cv2.cvtColor(np.array(images[index]), cv2.COLOR_RGB2BGR))
    cont_bright = Adjustment(img)
    enhanced_img = cont_bright.correct()

    color_correction = ColorCorrection(enhanced_img)
    enhanced_img = color_correction.correct()

    ec = ExposureCorrection(enhanced_img)
    enhanced_img = ec.correct()
    return enhanced_img


def get_enhanced_image(img, output_name):
    os.chmod(img, 0o777)
    img = cv2.imread(img)

    image_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../assets/'))
    os.chmod(image_path, 0o777)

    os.chdir(image_path)
    # pipeline(img)
    enhanced_img = pipeline(img)

    cv2.imwrite(output_name, enhanced_img)

    response = image_path + "/" + output_name

    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='ImageEditor',
        description='Enhances the quality of the given image',
    )
    parser.add_argument(
        "-i", "--image", help="Input image path", required=True)
    parser.add_argument(
        "-o", "--output", help="Output image path to be saved", default="output.jpg")

    args = vars(parser.parse_args())
    img = cv2.imread(args['image'])

    # pipeline(img)
    enhanced_img = pipeline(img)

    cv2.imwrite(args['output'], enhanced_img)

    # enhanced_img.save(args['output'])
