#!/usr/bin/env python2
#

import argparse
import cv2


class ImagePreprocessor:
    def __init__(self, xml, scale_factor=1.1):
        self.haar_face_cascade = cv2.CascadeClassifier(xml)
        self.scale_factor = scale_factor
        self.image = None
        self.faces = None

    def upload_image(self, image_path):
        self.image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2GRAY)
        self.faces = self.haar_face_cascade.detectMultiScale(self.image,
                                                             scaleFactor=self.scale_factor,
                                                             minNeighbors=5)

    def image_cropper(self):
        # cropping images
        # faces = (x, y, w, h)
        face_array = self.faces.flatten()
        height = face_array[3]
        width = face_array[2]
        width, height = max(width, height), max(width, height)
        cropped = self.image[int(face_array[1] - height * 0.2):int((face_array[1] + height * 1.3)),
                             int(face_array[0] - width * 0.2):int((face_array[0] + width * 1.3))]

        return cv2.resize(cropped, (512, 512))

    def image_save(self, img_path):
        cv2.imwrite(img_path, self.image_cropper())

    def pre_process_image(self, image_path, new_image_path):
        self.upload_image(image_path)
        self.image_save(new_image_path)


def argument_parser():
    parser = argparse.ArgumentParser(description='Image preprocessor')
    parser.add_argument('--image', dest='image_path', type=str)
    parser.add_argument('--grey', dest='grey_path', type=str)
    parser.add_argument('--xml', dest='xml_path', type=str,
                        default='data/haarcascade_frontalface_alt.xml')

    return parser.parse_args()


def main():
    args = argument_parser()
    impp = ImagePreprocessor(args.xml_path)
    impp.pre_process_image(args.image_path, args.grey_path)


if __name__ == '__main__':
    main()
