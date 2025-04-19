import cv2
import numpy as np
from PIL import Image

def toImgOpenCV(imgPIL): # Conver imgPIL to imgOpenCV
    i = np.array(imgPIL) # After mapping from PIL to numpy : [R,G,B,A]
                         # numpy Image Channel system: [B,G,R,A]
    red = i[:,:,0].copy(); i[:,:,0] = i[:,:,2].copy(); i[:,:,2] = red
    return i

def toImgPIL(imgOpenCV): 
    return Image.fromarray(cv2.cvtColor(imgOpenCV, cv2.COLOR_BGR2RGB))

def rotate_image(image, angle):
    """
    Fait pivoter l'image de l'angle donné en ajustant la taille pour conserver tout le contenu.
    """
    # Taille originale
    (h, w) = image.shape[:2]

    # Calcul du centre de l'image
    image_center = (w // 2, h // 2)

    # Matrice de rotation
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)

    # Calcul des nouvelles dimensions de l'image
    cos = np.abs(rot_mat[0, 0])
    sin = np.abs(rot_mat[0, 1])

    # Nouvelle largeur et hauteur de l'image après rotation
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Ajustement de la matrice de rotation pour prendre en compte la nouvelle taille
    rot_mat[0, 2] += (new_w / 2) - image_center[0]
    rot_mat[1, 2] += (new_h / 2) - image_center[1]

    # Rotation avec nouvelle taille
    rotated = cv2.warpAffine(image, rot_mat, (new_w, new_h), flags=cv2.INTER_LINEAR)

    return rotated


def adaptative_thresholding(img, threshold):
    """
    """
    # Convert image to grayscale
    if len(img.shape) > 2:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray=img
    # Original image size
    orignrows, origncols = gray.shape
    # Windows size
    M = int(np.floor(orignrows/16) + 1)
    N = int(np.floor(origncols/16) + 1)
    # Image border padding related to windows size
    Mextend = round(M/2)-1
    Nextend = round(N/2)-1
    # Padding image
    aux =cv2.copyMakeBorder(gray, top=Mextend, bottom=Mextend, left=Nextend,
                          right=Nextend, borderType=cv2.BORDER_REFLECT)
    windows = np.zeros((M,N),np.int32)
    # Image integral calculation
    imageIntegral = cv2.integral(aux, windows,-1)
    # Integral image size
    nrows, ncols = imageIntegral.shape
    # Image cumulative pixels in windows size calculation
    result = (
            imageIntegral[M:, N:] #Bas-droite
            - imageIntegral[M:, :-N]    #Bas-gauche
            - imageIntegral[:-M, N:]    #Haut-droite
            + imageIntegral[:-M, :-N]         #Haut-gauche
     )
    zeros_row = np.zeros((1, result.shape[1]), dtype=result.dtype)
    result = np.vstack([result, zeros_row])
    # Output binary image memory allocation    
    binar = np.ones((orignrows, origncols), dtype=bool)
    # Gray image weighted by windows size
    graymult = (gray).astype('float64')*M*N
    # Output image binarization
    binar[graymult <= result*(100.0 - threshold)/100.0] = False
    # binary image to UNIT8 conversion
    binar = (255*binar).astype(np.uint8)
    
    return binar