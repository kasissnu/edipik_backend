import os
import argparse
from bridge_ai_bucket.ai_image_editing.WBAugmenter import WBEmulator as wbAug


def parse_args():
    parser = argparse.ArgumentParser(description="WB color augmenter")
    p = parser.add_argument
    p("--input_image_filename",
      help="Input image's full filename (for a single image augmentation)")
    p("--input_image_dir",
      help="Training image directory (use it for batch processing)")
    p("--out_dir", help="Output directory")
    p("--out_number", type=int, default=10,
      help="Number of output images for each input image")
    p("--write_original", type=int, default=1,
      help="Save copy of original image(s) in out_dir")
    p("--ground_truth_dir", help="Ground truth directory")
    p("--out_ground_truth_dir", help="Output directory for ground truth files")
    p("--ground_truth_ext", help="File extension of ground truth files")
    return parser.parse_args()

class WhiteBalance:

  def __init__(self, img, out):
     
      self.img = img
      self.out = out

  def main(self):

      wbColorAug = wbAug.WBEmulator()  # create an instance of the WB emulator
      out_dir = wbColorAug.single_image_processing(self.img, self.out, 1, 0)

      return out_dir

