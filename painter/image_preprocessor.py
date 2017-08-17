def convert_image_to_grey(image_name):
    from PIL import Image
    img = Image.open(image_name).convert('LA')
    img.save('grey_'+image_name)


import cv2
import matplotlib.pyplot as plt
import time
