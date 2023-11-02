"""
 Demo single image
 Copyright (c) 2019 Samsung Electronics Co., Ltd. All Rights Reserved
 If you use this code, please cite the following paper:
 Mahmoud Afifi and Michael S Brown. Deep White-Balance Editing. In CVPR, 2020.
"""
__author__ = "Mahmoud Afifi"
__credits__ = ["Mahmoud Afifi"]

import argparse
import logging
import os
import torch
from PIL import Image
from bridge_ai_bucket.ai_image_editing.arch import deep_wb_model
import bridge_ai_bucket.ai_image_editing.utilities.utils as utls
from bridge_ai_bucket.ai_image_editing.utilities.deepWB import deep_wb
import bridge_ai_bucket.ai_image_editing.arch.splitNetworks as splitter
from bridge_ai_bucket.ai_image_editing.arch import deep_wb_single_task

def get_args():
    parser = argparse.ArgumentParser(description='Changing WB of an input image.')
    parser.add_argument('--model_dir', '-m', default='./models/',
                        help="Specify the directory of the trained model.", dest='model_dir')
    parser.add_argument('--input', '-i', help='Input image filename', dest='input',
                        default='../example_images/00.JPG')
    parser.add_argument('--output_dir', '-o', default='../result_images',
                        help='Directory to save the output images', dest='out_dir')
    parser.add_argument('--task', '-t', default='all',
                        help="Specify the required task: 'AWB', 'editing', or 'all'.", dest='task')
    parser.add_argument('--target_color_temp', '-tct', default=None, type=int,
                        help="Target color temperature [2850 - 7500]. If specified, the --task should be 'editing'",
                        dest='target_color_temp')
    parser.add_argument('--mxsize', '-S', default=656, type=int,
                        help="Max dim of input image to the network, the output will be saved in its original res.",
                        dest='S')
    parser.add_argument('--show', '-v', action='store_true', default=True,
                        help="Visualize the input and output images",
                        dest='show')
    parser.add_argument('--save', '-s', action='store_true',
                        help="Save the output images",
                        default=True, dest='save')
    parser.add_argument('--device', '-d', default='cuda',
                        help="Device: cuda or cpu.", dest='device')

    return parser.parse_args()

class DeepWhiteBalance:

    def __init__(self, img_path, out_path):
        self.img_path = img_path
        self.out_path = out_path

    def main(self):
  
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
 
        device = torch.device('cpu')

        fn = self.img_path
        out_dir = self.out_path
       
        self.tosave = True
        
        model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai_image_editing/models/'))
      
        if os.path.exists(os.path.join(model_dir, 'net_awb.pth')):
            # load awb net
            net_awb = deep_wb_single_task.deepWBnet()
            logging.info("Loading model {}".format(os.path.join(model_dir, 'net_awb.pth')))
            logging.info(f'Using device {device}')
            net_awb.to(device=device)
            net_awb.load_state_dict(torch.load(os.path.join(model_dir, 'net_awb.pth'),
                                            map_location=device))
            net_awb.eval()
        elif os.path.exists(os.path.join(model_dir, 'net.pth')):
            net = deep_wb_model.deepWBNet()
            logging.info("Loading model {}".format(os.path.join(model_dir, 'net.pth')))
            logging.info(f'Using device {device}')
            net.load_state_dict(torch.load(os.path.join(model_dir, 'net.pth')))
            net_awb, _, _ = splitter.splitNetworks(net)
            net_awb.to(device=device)
            net_awb.eval()
        else:
            raise Exception('Model not found!')


        logging.info("Processing image {} ...".format(fn))
        img = Image.open(fn)
        _, fname = os.path.split(fn)
        name, _ = os.path.splitext(fname)
        
        out_awb = deep_wb(img, 'awb' ,  net_awb=net_awb, device=device, s= 656)
        # if tosave:
        result_awb = utls.to_image(out_awb)
        path, _ = os.path.split(out_dir)
        out_dir_name = path + '/' +name + '_deep_wb.jpg'
        
        result_awb.save(out_dir_name)
        return out_dir_name

