import cv2
import numpy as np


class Adjustment:

    def __init__(self, img):
        self.img = img

    def contrast_correction(self):
        lab = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(50, 50))

        lab[0] = clahe.apply(lab[0])
        lab[1] = clahe.apply(lab[1])

        self.img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def brightness_correction(self):
        lab_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # extract L channel
        L = cv2.split(lab_img)[2]

        # calculate mean and standard deviation of L channel
        mean, std_dev = cv2.meanStdDev(L)

        # calculate gamma value based on mean and standard deviation
        gamma = np.log(0.1*255.0) / np.log(mean).clip(0, 255)

        # apply gamma correction
        self.img = np.power(self.img / 255.0, gamma)

        # convert corrected image to uint8 format
        self.img = np.uint8(self.img * 255)

    def correct(self):
        self.contrast_correction()
        self.brightness_correction()
        return self.img
