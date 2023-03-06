import numpy as np
import cv2
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import RPi.GPIO as GPIO
import requests
import time

def mask_detection():
    with_mask = np.load('with_mask.npy')
    without_mask = np.load('without_mask.npy')

    with_mask = with_mask.reshape(1000,50 * 50 * 3)
    without_mask = without_mask.reshape(1000,50 * 50 * 3)

    X = np.r_[with_mask, without_mask]
    labels = np.zeros(X.shape[0])
    labels[1000:] = 1.0
    names = {0 : 'Mask', 1:'No Mask'}

    x_train, x_test, y_train, y_test = train_test_split(X,labels, test_size = 0.25)
    pca = PCA(n_components=3)
    x_train = pca.fit_transform(x_train)

    svm = SVC()
    svm.fit(x_train, y_train)
    x_test = pca.transform(x_test)
    y_pred = svm.predict(x_test)

    haar_data = cv2.CascadeClassifier('data.xml')
    capture = cv2.VideoCapture(0)
    data = []
    font = cv2.FONT_HERSHEY_COMPLEX
    while True:
        flag, img = capture.read()
        if flag:
            faces = haar_data.detectMultiScale(img)
            for x, y, w, h in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 4)
                face = img[y : y + h, x : x + w, :]
                face = cv2.resize(face, (50,50))
                face = face.reshape(1,-1)
                face = pca.transform(face)
                pred = svm.predict(face)
                n = names[int(pred)]
                cv2.putText(img, n, (x,y), font, 1, (244, 250, 250), 2)
                print(n)
            cv2.imshow('result',img)
            if cv2.waitKey(2) == 27 :
                break
    capture.release()
    cv2.destroyAllWindows()
    return img,n

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
nr_persoane = 0
img = 0
url = 'http://localhost:5000/mask'
while True: # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        button = 1
        img,n = mask_detection()
        cv2.imwrite('./static/savedimage.jpeg', img)
        if n == "Mask":
            nr_persoane = nr_persoane + 1
        img = open('./static/savedimage.jpeg', 'rb')
        response = requests.post(url, files = {"img": img}, data = {'pers': nr_persoane})     
        print(nr_persoane)
    if GPIO.input(8) == GPIO.HIGH:
        nr_persoane = nr_persoane - 1
        print(nr_persoane)
        time.sleep(1)
        response = requests.post(url, files = {"img": img}, data = {'pers': nr_persoane})  
        
        
        