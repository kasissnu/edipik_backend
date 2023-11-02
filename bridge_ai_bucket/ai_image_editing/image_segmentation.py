import os
import random
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageEnhance
import sys

# Root directory of the project
ROOT_DIR = os.path.abspath("./bridge_ai_bucket/ai_image_editing")



# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
from bridge_ai_bucket.ai_image_editing.mrcnn import utils
import bridge_ai_bucket.ai_image_editing.mrcnn.model as modellib
from bridge_ai_bucket.ai_image_editing.mrcnn import visualize
from bridge_ai_bucket.ai_image_editing.samples.coco import coco

class InferenceConfig(coco.CocoConfig):
  
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

class ImageSegmentation:
    _model = None
    _instance = None

    def __init__(self, img, out_path, img_name, path):
        self.img = img
        self.out_path = out_path
        self.img_name = img_name
        self.path = path

    def div_light_percentage(filepath):
        # Load image as greyscale
        im = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        
        if im is None:
            print(f'ERROR: Unable to load {filepath}')

        # Calculate mean brightness as percentage
        meanpercent = np.mean(im) * 100 / 255

        return meanpercent

    def find_div_light(topleft_filepath):
        # taking light percentage
        top_left_light_percentage = ImageSegmentation.div_light_percentage(topleft_filepath)

        return top_left_light_percentage

    def brightness_parameter(percentage):
        # define the range
        min_value = 1.3
        max_value = 1.7

        # calculate the actual value based on percentage
        actual_value = min_value + percentage / 100 * (max_value - min_value)

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

    def result(out, img_name):
        # Load the image
        image_path = os.path.join(out,'temp_image_1.jpg')
        image = Image.open(image_path)

        # -------------------brightness enhancer (enhancer-01)---------------------------

        enhancer = ImageEnhance.Brightness(image)

        # getting maximum light part
        max_light_param_value = ImageSegmentation.find_div_light(image_path)

        # # selecting brightness parameter
        brightness = ImageSegmentation.brightness_parameter(max_light_param_value)
       
        brightness = brightness-0.6
        # applying brightness
        filtered_image = enhancer.enhance(brightness)

        filtered_image.save(os.path.join(out, 'brightness3.jpg'))

        foreground = cv2.imread(os.path.join(out, 'temp_image_2.jpg'))
        background = cv2.imread(os.path.join(out, 'brightness3.jpg'))

        # Create a mask for the foreground image
        gray_foreground = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_foreground, 10, 255, cv2.THRESH_BINARY)

        # Invert the mask
        mask_inv = cv2.bitwise_not(mask)


        # Apply the mask to the foreground and background images

        try:
            foreground = cv2.bitwise_and(foreground, foreground, mask=mask)
            background = cv2.bitwise_and(background, background, mask=mask_inv)
            # Combine the foreground and background images
            result = cv2.add(foreground, background)

            # Save the merged image

            # img_name = img_name +'_output.jpg'
            # path = os.path.join(out, img_name)
            return result
            # cv2.imwrite(path, result)
                
        except:
             print('Will not be able to work on this image because of th size of images: ', img_name)


    def get_model():

        if ImageSegmentation._model is None:
            
            # Directory to save logs and trained model
            MODEL_DIR = os.path.join(ROOT_DIR, "logs")
          

            # Local path to trained weights file
            COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
            # COCO_MODEL_PATH = os.path.abspath('/home/dhruvi/work/ai_photo_editing/photo-editing-ai-be/bridge_ai_bucket/ai_image_editing/mask_rcnn_coco.h5')
            # Download COCO trained weights from Releases if needed
            if not os.path.exists(COCO_MODEL_PATH):
               
                utils.download_trained_weights(COCO_MODEL_PATH)

          

            # Directory of images to run detection on
            config = InferenceConfig()
        
            config.display()

            # Create model object in inference mode.
            model1 = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
            # Load weights trained on MS-COCO

            model1.load_weights(os.path.join(ROOT_DIR, "mask_rcnn_coco.h5"),  by_name=True)
            # /home/dhruvi/work/ai_photo_editing/photo-editing-ai-be/bridge_ai_bucket/ai_image_editing/mask_rcnn_coco.h5
      

            ImageSegmentation._model = model1

        return ImageSegmentation._model
    
    def main(self):

        model = ImageSegmentation.get_model()
 

        image = self.img

        results = model.detect([image], verbose=1)

        r = results[0]

        converted_mask = r["masks"]
        mask = converted_mask.astype(np.uint8)

        # Convert the mask to a binary mask (0 or 1)
        binary_mask = np.any(mask, axis=-1).astype(np.uint8)

        # Invert the binary mask (to get the foreground instead of the masked part)
        inverted_mask = 1 - binary_mask

        # Apply the inverted mask to the original image
        background_image = image * inverted_mask[..., np.newaxis]
        image_rgb = cv2.cvtColor(background_image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(os.path.join(self.out_path, "temp_image_1.jpg"), image_rgb)

        # Resize the mask to match the original image dimensions (if needed)
        resized_mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

        # Convert the resized mask to a binary mask (0 or 1)
        binary_mask = np.any(resized_mask, axis=-1).astype(np.uint8)

        # Merge the mask into the original image using bitwise AND
        try:
            foreground_image = cv2.bitwise_and(image, image, mask=binary_mask)
            image_rgb = cv2.cvtColor(foreground_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(os.path.join(self.out_path, "temp_image_2.jpg"), image_rgb)

            result = ImageSegmentation.result(self.out_path, self.img_name)
            return result
        
        except:
             print('Will not be able to work for this image because the shape is not correct: ', self.img_name)