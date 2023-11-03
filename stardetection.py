import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

class WebcamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initWebcam()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.layout.addWidget(self.label)

    def initWebcam(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Could not open camera.")
            sys.exit()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(20)  # Refresh every 20ms.

    def updateFrame(self):
        ret, frame = self.cap.read()
        if ret:
            detected_frame = self.detectEntities(frame)
            self.displayImage(detected_frame)

    def detectEntities(self, frame):
        # Face Detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # Drawing blue rectangle around detected face
            cv2.putText(frame, "Head", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)  # Add label

        # Star Detection
        blurred = cv2.GaussianBlur(gray_frame, (15, 15), 0)  # Gaussian blur to reduce noise
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_star_area = 10  # Adjust this as per your needs
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_star_area]
        stars = [np.mean(cnt, axis=0)[0] for cnt in contours]
        for star in stars:
            cv2.circle(frame, tuple(star.astype(int)), 3, (0, 255, 0), -1)  # Smaller green circles for stars

        return frame

    def displayImage(self, img):
        qformat = QImage.Format_RGB888
        outImage = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], qformat)
        outImage = outImage.rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(outImage))
        self.label.setScaledContents(True)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebcamApp()
    window.show()
    sys.exit(app.exec_())