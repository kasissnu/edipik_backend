import cv2
import numpy as np

class ExposureCorrection:
    def __init__(self, img):
        self.img = img

    def gamma_correction(self):
        lab_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2LAB)
        L = cv2.split(lab_img)[0]
        mean, std_dev = cv2.meanStdDev(L)

        gamma = np.log(0.1*255.0) / np.log(mean).clip(0,255)
        img_corrected = np.power(self.img /255.0, gamma)

        self.img = np.uint8(img_corrected * 255)
    
    def saturation_correction(self):
        hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        s = cv2.split(hsv_img)[1]
        mean,std_dev = cv2.meanStdDev(s)
        gamma = 1/ (1+ (std_dev/mean)**2)

        img_corrected = np.power(self.img / 255.0, gamma)
        self.img = np.uint8(img_corrected * 255)
    
    def correct(self):
        self.gamma_correction()
        # self.saturation_correction()
        return self.img

