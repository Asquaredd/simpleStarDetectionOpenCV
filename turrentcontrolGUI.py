import os
import sys
import cv2
import mediapipe as mp
import serial
from PySide6.QtWidgets import QApplication, QFrame, QMainWindow, QLabel, QVBoxLayout,QHBoxLayout,QMessageBox, QWidget
from PySide6.QtCore import QTimer, Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPolygon, QImage, QPixmap, QAction


#Widget for Control Panel
class GamepadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

    def set_key_press(self, key, pressed):
        if key == Qt.Key_Up:
            self.up_pressed = pressed
        elif key == Qt.Key_Down:
            self.down_pressed = pressed
        elif key == Qt.Key_Left:
            self.left_pressed = pressed
        elif key == Qt.Key_Right:
            self.right_pressed = pressed
        self.update()  # Redraw the widget
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a semi-transparent circle around the whole gamepad
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 128))
        painter.drawEllipse(0, 0, 100, 100)

        painter.setPen(Qt.black)
        painter.setBrush(Qt.black)

        # Draw buttons according to their status
        if self.up_pressed:
            triangle = QPolygon([QPoint(50, 0), QPoint(100, 50), QPoint(0, 50)])
            painter.drawPolygon(triangle)
        if self.down_pressed:
            triangle = QPolygon([QPoint(0, 50), QPoint(100, 50), QPoint(50, 100)])
            painter.drawPolygon(triangle)
        if self.left_pressed:
            triangle = QPolygon([QPoint(0, 50), QPoint(50, 0), QPoint(50, 100)])
            painter.drawPolygon(triangle)
        if self.right_pressed:
            triangle = QPolygon([QPoint(100, 50), QPoint(50, 0), QPoint(50, 100)])
            painter.drawPolygon(triangle)

        painter.end()


#Main Window PySide6
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Servo Control with Webcam and Gamepad")
        self.setGeometry(100, 100, 960, 540)

        self.setupMenuBar()  # Setup the menu bar

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setupWebcamLabel()
        self.setupSidebar()

        ###self.initializeSerialConnection()###
        self.initializeWebcam()
        
        self.set_styles()

    def setupMenuBar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        view_menu = menu_bar.addMenu("&View")
        tool_menu = menu_bar.addMenu("&Tool")

        dark_mode_action = QAction("Dark Mode", self, checkable=True)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(dark_mode_action)

        show_dir_action = QAction("Show Current Directory", self)
        show_dir_action.triggered.connect(self.show_current_directory)
        file_menu.addAction(show_dir_action)

        calibrate_action = QAction("Calibrate", self)
        calibrate_action.triggered.connect(self.calibrate_function_placeholder)
        tool_menu.addAction(calibrate_action)



    def setupWebcamLabel(self):
        # Container for the webcam and its label
        self.webcam_container = QWidget()
        webcam_layout = QVBoxLayout(self.webcam_container)
        
        self.webcam_label_title = QLabel("Camera Window")
        self.webcam_label_title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        webcam_layout.addWidget(self.webcam_label_title)

        self.webcam_label = QLabel("Webcam feed here")
        self.webcam_label.setFixedSize(640, 480)
        webcam_layout.addWidget(self.webcam_label)

        self.main_layout.addWidget(self.webcam_container)
    
    def setupSidebar(self):
        self.sidebar_container = QFrame()
        self.sidebar_layout = QVBoxLayout(self.sidebar_container)
        self.sidebar_layout.setAlignment(Qt.AlignCenter)  # Center align the sidebar contents

        # Coordinate labels with enhanced styling
        self.servo1_angle = 90
        self.servo1_label = QLabel(f"Servo 1 Position: {self.servo1_angle}")
        self.servo1_label.setStyleSheet(self.get_servo_label_style())
        self.sidebar_layout.addWidget(self.servo1_label)

        self.servo2_pulse = 1500
        self.servo2_label = QLabel(f"Servo 2 Position: {self.servo2_pulse}")
        self.servo2_label.setStyleSheet(self.get_servo_label_style())
        self.sidebar_layout.addWidget(self.servo2_label)


        self.gamepad = GamepadWidget()
        self.gamepad.setFixedSize(100, 100)
        self.sidebar_layout.addWidget(self.gamepad)

        self.main_layout.addWidget(self.sidebar_container)
    
    def get_servo_label_style(self):
        # Define the CSS style for servo labels
        return """
            QLabel {
                font: bold 14px;
                color: #444;
                border: 1px solid #888;
                padding: 5px;
                border-radius: 4px;
                background-color: #EEE;
            }
        """
    
    
    """def initializeSerialConnection(self):
        self.ser = serial.Serial('COM6', 9600, timeout=1)"""

    def initializeWebcam(self):
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_webcam)
        self.timer.start(30)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    def set_styles(self):
        # Set styles for the application
        self.webcam_label.setStyleSheet("border: 5px solid black;")
        
        # Apply styles to the sidebar container
        self.sidebar_container.setStyleSheet(
            "background-color: rgba(255, 0, 0, 0.5);"
            "border: 1px solid gray;"
        )
        
        
    def toggle_dark_mode(self, checked):
        if checked:
            self.setStyleSheet("background-color: #333; color: #DDD;")
            self.sidebar_layout.setStyleSheet("background-color: rgba(50, 50, 50, 0.5); border: 1px solid gray;")
        else:
            self.setStyleSheet("")
            self.sidebar_layout.setStyleSheet("background-color: rgba(200, 200, 200, 0.5); border: 1px solid gray;")

    
    def show_current_directory(self):
        current_dir = os.getcwd()
        QMessageBox.information(self, "Current Directory", f"You are in: {current_dir}")

    def calibrate_function_placeholder(self):
        # Placeholder function for calibration
        QMessageBox.information(self, "Calibrate", "Calibration functionality will be implemented here.")

    
    
    def update_webcam(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame.flags.writeable = False  # Optimization

            # Hand detection
            hand_results = self.hands.process(frame)
            # Face detection
            face_results = self.face_detection.process(frame)


            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Draw hand landmarks and labels
            if hand_results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
                    # Draw landmarks
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    # Label each hand as 'Left' or 'Right'
                    label = handedness.classification[0].label
                    hand_coords = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
                    cv2.putText(frame, label, (int(hand_coords.x * frame.shape[1]), int(hand_coords.y * frame.shape[0])), 
                                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)

            if face_results.detections:
                for detection in face_results.detections:
                    # Get bounding box coordinates
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                    # Draw rectangle (bounding box) around the face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Draw label
                    cv2.putText(frame, 'Head', (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 255, 0), 1)

            
            # Display the image
            qImg = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            self.webcam_label.setPixmap(QPixmap.fromImage(qImg))

    def keyPressEvent(self, event):
        self.gamepad.set_key_press(event.key(), True)

        if event.key() == Qt.Key_Up:
            self.servo1_angle = min(180, self.servo1_angle + 10)
            self.servo1_label.setText(f"Servo 1 Position: {self.servo1_angle}")
            self.send_servo_command(1, self.servo1_angle)

        elif event.key() == Qt.Key_Down:
            self.servo1_angle = max(0, self.servo1_angle - 10)
            self.servo1_label.setText(f"Servo 1 Position: {self.servo1_angle}")
            self.send_servo_command(1, self.servo1_angle)

        elif event.key() == Qt.Key_Left:
            self.servo2_pulse = 1540
            self.servo2_label.setText("Servo 2 Position: 1540")
            self.send_servo_command(2, self.servo2_pulse)

        elif event.key() == Qt.Key_Right:
            self.servo2_pulse = 1470
            self.servo2_label.setText("Servo 2 Position: 1470")
            self.send_servo_command(2, self.servo2_pulse)

    def keyReleaseEvent(self, event):
        self.gamepad.set_key_press(event.key(), False)
        if event.key() in [Qt.Key_Left, Qt.Key_Right]:
            self.servo2_pulse = 1500
            self.servo2_label.setText("Servo 2 Position: 1500")
            self.send_servo_command(2, self.servo2_pulse)

    def send_servo_command(self, servo_id, value):
         """command = f"{servo_id} {value}\n".encode()
        self.ser.write(command)"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
