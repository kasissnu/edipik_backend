import os
import cv2
import argparse
import numpy as np
from PIL import Image
import rawpy
import imageio
from bridge_ai_bucket.ai_image_editing.WBAugmenter import WBEmulator as wbAug
from bridge_ai_bucket.ai_image_editing.wbAug import WhiteBalance
from bridge_ai_bucket.ai_image_editing.image_enhance import Enhancer
from bridge_ai_bucket.ai_image_editing.demo_single_image import DeepWhiteBalance
from bridge_ai_bucket.ai_image_editing.light_calculation import lightPercentage
from bridge_ai_bucket.ai_image_editing.image_segmentation import ImageSegmentation
from bridge_ai_bucket.ai_image_editing import awr_to_jpg_converter
import time


def pipeline(img_path, out_path):

    img_path = os.path.abspath(img_path)
    light_percentage = lightPercentage(img_path, out_path)
    value = light_percentage.main(out_path)

    white_balance = WhiteBalance(img_path, out_path)
    enhanced_image_path = white_balance.main()   


    if value < 30:


        deep_white_balance = DeepWhiteBalance(enhanced_image_path, enhanced_image_path)
        enhanced_image_path = deep_white_balance.main()
       

  
    enhancer = Enhancer(enhanced_image_path, enhanced_image_path)
    enhanced_img = enhancer.main(out_path)
 

    img = cv2.imread(enhanced_img)


    path, img_name_path = os.path.split(enhanced_img)
    img_name, _ = os.path.splitext(img_name_path)


    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
   

    enhancer = ImageSegmentation(img, out_path, img_name, path)
 
    result = enhancer.main()
    return result

def get_enhanced_image(img, output_name, out_dir):
 
    image_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../assets/'))
    os.chmod(image_path, 0o777)

    if img.endswith('.jpg'):        
        img = os.path.join(image_path, img)            
    else:
        awr_to_jpg_converter.main(os.path.join(image_path, img))
        name, ext = os.path.splitext(img)
        name = name + '.jpg'
        img = os.path.join(image_path, name)
    

    # img = cv2.imread(img)

    
    os.chdir(image_path)
  
    
    enhanced_img= pipeline(img, image_path)

 

    cv2.imwrite(output_name, enhanced_img)

    response = image_path + "/" + output_name
    
 
    return response

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(
       prog='ImageEditor',
       description='Enhances the quality of the given image',
    )
    parser.add_argument("-i", "--image_dir_path", help="Input image path", required=True)
    parser.add_argument("-o", "--output_dir_path", help="Output image path to be saved")
  
    args = vars(parser.parse_args())
    img_dir = args['image_dir_path']
    out = args['output_dir_path']

       
    for filename in os.listdir(img_dir):

        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
            img = os.path.join(img_dir, filename)
              
        else:
            awr_to_jpg_converter.main(os.path.join(img_dir, filename))
            name, ext = os.path.splitext(filename)
            name = name + '.jpg'
            img = os.path.join(img_dir, name)
        
        pipeline(img, out) 
      
    suffix = ('T_AS.jpg', 'T_AS_deep_wb_enhanced.jpg', 'T_AS_enhanced.jpg', 'T_AS_deep_wb.jpg', 'brightness3.jpg', 'image_1.jpg', 'image_2.jpg')
      
    for filename in os.listdir(out):
        if filename.endswith(suffix):
            os.remove(os.path.join(out, filename))
        else:
            continue