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
Image processing functions for the Read For Me project
This module contains functions for image rotation, adaptive thresholding,
and conversion between OpenCV and PIL image formats.
"""
# fix pylint problem with cv2
# pylint: disable=no-member
import cv2
import numpy as np
from PIL import Image

def to_img_opencv(img_pil:Image) -> np.ndarray:
    """
    Convert a PIL image to OpenCV format
    
    Parameters:
    img_pil : PIL.Image
        The input image in PIL format.
    Returns:        
    imgOpenCV : numpy.ndarray
        The converted image in OpenCV format.
    """
    # Conver imgPIL to imgOpenCV
    i = np.array(img_pil) # After mapping from PIL to numpy : [R,G,B,A]
                         # numpy Image Channel system: [B,G,R,A]
    red = i[:,:,0].copy()
    i[:,:,0] = i[:,:,2].copy()
    i[:,:,2] = red
    return i

def to_img_pil(img_opencv:np.ndarray) -> Image:
    """
    Convert an OpenCV image to PIL format
    
    Parameters:
    ----------
    img_opencv : numpy.ndarray
        The input image in OpenCV format.
        
    Returns:
    -------
    img_pil : PIL.Image
        The converted image in PIL format.
    """
    return Image.fromarray(cv2.cvtColor(img_opencv, cv2.COLOR_BGR2RGB))

def rotate_image(image:np.ndarray, angle:float) -> np.ndarray:
    """
    Rotate the image by the given angle, adjusting the size 
    to keep all content.
    
    Parameters:
    ----------
    image : numpy.ndarray
        The input image to be rotated.
    angle : float
        The angle in degrees to rotate the image.
    
    Returns:
    -------
    rotated : numpy.ndarray
        The rotated image with adjusted size.   
    """

    # original image size
    (h, w) = image.shape[:2]
    # Center of the image
    image_center = (w // 2, h // 2)
    # rotation matrix
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    # Compute new dimension of the image
    cos = np.abs(rot_mat[0, 0])
    sin = np.abs(rot_mat[0, 1])
    # High and width of the image after rotation
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    # Adjustment of the rotation matrix to take into account the new size
    rot_mat[0, 2] += (new_w / 2) - image_center[0]
    rot_mat[1, 2] += (new_h / 2) - image_center[1]
    # Rotation of the image with the new size
    rotated = cv2.warpAffine(image, rot_mat, (new_w, new_h), flags=cv2.INTER_LINEAR)

    return rotated

# pylint: disable=too-many-locals
def adaptative_thresholding(img:np.ndarray, threshold:int) -> np.ndarray:
    """
    Apply adaptive thresholding to the input image.
    Parameters: 
    ----------
    img : numpy.ndarray
        The input image to be processed.
    threshold : int
        The threshold value for binarization.   
    Returns:
    -------
    binar : numpy.ndarray
        The binarized image after adaptive thresholding.
    """
    # Convert image to grayscale
    if len(img.shape) > 2:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray=img
    # Original image size
    origin_rows, origin_cols = gray.shape
    # Windows size
    win_m = int(np.floor(origin_rows/16) + 1)
    win_n = int(np.floor(origin_cols/16) + 1)
    # Image border padding related to windows size
    m_ext_end = round(win_m/2)-1
    n_ext_end = round(win_n/2)-1
    # Padding image
    aux =cv2.copyMakeBorder(gray, top=m_ext_end, bottom=m_ext_end,
                            left=n_ext_end, right=n_ext_end,
                            borderType=cv2.BORDER_REFLECT)
    windows = np.zeros((win_m,win_n),np.int32)
    # Image integral calculation
    image_integral = cv2.integral(aux, windows,-1)
    # Integral image size
    _, _ = image_integral.shape
    # Image cumulative pixels in windows size calculation
    result = (
            image_integral[win_m:, win_n:]       #bottom-right
            - image_integral[win_m:, :-win_n]    #bottom-left
            - image_integral[:-win_m, win_n:]    #top-right
            + image_integral[:-win_m, :-win_n]   #top-left
     )
    zeros_row = np.zeros((1, result.shape[1]), dtype=result.dtype)
    result = np.vstack([result, zeros_row])
    # Output binary image memory allocation
    binar = np.ones((origin_rows, origin_cols), dtype=bool)
    # Gray image weighted by windows size
    graymult = (gray).astype('float64')*win_m*win_n
    # Output image binarization
    binar[graymult <= result*(100.0 - threshold)/100.0] = False
    # binary image to UNIT8 conversion
    binar = (255*binar).astype(np.uint8)
    return binar
