from PyQt5.QtWidgets import QApplication,QMainWindow,QLabel,QCheckBox,QVBoxLayout, QDialog,QTextEdit,QHBoxLayout,QGroupBox, QPushButton, QFileDialog, QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap, QResizeEvent, QPainter, QPen, QIcon, QDesktopServices
from PyQt5.QtCore import Qt,QUrl
from paddleocr import PaddleOCR
import sys

class MainWindow(QMainWindow):
    file_path = None
    def __init__(self):
        super().__init__()
        # 标题图标和窗口大小
        self.setFixedSize(1200, 700)
        self.setWindowTitle("GarfieldGod's OCR")
        self.setWindowIcon(QIcon("ico.ico"))
        # 窗口置中
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.space_label = QLabel()
# 结果区---------------------------------------------------------------------------------------------
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(550, 500)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.result_label = QTextEdit(self)
        self.result_label.setAlignment(Qt.AlignLeft)
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.result_label.setFixedSize(550, 500)
        self.result_label.setStyleSheet("border: 1px solid black;")
# 功能区---------------------------------------------------------------------------------------------
        self.open_button = QPushButton("打开图片")
        self.open_button.clicked.connect(self.open_image)

        self.reocr_button = QPushButton("识别")
        self.reocr_button.clicked.connect(self.myocr)

        self.viewimage_button = QPushButton("查看原图")
        self.viewimage_button.clicked.connect(self.view_image)

        self.info_button = QPushButton("关于")
        self.info_button.clicked.connect(self.info_window)

        self.checkbox_imageline = QCheckBox("框选图片中的文字区域")
        self.checkbox_imageline.setChecked(True)
        self.checkbox_Textline = QCheckBox("在识别结果中显示文本标记")

# 布局区---------------------------------------------------------------------------------------------
        # 功能
        Function = QGroupBox("功能")
        Blayout = QHBoxLayout()
        Blayout.addWidget(self.open_button)
        Blayout.addWidget(self.reocr_button)
        Blayout.addWidget(self.viewimage_button)
        Blayout.addWidget(self.info_button)
        Function.setLayout(Blayout)
        # 设置
        Option = QGroupBox("设置")
        Olayout = QHBoxLayout()
        Olayout.addWidget(self.space_label)
        Olayout.addWidget(self.checkbox_imageline)
        Olayout.addWidget(self.space_label)
        Olayout.addWidget(self.space_label)
        Olayout.addWidget(self.checkbox_Textline)
        Olayout.addWidget(self.space_label)
        Option.setLayout(Olayout)
        # 识别
        UI = QGroupBox("识别结果")
        uLayout = QHBoxLayout()
        uLayout.addWidget(self.image_label)
        uLayout.addWidget(self.result_label)
        UI.setLayout(uLayout)
        # 全局
        ALLBox = QVBoxLayout()
        ALLBox.addWidget(Function)
        ALLBox.addWidget(Option)
        ALLBox.addWidget(UI)
        central_widget = QWidget()
        central_widget.setLayout(ALLBox)
        self.setCentralWidget(central_widget)
# OCR区---------------------------------------------------------------------------------------------
        # 初始化 PaddleOCR
        self.ocr = PaddleOCR(use_gpu=False)
        det_model_path = 'mydet.pdiparams'  # 文字检测模型路径
        rec_model_path = 'cls.pdiparams'  # 文字识别模型路径
        self.ocr.det_model_dir = det_model_path  # 设置文字检测模型路径
        self.ocr.rec_model_dir = rec_model_path  # 设置文字识别模型路径

    def info_window(self):
        self.window_info = Info()
        self.window_info.show()
    def view_image(self):
        if MainWindow.file_path:
            self.new_window = ShowOriginalImage()
            self.new_window.show()
            self.new_window.get_pixmap(self.pixmap)
        else:
            self.show_message_box("请先打开图片文件!")

    def open_image(self):
        file_dialog = QFileDialog()
        MainWindow.file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.bmp)")
        if MainWindow.file_path:
            self.result_label.setText("")
            self.pixmap = QPixmap(MainWindow.file_path)
            scaled_pixmap = self.pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)

    def myocr(self):
        if MainWindow.file_path:
            self.result_label.setText("")
            self.pixmap = QPixmap(MainWindow.file_path)
            result = self.ocr.ocr(MainWindow.file_path)
            text = "\n"
            for i in result[0]:
                print(i)
                print("\n")
            if result[0] != None:
                i = 0
                goal = 0
                for line in result[0]:
                    i += 1
                    goal += line[1][1]
                    if self.checkbox_imageline.isChecked():
                        self.drawBox(line[0])
                    if self.checkbox_Textline.isChecked():
                        text += " 【Line:" + str(i) + "】\t" + str(line[1][0]) + "\n"
                    else:
                        text += " " + str(line[1][0]) + "\n"
                self.result_label.setText(text)
                scaled_pixmap = self.pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
                self.show_message_box("识别成功，正确率" + str(round(goal / i *100, 1))+"%!")
            else:
                scaled_pixmap = self.pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
                self.image_label.setPixmap(scaled_pixmap)
                self.show_message_box("未识别到文字信息!")
        else:
            self.show_message_box("请先打开图片文件!")

    def show_message_box(self,text):
        self.message_window = message_box()
        self.message_window.show()
        self.message_window.set_text(text)

    def drawBox(self, coordinates):
        drawBox = QPainter(self.pixmap)
        drawBox.setPen(QPen(Qt.red, 2))  # 设置画笔颜色和线宽

        # 绘制边框
        for i in range(len(coordinates)):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[(i + 1) % len(coordinates)]
            drawBox.drawLine(x1, y1, x2, y2)

        drawBox.end()

    def resizeEvent(self, event: QResizeEvent):
        if not self.image_label.pixmap():
            return

        pixmap = self.image_label.pixmap()
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)

        super().resizeEvent(event)

class ShowOriginalImage(QMainWindow):
    def __init__(self):
        super().__init__()
        # 标题和图标
        self.setWindowTitle("GarfieldGod's OCR")
        self.setWindowIcon(QIcon("ico.ico"))

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.image_label)
    def get_pixmap(self, pixmap):
        self.image_label.setPixmap(pixmap)
        self.setFixedSize(pixmap.size())
        # 窗口置中
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - pixmap.size().width()) // 2
        y = (screen_geometry.height() - pixmap.size().height()) // 2
        self.move(x, y)


class Info(QDialog):
    def __init__(self):
        super().__init__()
        # 窗口置为顶级
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.WindowStaysOnTopHint)
        # 标题图标和窗口大小
        self.setFixedSize(400, 600)
        self.setWindowTitle("GarfieldGod's OCR")
        self.setWindowIcon(QIcon("ico.ico"))
        # 窗口置中
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.button = QPushButton("访问官网")
        self.button.clicked.connect(self.open_webpage)

        self.infomation = "欢迎使用GarfieldGod's OCR! \n\n本软件使用PaddleOCR和PyQT5制作。 \n\n更多信息及源码请访问我的个人主页！ \n\n ---------2024年4月24日\n\n\n\n作者：GarfieldGod \n\n主页：garfieldgod.cn"
        self.label = QLabel(self.infomation)
        self.label.setAlignment(Qt.AlignCenter)

        self.slabel = QLabel("")
        self.slabel.setAlignment(Qt.AlignCenter)

        self.IconLabel = QLabel()

        self.IconLabel.setAlignment(Qt.AlignCenter)
        self.IconLabel.setFixedSize(250, 250)

        image_path = "IndexCover.png"
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.IconLabel.size(), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)

        self.IconLabel.setPixmap(scaled_pixmap)
        self.IconLabel.setScaledContents(True)
        self.IconLabel.setStyleSheet("QLabel { border-radius: 0px; border: 2px solid black; }")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.IconLabel)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slabel)
        self.layout.addWidget(self.button)
        self.layout.setAlignment(Qt.AlignCenter)

        self.setLayout(self.layout)
    def open_webpage(self):
        url = QUrl("https://garfieldgod.cn/")
        QDesktopServices.openUrl(url)
        self.close()

class message_box(QDialog):
    def __init__(self):
        super().__init__()
        # 窗口置为顶级
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.WindowStaysOnTopHint)
        # 标题图标和窗口大小
        self.setFixedSize(200, 100)
        self.setWindowTitle("God：")
        self.setWindowIcon(QIcon("ico.ico"))
        # 窗口置中
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.button = QPushButton("确定")
        self.button.clicked.connect(self.click_ok)
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.slabel = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.slabel)
        self.layout.addWidget(self.button)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
    def set_text(self,text):
        self.label.setText(text)
    def click_ok(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())