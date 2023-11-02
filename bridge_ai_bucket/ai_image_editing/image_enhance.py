import cv2
import numpy as np
from PIL import Image, ImageEnhance
import shutil 
import os

class Enhancer:
    def __init__(self, img, out):
        self.img = img
        self.out = out
        
    
    def div_light_percentage(filepath):
        
        # Load image as greyscale
        try:
        
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
        top_left_light_percentage = Enhancer.div_light_percentage(topleft_filepath)

        return (top_left_light_percentage)
    
    def brightness_parameter(percentage):

        # define the range
        min_value = 1.3
        max_value = 1.7

        # calculate the actual value based on percentage
        actual_value = min_value + percentage/100 * (max_value - min_value)

        # check if actual value is within range
        if actual_value < min_value:
            actual_value = min_value
        elif actual_value > max_value:
            actual_value = max_value

        # check if percentage is below 30% and adjust the actual value accordingly
        if percentage < 30:
            actual_value += 0.1
            if actual_value > max_value:
                actual_value = max_value

        return actual_value

    def find_dark_shade_percentage(file_path):

        image = cv2.imread(file_path)

        # Convert the image to the HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define the color range you want to analyze
        lower_color = np.array([0, 0, 0])  # Adjust the lower threshold for the color

        # Adjust the upper threshold for the color
        upper_color = np.array([40, 40, 40])

        # Create a mask for the specified color range
        mask = cv2.inRange(hsv, lower_color, upper_color)

        # Calculate the percentage of the color's appearance
        total_pixels = mask.size
        color_pixels = cv2.countNonZero(mask)
        percentage = (color_pixels / total_pixels) * 100

        return percentage


    def color_parameter_value(dark_shade_percentage):
        color_parameter = 0

        # range
        max_value = 1.7
        min_value = 1.4

        # conditional statements
        if dark_shade_percentage < 3.5:
            color_parameter = max_value
        elif dark_shade_percentage > 3.5 and dark_shade_percentage < 3.8:
            color_parameter = 1.65
        else:
            color_parameter = min_value + \
                dark_shade_percentage/100 * (max_value - min_value)

        # final value check
        if color_parameter < min_value:
            color_parameter = min_value
        elif color_parameter > max_value:
            color_parameter = max_value

        return color_parameter

    def main(self, out_path):

        # make directory paths
        div_image_path = out_path + '/divided_image'
        brightness_only_path = out_path + '/brightness_only_image'

        # making divided_image and brightness_only directory
        os.makedirs(div_image_path)
        os.makedirs(brightness_only_path)

        # for each_file in file_names:

        
        # each image paths
        file_path = self.img
        brightness_file_path = self.img

        # Load the image
        image = Image.open(file_path)

        # -------------------brightness enhancer (enhancer-01)---------------------------
        enhancer = ImageEnhance.Brightness(image)

        # getting maximum light part
        max_light_param_value = Enhancer.find_div_light(file_path)

        # selecting brightness parameter
        brightness = Enhancer.brightness_parameter(max_light_param_value)

        # applying brightness
        filtered_image = enhancer.enhance(brightness)

        # only brightness applied images save
        filtered_image.save(brightness_file_path)

        # ------------------------------Enhance the color saturation (enhancer-02)-----------------------
        enhancer_02 = ImageEnhance.Color(filtered_image)

        # finding dark shade percentage in image
        dark_shade_percent = Enhancer.find_dark_shade_percentage(brightness_file_path)

        # finalizing color value
        color_value = Enhancer.color_parameter_value(dark_shade_percent)

        # applying brightness
        filtered_image = enhancer_02.enhance(color_value)

        # ------------------------------------contrast enhancer (enhancer-03)--------------------------------
        enhancer_03 = ImageEnhance.Contrast(filtered_image)

        # applying contrast
        filtered_image = enhancer_03.enhance(0.9)

        # saving final output image

        path, img_name = os.path.split(self.out)
        image, ext = os.path.splitext(img_name)
      
        out_image = path +'/'+ image + '_enhanced'+ ext
        filtered_image.save(out_image)

        # removing divided image directory and brightness_only directory
        shutil.rmtree(div_image_path)
       

        shutil.rmtree(brightness_only_path)
     
        return out_image
