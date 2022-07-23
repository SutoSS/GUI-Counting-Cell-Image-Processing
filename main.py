import sys
import cv2
from skimage.feature import peak_local_max
from skimage.segmentation import watershed
from scipy import ndimage
import numpy as np
import imutils

btn_down = False

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QLCDNumber
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap

class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("GUI.ui",self)
        self.lcd = QLCDNumber()
        self.browse.clicked.connect(self.browsefiles)
        self.counting.clicked.connect(self.countingfile)

    def browsefiles(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file', 'D:\codefirst.io\PyQt5 tutorials\Browse Files', 'Images (*.png, *.xmp *.jpg *.PNG)')
        self.filename.setText(fname[0])
        imagepath = fname[0]

        image_path = cv2.imread(fname[0])
        gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("images/gray.png", gray)

        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU )[1]
        cv2.imwrite("images/threshold.png", thresh)

        img_mop = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1)))
        img_mop = cv2.morphologyEx(img_mop, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))

        D = ndimage.distance_transform_edt(img_mop)
        localMax = peak_local_max(D, indices=False, min_distance=10, labels=img_mop)
        cv2.imwrite("images/ndimage.png", D)

        markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
        labels = watershed(-D, markers, mask=img_mop)
        print("White Adipose Count: {} ".format(len(np.unique(labels)) -1 ))
        self.filename_3.setText(format(len(np.unique(labels)) -1 ))

        for label in np.unique(labels):
            if label == 255:
                continue
            mask = np.zeros(D.shape, dtype="uint8")
            mask[labels == label] = 255

            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            c = max(cnts, key=cv2.contourArea)

            ((x, y), r) = cv2.minEnclosingCircle(c)
            cv2.circle(image_path, (int(x), int(y)), int(r), (255, 61, 139), 1,5)
            cv2.putText(image_path, "{}".format(label), (int(x) - 4, int(y)), cv2.FONT_HERSHEY_COMPLEX, 0.45, (0,0, 155), 1)

        cv2.imwrite("images/Count_WAT.png", image_path)
        
        Or = imagepath
        gy = 'images/gray.png'
        th = 'images/threshold.png'
        nd = 'images/ndimage.png'
        pixmap = QPixmap(Or)
        self.OR_Image.setPixmap(QPixmap(pixmap))

        pixmap = QPixmap(gy)
        self.GY_Image.setPixmap(QPixmap(pixmap))

        pixmap = QPixmap(th)
        self.TH_Image.setPixmap(QPixmap(pixmap))

        pixmap = QPixmap(nd)
        self.ND_Image.setPixmap(QPixmap(pixmap))

    def countingfile(self):
        image= cv2.imread("images/Count_WAT.png", 1)
        
        def get_points(im):
            # Set up data to send to mouse handler

            data = {}
            data['im'] = im.copy()
            data['lines'] = []

            # Set the callback function for any mouse event
            cv2.imshow("Image", im)
            cv2.setMouseCallback("Image", mouse_handler, data)
            cv2.waitKey(0)

            # Convert array to np.array in shape n,2,2
            points = np.uint16(data['lines'])

            return points, data['im']

        def mouse_handler(event, x, y, flags, data):
            global btn_down

            if event == cv2.EVENT_LBUTTONUP and btn_down:
                #if you release the button, finish the line
                btn_down = False
                data['lines'][0].append((x, y)) #append the second point
                cv2.circle(data['im'], (x, y), 3, (0, 0, 255),5)
                cv2.line(data['im'], data['lines'][0][0], data['lines'][0][1], (0,0,255), 2)
                cv2.imshow("Image", data['im'])

            elif event == cv2.EVENT_MOUSEMOVE and btn_down:
                #this is just for a line visualization
                image = data['im'].copy()
                cv2.line(image, data['lines'][0][0], (x, y), (0,0,255), 1)
                cv2.imshow("Image", image)

            elif event == cv2.EVENT_LBUTTONDOWN and len(data['lines']) < 2:
                btn_down = True
                data['lines'].insert(0,[(x, y)]) #prepend the point
                cv2.circle(data['im'], (x, y), 3, (0, 0, 255), 5, 16)
                cv2.imshow("Image", data['im'])

        pts, final_image = get_points(image)
        data = pts.tolist()
        data1 = data[0]
        data2 = data[1]

        data1_1 = data1[0]
        data1_2 = data1[1]

        data2_1 = data2[0]
        data2_2 = data2[1]

        matriks1_a = data1_1[0]
        matriks1_b = data1_1[1]
        matriks1_c = data1_2[0]
        matriks1_d = data1_2[1]

        matriks2_a = data2_1[0]
        matriks2_b = data2_1[1]
        matriks2_c = data2_2[0]
        matriks2_d = data2_2[1]

        self.lcdNumber.display(matriks1_a)
        self.lcdNumber_2.display(matriks1_b)
        self.lcdNumber_3.display(matriks1_c)
        self.lcdNumber_4.display(matriks1_d)

        self.lcdNumber_7.display(matriks2_a)
        self.lcdNumber_6.display(matriks2_b)
        self.lcdNumber_5.display(matriks2_c)
        self.lcdNumber_8.display(matriks2_d)

        a = np.array([[matriks1_a,matriks1_b],[matriks1_c,matriks1_d]])
        b = np.array([[matriks2_a,matriks2_b],[matriks2_c,matriks2_d]])
        dist = np.linalg.norm(a-b)
        
        self.lcdNumber_9.display(dist)

        cv2.imshow('Image', final_image)
        cv2.imwrite('images\count.png', final_image)
        cv2.waitKey(0)

        final_image='images\count.png'
        pixmap = QPixmap(final_image)
        self.Counting_layer.setPixmap(QPixmap(pixmap))

app=QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(1500)
widget.setFixedHeight(1000)
widget.show()
sys.exit(app.exec_())