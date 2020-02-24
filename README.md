## 介绍
这是一个人脸识别后，从信息库中显示相应信息的Qt5 + python的程序，使用现成的face_recognition库作识别人脸。

## 效果
![效果图](https://github.com/peinikanxue/field/blob/master/src/other/face_qt5/effect.gif?raw=true)

## 重新编译
依赖opencv、face_recognition

face_recognition依赖dlib

```bash
sudo apt install cmake
pip install dlib
pip install face_recognition
pip install opencv-python
pip install pyqt5
```

自己编译dlib

```bash
git clone https://github.com/davisking/dlib.git
```
```bash
mkdir build; cd build; cmake .. ; cmake --build .
```
 ```bash
 cd ..; python setup.py install
 ```

## 使用
需要先在known目录下放置已知的人脸图片，图片名为人名信息。
```bash
python face_meeting.py
```

## 打包
ref: https://github.com/ageitgey/face_recognition/issues/357

1. 需要先复制python/lib/python3.6/site-packages/face_recognition_models/到自己的项目目录中
2. 复制.spec文件到自己的项目目录，并修改12,13,46行为自己的项目名
3. python -m PyInstaller face_meeting.spec

(spec: 是一种配置打包的文件，通过pyi-makespec name.py可生成)

## 发布
https://github.com/peinikanxue/field/releases

## 注意
known目录下的图片名，一定要和info_csv目录下的csv里面的数据匹配。

不能出现，刷新图库编码了图片，而csv里面不存在这张图片。


## 参考网址
1. PyQt5入门：https://www.cnblogs.com/archisama/p/5444032.html
2. face_recognition官方教程：https://github.com/ageitgey/face_recognition
3. opencv显示图像中waitKey的作用：https://blog.csdn.net/Du_Shuang/article/details/77836492
4. PyQt显示图片：https://blog.csdn.net/qq_32973061/article/details/81139689
5. PyQt打开子窗口:https://www.cnblogs.com/ansang/p/7895065.html
6. 解决numpy与QPixmap转换:https://blog.csdn.net/weixin_39964552/article/details/82937144
7. PyQt使用pyinstaller打包资源：https://blog.csdn.net/weixin_42296333/article/details/81178915
8. 程序打包问题:https://github.com/ageitgey/face_recognition/issues/357
