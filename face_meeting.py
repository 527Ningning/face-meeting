import sys
import os
import numpy as np
import pickle
from tqdm import tqdm
import configparser

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtCore import QCoreApplication, Qt

import face_recognition
import cv2

from InfoWin import InfoWin

import resource

class CameraWin(QWidget):

    conf_path = 'setting.ini'

    known_path = 'known/'  # 只能在当前目录下
    coding_path = 'coding.pickle'  # 编码数据路径
    tolerance = 0.6
    image_postfix = ['jpg', 'png', 'bmp', 'gif', 'jpeg']

    known_face_encodings = None
    known_face_names = None
    loc_list = []
    label_list = []

    cur_flag = ''
    ignore_frame_counter = 0

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

        self._init_conf()
        self._init_ui()
        self._init_cap()
        self._init_env()

    def _init_conf(self):
        self.conf = configparser.ConfigParser()
        self.conf.read(self.conf_path)

        self.WIN_WIDTH = int(self.conf['window']['width'])
        self.WIN_HEIGHT = int(self.conf['window']['height'])
        self.WIN_LEFT = int(self.conf['window']['left'])
        self.WIN_TOP = int(self.conf['window']['top'])

        self.CAMERA_WIDTH = int(self.conf['camera']['width'])
        self.CAMERA_HEIGHT = int(self.conf['camera']['height'])
        self.RECT_COLOR = eval(self.conf['camera']['rect_color'])
        self.FPS = int(self.conf['camera']['fps'])
        self.DELAY = int(self.conf['camera']['delay'])
        self.IGNORE_FRAME = int(self.conf['camera']['ignore_frame'])


    def _init_ui(self):
        # 设置窗体
        self.setGeometry(self.WIN_LEFT, self.WIN_TOP, self.WIN_WIDTH, self.WIN_HEIGHT)
        self.setWindowTitle('实时')
        self.setWindowIcon(QIcon(':./icon.png'))

        # 功能
        # 按钮
        self.btn_load_image = QPushButton('打开摄像头', self)
        self.btn_load_image.move(self.WIN_WIDTH / 2 - 30, self.WIN_HEIGHT / 4)
        self.btn_load_image.clicked.connect(self.open_camera)
        
        self.btn_info = QPushButton('打开信息板', self)
        self.btn_info.move(self.WIN_WIDTH / 2 - 30, self.WIN_HEIGHT / 4 * 2)

        self.btn_refesh = QPushButton('刷新图库', self)
        self.btn_refesh.move(self.WIN_WIDTH / 2 - 30, self.WIN_HEIGHT / 4 * 3)
        self.btn_refesh.clicked.connect(self.pre_encode)
        
        # 标签
        self.label_msg = QLabel(self)
        self.label_msg.move(0, self.WIN_HEIGHT - 20)
        self.label_msg.setText(' ' * 20)


    def _init_env(self):
        if not os.path.exists(self.known_path):
            os.mkdir(self.known_path.split('/')[-2])

    def _init_cap(self):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, self.FPS)

    def _init_coding(self):
        if self.known_face_encodings is None:
            if os.path.exists(self.coding_path):  # 如果没有加载编码，先加载编码
                self.load_coding()
            else:   # 如果图片没有先编码，就先执行预编码
                self.pre_encode()

    def open_camera(self):
        self._init_coding()

        if self.cap.isOpened():
            while True:
                ret, frame = self.cap.read()

                if self.ignore_frame_counter == self.IGNORE_FRAME:
                    frame = self.process_frame(frame)
                    self.ignore_frame_counter = 0
                self.ignore_frame_counter += 1

                cv2.imshow('capture', frame)

                if cv2.waitKey(self.DELAY) & 0xff == ord('q'):   # read wait frame or exit
                    print('finish')
                    break
        else:
            print('not open camera!')
            self.label_msg.setText('不能打开摄像头!')

        # self.cap.release()    # 不能被释放，否则不能再打开
        cv2.destroyAllWindows()
    
    def process_frame(self, frame):
        # ref: https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]

                if self.cur_flag != name:   # 设置标志，去重
                    iw.set_infos(name)  # 通知InfoWin窗体设置信息
                    self.cur_flag = name

            face_names.append(name)
        
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), self.RECT_COLOR, 2)

            # # Draw a label with a name below the face
            # cv2.rectangle(frame, (left, bottom + 35), (right, bottom), (255, 100, 100), cv2.FILLED)
            # font = cv2.FONT_HERSHEY_DUPLEX
            # cv2.putText(frame, name, (left + 6, bottom + 24), font, 1.0, (255, 255, 255), 1)

        return frame

    
    def pre_encode(self):
        self.known_face_encodings = []
        self.known_face_names = []

        count = len(os.listdir(self.known_path))
        for _, file in zip(tqdm(range(count)), os.listdir(self.known_path)):
            if file.split('.')[-1] in self.image_postfix:
                file_name = self.known_path + file

                known_image = face_recognition.load_image_file(file_name)
                self.known_face_encodings.append(face_recognition.face_encodings(known_image)[0])
                self.known_face_names.append(file.split('.')[0])
        
        self.save_coding()

        print('achvie refresh')
        self.label_msg.setText('完成')

    def save_coding(self):
        if self.known_face_encodings is not None:
            with open(self.coding_path, 'wb') as f:
                coding_dict = {}
                coding_dict['name'] = self.known_face_names
                coding_dict['encoding'] = self.known_face_encodings
                pickle.dump(coding_dict, f)

    def load_coding(self):
        if os.path.exists(self.coding_path):
            with open(self.coding_path, 'rb') as f:
                coding_dict = pickle.load(f)
                self.known_face_names = coding_dict['name']
                self.known_face_encodings = coding_dict['encoding']
        
    
    def closeEvent(self, event):
        sys.exit(0)


if __name__ == '__main__':
    '''
        打包流程:
        ref: https://github.com/ageitgey/face_recognition/issues/357
        1.需要先复制python/lib/python3.6/site-packages/face_recognition_models/到自己的项目目录中
        2.复制.spec文件到自己的项目目录，并修改12,13,46行为自己的项目名
        3.python -m PyInstaller face_qt5.spec
    '''
    app = QApplication(sys.argv)

    # 创建窗体对象
    mw = CameraWin()
    iw = InfoWin()

    mw.btn_info.clicked.connect(iw.show)

    mw.show()
    sys.exit(app.exec_())