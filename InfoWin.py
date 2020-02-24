import pandas as pd
import configparser

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QLabel, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
from PyQt5.QtCore import QCoreApplication, Qt

import resource

class InfoWin(QWidget):
    conf_path = 'setting.ini'
    
    csv_path = './info_csv/info.csv'
    photo_dir = './known/'
    
    def __init__(self):
        super().__init__()

        self._init_conf()
        self._init_var()
        self._init_ui()
    
    def _init_conf(self):
        self.conf = configparser.ConfigParser()
        self.conf.read(self.conf_path)

        self.WIN_WIDTH = int(self.conf['window-info']['width'])
        self.WIN_HEIGHT = int(self.conf['window-info']['height'])
        self.WIN_LEFT = int(self.conf['window-info']['left'])
        self.WIN_TOP = int(self.conf['window-info']['top'])

        self.FONT_SIZE = self.conf['font']['size']
        self.FONT_FAMILY = self.conf['font']['family']
        self.FONT_COLOR = self.conf['font']['color']
        self.FONT_WEIGHT = self.conf['font']['weight']
        
        self.PHOTO_WIDTH = int(self.conf['info']['photo-width'])
        self.PHOTO_HEIGHT = int(self.conf['info']['photo-height'])
        self.CSV_PHOTO_NAME = self.conf['info']['csv-photo-name']
        self.PHOTO_SUFFIX = self.conf['info']['photo-suffix']

        self.SYS_LABEL_TEXT_MAX_NUM = int(self.conf['sys']['label-text-max-num'])
    
    def _init_var(self):
        self.csv = pd.read_csv(self.csv_path)
        self.label_infos = []
        
        self.csv_columns_num = len(self.csv.columns)
    
    def _init_ui(self):
        # 设置窗体
        self.setGeometry(self.WIN_LEFT, self.WIN_TOP, self.WIN_WIDTH, self.WIN_HEIGHT)
        self.setWindowTitle('face')
        self.setWindowIcon(QIcon(':./icon.png'))

        # 窗体居中
        fg = self.frameGeometry()
        dw = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(dw)
        self.move(fg.topLeft())


        # 设置字体
        # Arial
        font_str = 'QLabel{color:' + self.FONT_COLOR + ';font-size:' + self.FONT_SIZE + 'px;font-weight:' + self.FONT_WEIGHT + ';font-family:' + self.FONT_FAMILY + ';}' 
        self.setStyleSheet(font_str)

        # 文本
        for i in range(self.csv_columns_num):
            self.label_infos.append(QLabel(self))

            if self.csv.columns[i] == self.CSV_PHOTO_NAME:  # 单独处理图片
                self.label_infos[-1].move(self.WIN_WIDTH * 0.25, 0)
                self.label_infos[-1].resize(self.PHOTO_WIDTH, self.PHOTO_HEIGHT)
                # self.label_infos[-1].setGeometry(0, 0, 320, 320)
                # self.label_infos[-1].setScaledContents(True)
            else:
                self.label_infos[-1].move(self.WIN_WIDTH * 0.3, (self.WIN_HEIGHT - self.PHOTO_HEIGHT) / self.csv_columns_num * i + self.PHOTO_HEIGHT)
                self.label_infos[-1].setText(' ' * self.SYS_LABEL_TEXT_MAX_NUM)
        
    def set_infos(self, query_name):
        df = self.csv[self.csv[self.CSV_PHOTO_NAME] == query_name]

        for i in range(self.csv_columns_num):
            if df.columns[i] == self.CSV_PHOTO_NAME:    # 单独处理图片
                photo_path = self.photo_dir + df[self.CSV_PHOTO_NAME].iloc[0] + self.PHOTO_SUFFIX
                print(photo_path)

                img = QPixmap(photo_path)
                img = img.scaled(self.PHOTO_WIDTH, self.PHOTO_HEIGHT, aspectRatioMode=Qt.KeepAspectRatio)
                self.label_infos[i].setPixmap(img)
            else:
                txt = str(df.columns[i]) + ':' + str(df[df.columns[i]].iloc[0])
                print(txt)
                self.label_infos[i].setText(txt)


if __name__ == '__main__':
    '''
        打包流程:
        ref: https://github.com/ageitgey/face_recognition/issues/357
        1.需要先复制python/lib/python3.6/site-packages/face_recognition_models/到自己的项目目录中
        2.复制.spec文件到自己的项目目录，并修改12,13,46行为自己的项目名
        3.python -m PyInstaller face_qt5.spec
    '''
    app = QApplication()

    # 创建窗体对象
    mw = InfoWin()

    mw.show()