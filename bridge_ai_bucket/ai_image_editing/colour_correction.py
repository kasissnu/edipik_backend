import cv2
import os
import math
import glob
import numpy as np

class ColorCorrection:
    def __init__(self, img):
        self.img = img

    def apply_mask(self, matrix, mask, fill_value):
        masked = np.ma.array(matrix, mask=mask, fill_value=fill_value)
        return masked.filled()

    def apply_threshold(self, matrix, low_value, high_value):
        low_mask = matrix < low_value
        matrix = self.apply_mask(matrix, low_mask, low_value)

        high_mask = matrix > high_value
        matrix = self.apply_mask(matrix, high_mask, high_value)

        return matrix
    
    def simplest_cb(self, percent=1.0):
        assert self.img.shape[2] == 3
        assert percent > 0 and percent < 100

        half_percent = percent / 200.0

        channels = cv2.split(self.img)

        out_channels = []
        for channel in channels:
            assert len(channel.shape) == 2
            # find the low and high precentile values (based on the input percentile)
            height, width = channel.shape
            vec_size = width * height
            flat = channel.reshape(vec_size)

            assert len(flat.shape) == 1

            flat = np.sort(flat)

            n_cols = flat.shape[0]
            low_val  = flat[math.floor(n_cols * half_percent)]
            high_val = flat[math.ceil( n_cols * (1.0 - half_percent))]

            # saturate below the low percentile and above the high percentile
            thresholded = self.apply_threshold(channel, low_val, high_val)
            # scale the channel
            normalized = cv2.normalize(thresholded, thresholded.copy(), 0, 255, cv2.NORM_MINMAX)
            out_channels.append(normalized)

        return cv2.merge(out_channels)
    
    def correct(self):
        image = self.simplest_cb()
        return image