import os
import numpy as np
from logger import logger
from constantes import *
import pytesseract as pyt
from PIL import Image
import cv2
import shutil
from img_filter import rotate_image, adaptative_thresholding, toImgPIL, toImgOpenCV

def clean_text(basename):
    """Text cleanup """
    logger.info('player.clean_text')
    inputfile = basename + '_raw' + '.txt'
    outputfile = basename + '.txt'
    with open(inputfile, 'r') as infile:
        texte = infile.read()
        texte = texte.replace('-\n', '')
        texte = texte.replace('-\r\n', '')
        texte = texte.strip()
        with open(outputfile, 'w') as outfile:
            outfile.write(texte)

def snapshot(basename, extension='.jpg'):
    """Grab image"""
    logger.info('reader.snapshot')
    # Take photo
    outfile = basename + extension
    cmd = CMD_CAMERA + ' ' + outfile
    logger.info(cmd)
    os.system(cmd)

    # Copie la photo dans le dossier Pictures
    pictures_dir = '/home/pi/Pictures/'
    shutil.copy(outfile, pictures_dir + 'base' + extension)

def ocr_to_text1(basename, extension='.jpg'):
    """OCR using tesseract"""
    logger.info('reader.ocr_to_text')
    infile = basename + extension
    cmd = CMD_OCR + ' ' + infile + ' ' + basename + '_raw'
    logger.info(cmd)
    os.system(cmd)
    #proc=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    #proc.wait()
    return

def _filter(basename, img, b_rotation, b_filter):
    """ img PIL format """
    logger.info('_filter image')
    img_filt_cv2=None
    pictures_dir = '/home/pi/Pictures/'
    extension = '.jpg'
    if b_rotation is True:
        osd_info = pyt.image_to_osd(img, output_type=pyt.Output.DICT) 
        #print('--- Info Brute', osd_info)
        if osd_info['rotate'] != 0:  
            img_filt_cv2 = rotate_image(np.asarray(img), - osd_info['rotate'])
            cv2.imwrite(pictures_dir + 'rotation' + extension, img_filt_cv2)
    if b_filter is True:
        if img_filt_cv2 is None:
            # filter with image without rotation
            img_filt_cv2 = adaptative_thresholding(np.asarray(img), 20)
            cv2.imwrite(pictures_dir + 'filtre' + extension, img_filt_cv2)
        else:
            # filter with image rotated
            img_filt_cv2 = adaptative_thresholding(img_filt_cv2, 20)
            cv2.imwrite(pictures_dir + 'filter&rotation' + extension, img_filt_cv2)
    # Return 
    if img_filt_cv2 is None:
        # no rotation and filter
        img_cv2 = toImgOpenCV(img)
        cv2.imwrite(pictures_dir + 'non_filtree' + extension, img_cv2) 
        return img
    else:
        # image conversion from cv2 to pil format
        img_filt_pil = toImgPIL(img_filt_cv2)
        return img_filt_pil

def ocr_to_text(basename, b_rotation=False, b_filter=False,  extension='.jpg'):
    """OCR using tesseract"""
    logger.info('reader.ocr_to_text')
    img = Image.open(basename+extension)
    if b_rotation is True or b_filter is True:
        img =_filter(basename, img, b_rotation, b_filter)
    texte = pyt.image_to_string(img, lang='fra')
    outputfile = basename + '_raw' + '.txt'
    with open(outputfile, 'w') as outfile:
            outfile.write(texte)
    return


def text_to_sound(basename):
    """Text to sound using picoTTS"""
    logger.info('reader.text_to_sound')

    infile = basename + '.txt'
    outfile = basename + '.wav'

    cmd = CMD_SOUND + outfile + " < " + infile
    logger.info(cmd)

    os.system(cmd)
