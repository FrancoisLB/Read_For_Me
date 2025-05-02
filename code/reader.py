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
from img_filter import rotate_image, adaptative_thresholding, to_img_pil, to_img_opencv
from logger import logger

class Reader:
    """
    Handle reader process
    """
    def __init__(self, basename:str='', extension:str='.jpg',
                 directory:str='.pictures/'):
        """
        Constructor
        
        Parameters:
        -----------
        basename: str
            The base name for the image and text files
        extension: str
        
        """
        self.cmd_camera  = 'libcamera-still --rotation 180 -t 500 -o '
        self.cmd_ocr = 'tesseract -l fra --psm 3'
        self.cmd_txt_to_sound = '/usr/bin/pico2wave -l fr-FR -w'
        self.cmd_mixer = 'amixer -q sset Headphone,0 '
        self.file_txt_to_sound = '.tmp_txt_to_sound.wav'
        self.directory = directory

        self.basename = basename
        self.extension = extension

    def set_base(self, basename:str, extension:str='.jpg') -> None:
        """
        Set basename and extension
        
        Parameters:
        -----------
        basename: str
            The base name for the image and text files
        extension: str
            The file extension for the image files
        
        Returns:
        --------    
        None
        """
        self.basename = basename
        self.extension = extension

    def is_image(self) -> bool:
        """
        Check if file image exists
        
        Returns:
        --------
        bool
            True if the image file exists, False otherwise
        """
        return os.path.isfile(self.basename+self.extension)

    def clean_text(self):
        """Text cleanup """
        logger.info('Reader.clean_text')
        inputfile = self.basename + '_raw' + '.txt'
        outputfile = self.basename + '.txt'
        with open(inputfile, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
            texte = ""
            # concatenate lines without an extra line break
            # one paragraph per line
        for line in lines:
            if line.strip() != '':
                texte += line.strip() + ' '
            else:
                texte += '\n\n'
        # remove unwanted characters
        texte = texte.replace('-\n', '')
        texte = texte.replace('-\r\n', '')
        with open(outputfile, 'w', encoding='utf-8') as outfile:
            outfile.write(texte)

    def snapshot(self) -> None:
        """Grab  image with raspicam
        """
        logger.info('Reader.snapshot')
        # Take photo
        outfile = self.basename + self.extension
        cmd = self.cmd_camera + ' ' + outfile
        logger.debug('os: %s', cmd)
        os.system(cmd)
        # copy image to directory
        if os.path.exists(self.directory) is False:
            shutil.copy(outfile, self.directory)

    def _filter(self, img, b_rotation, b_filter) -> Image:
        """ img PIL format 
        Filter image using OpenCV
        Parameters:
        ----------
        img: PIL image
            The image to be filtered
        b_rotation: bool
            If True, rotate the image
        b_filter: bool      
            If True, apply adaptive thresholding
        Returns:
        -------     
        img_filt_pil: PIL image
            The filtered image  
        """
        logger.info('_filter image')
        img_filt_cv2=None
        if b_rotation is True:
            osd_info = pyt.image_to_osd(img, output_type=pyt.Output.DICT)
            #print('--- Info Brute', osd_info)
            if osd_info['rotate'] != 0:
                img_filt_cv2 = rotate_image(np.asarray(img), - osd_info['rotate'])
                # pylint: disable=no-member
                cv2.imwrite(self.directory + 'rotation' + self.extension, img_filt_cv2)
        if b_filter is True:
            if img_filt_cv2 is None:
                # filter with image without rotation
                img_filt_cv2 = adaptative_thresholding(np.asarray(img), 20)
                # pylint: disable=no-member
                cv2.imwrite(self.directory + 'filtre' + self.extension, img_filt_cv2)
            else:
                # filter with image rotated
                img_filt_cv2 = adaptative_thresholding(img_filt_cv2, 20)
                # pylint: disable=no-member
                cv2.imwrite(self.directory + 'filter_and_rotation' + self.extension, img_filt_cv2)
        # Return
        if img_filt_cv2 is None:
            # no rotation and filter
            img_cv2 = to_img_opencv(img)
            # pylint: disable=no-member
            cv2.imwrite(self.directory + 'non_filtree' + self.extension, img_cv2)
            return img
        # image conversion from cv2 to pil format
        img_filt_pil = to_img_pil(img_filt_cv2)
        return img_filt_pil

    def ocr_to_text(self, b_rotation=False, b_filter=False) -> None:
        """OCR using tesseract"""
        logger.info('reader.ocr_to_text')
        img = Image.open(self.basename+self.extension)
        if b_rotation is True or b_filter is True:
            img =self._filter(img, b_rotation, b_filter)
        texte = pyt.image_to_string(img, lang='fra')
        outputfile = self.basename + '_raw' + '.txt'
        with open(outputfile, 'w', encoding='utf-8') as outfile:
            outfile.write(texte)

    def text_to_sound(self, text:str=None) -> None:
        """Text to sound using picoTTS"""
        logger.info('Reader.text_to_sound')
        if text:
            outfile = self.file_txt_to_sound
            cmd = f'{self.cmd_txt_to_sound} {outfile} "{text}"'
        else:
            infile = self.basename + '.txt'
            outfile = self.basename + '.wav'
            cmd = f'{self.cmd_txt_to_sound} {outfile} < {infile}'
        logger.debug('os: %s', cmd)
        os.system(cmd)
