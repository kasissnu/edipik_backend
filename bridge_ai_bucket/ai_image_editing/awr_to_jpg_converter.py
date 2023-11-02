import sys
from PIL import Image
import os
from threading import *
import rawpy
import imageio
from datetime import datetime
import optparse


# Keeping the output cleaned 
screenLock = Semaphore(value=1)


# convert RAW images function
def convert_raw(file, extension=".jpg"):

    try:
        with rawpy.imread(file) as raw:
           rgb = raw.postprocess()
        file_path, file_name = os.path.split(file)
        file, _ = os.path.splitext(file_name)
        imageio.imsave(os.path.abspath(os.path.join(file_path, file) + extension), rgb)

    except:
        lst = []
        file_path, file_name = os.path.split(file)
        file, _ = os.path.splitext(file_name)
        lst.append(os.path.join(file_name, file))
    
        



# rename .ai 2 pdf and problem solved! 
def ai_2_pdf(file_path, e):
    if e.endswith('.ai'):
        os.rename(e, os.path.join(file_path, e + '.pdf'))

# IT IS POINTLESS TO CONVERT WHAT IS ALREADY CONVERTED!!!!
def image_not_exists(file_path, e):
    if os.path.isfile(os.path.join(file_path, e + '.jpg')):
        screenLock.acquire()
        screenLock.release()
        return False
    else:
        return True


# here we check each file to decide what to do		
def check_extension(file_path, ext):
    # set supported raw conversion extensions!
    extensionsForRawConversion = ['.dng', '.raw', '.cr2', '.crw', '.erf', '.raf', '.tif', '.kdc', '.dcr', '.mos',
                                '.mef', '.nef', '.orf', '.rw2', '.pef', '.x3f', '.srw', '.srf', '.sr2', '.arw',
                                '.mdc', '.mrw']
    # set supported imageio conversion extensions
    extensionsForConversion = ['.ppm', '.psd', '.tif', '.webp']

    for i in extensionsForRawConversion:
        if ext.lower().endswith(i):
            return 'RAW'

    for e in extensionsForConversion:
        if ext.lower().endswith(e):
            return 'NOT_RAW'
    # check if an .ai exists and rename it to .pdf	!
    ai_2_pdf(file_path, ext)


def main(file):

    # CHECK IF WE HAVE CONVERTED THIS IMAGE! IF YES SKIP THE CONVERSIONS!
    file_path, file_name = os.path.split(file)
    if image_not_exists(file_path, os.path.join(file_path, file_name)):
        
        if 'RAW' == check_extension(file_path, file):
            convert_raw(os.path.join(file_path, file_name))
         
        if 'NOT_RAW' == check_extension(file_path, os.path.join(file_path, file_name)):
            convert_raw(os.path.join(file_path, file_name))

    os.remove(os.path.join(file_path, file_name))