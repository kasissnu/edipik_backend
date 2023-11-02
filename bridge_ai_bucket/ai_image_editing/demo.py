from PIL import Image
import os
from WBAugmenter import WBEmulator as wbAug

wbColorAug = wbAug.WBEmulator()  # create an instance of the WB emulator
in_img = r"D:\ai photo editing\white_balance\Deep_White_Balance\PyTorch\_DSC4829_AWB_local.jpg"  # input image filename
filename, file_extension = os.path.splitext(in_img)  # get file parts
out_dir = "."  # output directory
os.makedirs(out_dir, exist_ok=True)
I = Image.open(in_img)  # read the image
outNum = 10  # number of images to generate (should be <= 10)
# generate new images with different WB settings
outImgs, wb_pf = wbColorAug.generateWbsRGB(I, outNum)

for i in range(outNum):  # save images
    outImg = outImgs[i]  # get the ith output image
    outImg.save(out_dir + '/' + os.path.basename(filename) +
                '_' + wb_pf[i] + file_extension)  # save it



