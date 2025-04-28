# Python code Read For Me which is dedicated to visualy impaired people
# to read A4 document, based on Raspberry PI.
# Copyright 2025 Read For Me
# Contributors: see AUTHORS file
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
    Reader class to handle image capture, OCR processing, and text-to-speech conversion
    This class provides methods to take a snapshot, perform OCR on the image,
    clean up the extracted text, and convert the text to speech using picoTTS
"""
import os
import shutil
import numpy as np
import cv2
from PIL import Image
import pytesseract as pyt
from constantes import CMD_CAMERA, CMD_SOUND
from img_filter import rotate_image, adaptative_thresholding, to_img_pil, to_img_opencv
from logger import logger

def clean_text(basename):
    """Text cleanup """
    logger.info('player.clean_text')
    inputfile = basename + '_raw' + '.txt'
    outputfile = basename + '.txt'
    with open(inputfile, 'r', encoding='utf-8') as infile:
        texte = infile.read()
        texte = texte.replace('-\n', '')
        texte = texte.replace('-\r\n', '')
        texte = texte.strip()
        with open(outputfile, 'w', encoding='utf-8') as outfile:
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


def _filter(img, b_rotation, b_filter):
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
            # pylint: disable=no-member
            cv2.imwrite(pictures_dir + 'rotation' + extension, img_filt_cv2)
    if b_filter is True:
        if img_filt_cv2 is None:
            # filter with image without rotation
            img_filt_cv2 = adaptative_thresholding(np.asarray(img), 20)
            # pylint: disable=no-member
            cv2.imwrite(pictures_dir + 'filtre' + extension, img_filt_cv2)
        else:
            # filter with image rotated
            img_filt_cv2 = adaptative_thresholding(img_filt_cv2, 20)
            # pylint: disable=no-member
            cv2.imwrite(pictures_dir + 'filter&rotation' + extension, img_filt_cv2)
    # Return
    if img_filt_cv2 is None:
        # no rotation and filter
        img_cv2 = to_img_opencv(img)
        # pylint: disable=no-member
        cv2.imwrite(pictures_dir + 'non_filtree' + extension, img_cv2)
        return img
    # image conversion from cv2 to pil format
    img_filt_pil = to_img_pil(img_filt_cv2)
    return img_filt_pil

def ocr_to_text(basename, b_rotation=False, b_filter=False,  extension='.jpg'):
    """OCR using tesseract"""
    logger.info('reader.ocr_to_text')
    img = Image.open(basename+extension)
    if b_rotation is True or b_filter is True:
        img =_filter(img, b_rotation, b_filter)
    texte = pyt.image_to_string(img, lang='fra')
    outputfile = basename + '_raw' + '.txt'
    with open(outputfile, 'w', encoding='utf-8') as outfile:
        outfile.write(texte)


def text_to_sound(basename):
    """Text to sound using picoTTS"""
    logger.info('reader.text_to_sound')

    infile = basename + '.txt'
    outfile = basename + '.wav'

    cmd = CMD_SOUND + outfile + " < " + infile
    logger.info(cmd)

    os.system(cmd)
