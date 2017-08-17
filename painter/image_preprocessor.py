import cv2


class ImagePreprocessor:
    def __init__(self, image, xml='data/haarcascade_frontalface_alt.xml', scale_factor=1.1):
        self.haar_face_cascade = cv2.CascadeClassifier(xml)
        self.scale_factor = scale_factor
        self.image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
