import cv2
import matplotlib.pyplot as plt
import numpy as np

img = cv2.imread('image.jpg')
print(img.shape)

haar_data = cv2.CascadeClassifier('data.xml')

while True:
    faces = haar_data.detectMultiScale(img)
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 4)
    cv2.imshow('poza', img)
    if cv2.waitKey(2) == 27:
        break
cv2.destroyAllWindows()

capture = cv2.VideoCapture(0)

data = []
while True:
    flag, img = capture.read()
    faces = haar_data.detectMultiScale(img)
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 4)
        face = img[y : y + h, x : x + w, :]
        face = cv2.resize(face, (50,50))
        print(len(data))
        if len(data) < 400:
            data.append(face)
    if cv2.waitKey(2) == 27 or len(data) >= 300:
        break
capture.release()
cv2.destroyAllWindows()

#np.save('without_mask.npy',data)
np.save('with_mask.npy',data)