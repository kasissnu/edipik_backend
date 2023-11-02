import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import shutil
import gc
gc.collect()

class lightPercentage:

    def __init__(self, img_path, out_path):
        self.img_path = img_path
        self.out_path = out_path

    def div_light_percentage(filepath):

        try:
            # Load image as greyscale

            im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

            if im is None:
                print(f'ERROR: Unable to load {filepath}')

            # Calculate mean brightness as percentage
            meanpercent = np.mean(im) * 100 / 255
         
        except:
            print('Unable to load the file: ', filepath)
            
        return meanpercent


    def find_div_light(topleft_filepath):
        # taking light percentage

        top_left_light_percentage = lightPercentage.div_light_percentage(topleft_filepath)
    
        return top_left_light_percentage

    def main(self, out_path):

        # make directory paths
        div_image_path = out_path + '/divided_image'
        brightness_only_path = out_path + '/brightness_only_image'

        # making divided_image and brightness_only directory
        os.makedirs(div_image_path)
        os.makedirs(brightness_only_path)
        
        os.chmod(div_image_path, 0o777)
        os.chmod(brightness_only_path, 0o777)


        file_path = self.img_path
     

        max_light_param_value = lightPercentage.find_div_light(file_path)
    

        # removing divided image directory and brightness_only directory
        shutil.rmtree(div_image_path)

        shutil.rmtree(brightness_only_path)
        
        return max_light_param_value 
    
