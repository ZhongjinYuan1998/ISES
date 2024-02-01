
# 导入需要的包和模块
import sys
import os
import time
import base64
import json
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QDesktopWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
# QDesktopWidget这个库提供了用户的桌面信息,包括屏幕的大小
from PyQt5.QtWidgets import QApplication, QMenu, QMainWindow, QAction, QPushButton, QTabBar, QTabWidget, QInputDialog
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QSplitter, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
# from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap, QImageReader, QImage
from language import lan

from sdk.textClassfication.ALBERTService import ALBERTService
from sdk.preprocess.preprocess_sentences import filter_sentences
from sdk.relationExtraction.relationExtraction import relationExtraction
from Mythread import MyThread

albert_service = ALBERTService()
global editor_list
editor_list = []
global language_tab 
language_tab = "zh"
def analyze_f(text, id):
    # 在这里添加文本分析的逻辑
    # albert_service = ALBERTService()
    # text = text.replace("\n","").split("。")
    mark = ["。", "\r\n", "\n"]
    text = [text]
    for _ in mark:
        text = [s.split(_) for s in text]
        text = [_ for s in text for _ in s if _ != ""]
    print(text)
    relevant_texts = albert_service.get_relevant_sentence_by_albert(text)
    # # relevant_texts = text
    print("relevant_texts",relevant_texts)

    # '''
    #     数据预处理：分句；停用词、无用的状语去除
    # '''
    filter_texts = filter_sentences(relevant_texts)
    print(filter_texts)
        
    # '''
    #     活动图元素及其关系提取
    # '''
    graph = relationExtraction(filter_texts)
    # graph._print()
    filename = str(time.time())
    directory= os.path.join(os.path.dirname(os.path.abspath(__file__)),"result")
    graph.to_plantuml_img(os.path.join(directory,filename+".png"))
    global editor_list
    editor_list[id].viewer.viewer.load_image(os.path.join(directory,filename+".png"))
    return os.path.join(directory,filename+".png")

class CloseableTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()

        self.id = -1
        self.tab_bar = self.tabBar()

    def set_id(self, id):
        self.id = id

    def addTab(self, widget, title):
        index = super().addTab(widget, title)

        close_button = QPushButton('x')
        close_button.setFixedSize(15,15)
        close_button.setStyleSheet("background-color: #b16f7f;color:#ffffff")
        close_button.clicked.connect(lambda: self.close_tab(index))
        self.tab_bar.setTabButton(index, QTabBar.RightSide, close_button)

    def close_tab(self, index):
        self.removeTab(index)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            index = self.tab_bar.tabAt(event.pos())
            if index != -1:
                self.show_context_menu(index)
        
        super().mousePressEvent(event)

    def show_context_menu(self, index):
        global language_tab
        menu = QMenu(self)
        self.rename_action = menu.addAction(lan[language_tab]["rename"])
        self.rename_action.triggered.connect(lambda: self.rename_tab(index))
        menu.exec_(self.tab_bar.mapToGlobal(self.tab_bar.tabRect(index).topRight()))

    def rename_tab(self, index):
        current_title = self.tab_bar.tabText(index)
        new_title, ok_pressed = QInputDialog.getText(self, lan[language_tab]["rename"], lan[language_tab]["new_filename"], QLineEdit.Normal, current_title)
        if ok_pressed and new_title:
            self.setTabText(index, new_title)

class customTextLine(QMainWindow):
    def __init__(self, id):
        super(customTextLine, self).__init__()

        self.id = id
        self.init_ui()
        # self.albert_service = ALBERTService()
        self.thread_pool = QThreadPool.globalInstance()

    def init_ui(self):
        # 创建文本数据框
        self.text_edit = QTextEdit(self)
        # self.text_edit.setPlainText("请输入活动图分析文本")
        font = QFont()
        font.setPointSize(12)  # 设置字体大小
        self.text_edit.setFont(font)

        # 创建“分析”和“清空”按钮
        global language_tab
        self.analyze_button = QPushButton(lan[language_tab]["analyse"], self)
        self.clear_button = QPushButton(lan[language_tab]["clear"], self)
        self.set_button_style(self.analyze_button)
        self.set_button_style(self.clear_button)
        self.analyze_button.setFixedWidth(100)
        self.clear_button.setFixedWidth(100)

        # 连接按钮的槽函数
        self.analyze_button.clicked.connect(self.analyze_text)
        self.clear_button.clicked.connect(self.clear_text)

        # 创建水平布局
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.analyze_button)
        hbox_layout.addWidget(self.clear_button)

        # 创建垂直布局
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.text_edit)
        vbox_layout.addLayout(hbox_layout)

        # 创建主布局
        central_widget = QWidget(self)
        central_widget.setLayout(vbox_layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 400, 300)
        # self.setWindowTitle('文本分析窗口')
        # self.show()
    
    def set_button_style(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #45a049; /* Darker Green */
            }

            QPushButton:pressed {
                background-color: #367d39; /* Even Darker Green */
            }
        """)

        button.setCursor(Qt.PointingHandCursor)  # 添加手型光标

    def analyze_text(self):
        # global editor
        # editor.viewer.viewer.load_image(os.path.join(os.path.dirname(os.path.abspath(__file__)),"0158d05aa1ed29a801206d96a17bd4.jpg"))
        analyze_f(self.text_edit.toPlainText(),self.id)
        # t = MyThread(analyze_f,(self.text_edit.toPlainText(),self.id,))
        # t.start()
        # t.join()
        # img_path = t.get_result()
        # global editor
        # editor.viewer.viewer.load_image(img_path)

    def clear_text(self):
        # 在这里添加清空文本框的逻辑
        self.text_edit.setText("")

class ImageViewer(QGraphicsView):
    def __init__(self):
        super(ImageViewer, self).__init__()

        # 设置场景
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 图片项
        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)

        # 页面大小
        # self.page_width = 800
        # self.page_height = 600

        # 图片拖动相关变量
        self.dragging = False
        self.last_pos = None

        # 缩放比例
        self.scale_factor = 1.0

        # 设置页面大小
        # self.setFixedSize(self.page_width, self.page_height)

        # 添加右键菜单
        global language_tab
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.context_menu = QMenu(self)
        self.save_as_action = QAction(lan[language_tab]["save_as"], self)
        self.save_as_action.triggered.connect(self.save_image_as)
        self.context_menu.addAction(self.save_as_action)

        self.image_path = ""

    def load_image(self, image_path):
        # 加载图片
        self.image_path = image_path
        # image = QPixmap(image_path)
        
        # self.image_item.setPixmap(QPixmap())
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()

        self.load_image_by_binary(image_data)

    def load_image_by_binary(self,image_data):
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)

        self.image_item.setPixmap(pixmap)

        # 调整图片显示位置和大小
        self.image_item.setPos(0, 0)
        self.image_item.setScale(self.scale_factor)
        # self.repaint()

    def wheelEvent(self, event):
        # 处理鼠标滚轮事件，实现图片缩放
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        self.scale_factor *= factor
        self.image_item.setScale(self.scale_factor)

    def mousePressEvent(self, event):
        # 处理鼠标按下事件，记录起始位置
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        # 处理鼠标释放事件，结束拖动
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseMoveEvent(self, event):
        # 处理鼠标移动事件，实现图片拖动
        if self.dragging:
            delta = event.pos() - self.last_pos
            self.image_item.setPos(self.image_item.pos() + delta)
            self.last_pos = event.pos()

    def show_context_menu(self, event):
        # 在右键位置显示上下文菜单
        self.context_menu.exec_(self.mapToGlobal(event))

    def save_image_as(self):
        # 弹出文件对话框，选择保存路径
        global language_tab
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, lan[language_tab]["save_as"], "", "Images (*.png *.jpg *.bmp *.gif);;All Files (*)", options=options)

        # 如果用户选择了路径，保存当前显示的图片
        if file_path:
            image = self.image_item.pixmap().toImage()
            image.save(file_path)

class ImageWindow(QWidget):
    def __init__(self):
        super(ImageWindow, self).__init__()

        # 创建图片显示页面
        self.viewer = ImageViewer()

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.viewer)
        self.setLayout(layout)

class customMainWindow(QMainWindow):
    def __init__(self, id):
        super(customMainWindow, self).__init__()

        self.id = id
        self.init_ui()

    def init_ui(self):
        # 创建文本数据框
        self.text_edit = customTextLine(self.id)

        # # 创建浏览器框
        # browser = QWebEngineView(self)
        # browser.setUrl(QUrl("https://www.baidu.com"))
        self.viewer = ImageWindow()
        # self.viewer.viewer.load_image("activity_diagram.png")

        # 创建一个分割器，使两个部分可以调整大小
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.text_edit)
        splitter.addWidget(self.viewer)

        # 手动设置分割器的大小，确保文本输入框和浏览器框各自占据50%
        sizes = [splitter.size().width() * 0.3, splitter.size().width() * 0.7]
        splitter.setSizes(sizes)

        # 设置主窗口的布局
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(splitter)

        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 800, 600)
        # self.show()

# 创建一个类
class Ex(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "zh"
        self.initUI()
        self.file_index = 1
        
    def initUI(self):
        self.resize(1080,720)
        self.center()
        # 这个方法调用我们下面写的,实现对话框居中的方法
        self.setWindowTitle(lan[self.language]["window_title"])
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)),"logo.png")))

        self.tab_widget = CloseableTabWidget()
        self.setCentralWidget(self.tab_widget)

        #菜单栏
        self.menubar = self.menuBar()
        self.projectMenu = QMenu(lan[self.language]["project"], self)
        # self.helpMenu = QMenu(lan[self.language]["help"], self)
        self.languageMenu = QMenu(lan[self.language]["language"], self)
        self.menubar.addMenu(self.projectMenu)
        # self.menubar.addMenu(self.helpMenu)
        self.menubar.addMenu(self.languageMenu)
        # self.projectMenu = menubar.addMenu(lan[self.language]["project"])
        # self.helpMenu = menubar.addMenu(lan[self.language]["help"])
        # self.languageMenu = menubar.addMenu(lan[self.language]["language"])

        #项目菜单栏
        self.newprojectMenu = QAction(lan[self.language]["new_project"], self)
        # self.recentprojectMenu = QAction(lan[self.language]["recent_project"], self)
        self.importprojectMenu = QAction(lan[self.language]["import_project"], self)
        self.exportprojectMenu = QAction(lan[self.language]["export_project"], self)
        self.projectMenu.addAction(self.newprojectMenu)
        # self.projectMenu.addAction(self.recentprojectMenu)
        self.projectMenu.addAction(self.importprojectMenu)
        self.projectMenu.addAction(self.exportprojectMenu)
        self.newprojectMenu.triggered.connect(self.new_project)
        self.importprojectMenu.triggered.connect(self.import_project)
        self.exportprojectMenu.triggered.connect(self.export_project)

        #帮助菜单栏
        # self.aboutMenu = QAction(lan[self.language]["about"], self)
        # self.usageMenu = QAction(lan[self.language]["usage"], self)
        # self.helpMenu.addAction(self.aboutMenu)
        # self.helpMenu.addAction(self.usageMenu)

        #语言菜单栏
        self.chineseMenu = QAction(lan[self.language]["chinese"], self)
        self.englishMenu = QAction(lan[self.language]["english"], self)
        self.languageMenu.addAction(self.chineseMenu)
        self.languageMenu.addAction(self.englishMenu)
        self.chineseMenu.triggered.connect(lambda: self.setLanguage("zh"))
        self.englishMenu.triggered.connect(lambda: self.setLanguage("en"))

        self.show()

    def setLanguage(self, language):
        self.language = language
        self.setWindowTitle(lan[self.language]["window_title"])
        self.projectMenu.setTitle(lan[self.language]["project"])
        # self.helpMenu.setTitle(lan[self.language]["help"])
        self.languageMenu.setTitle(lan[self.language]["language"])
        self.newprojectMenu.setText(lan[self.language]["new_project"])
        # self.recentprojectMenu.setText(lan[self.language]["recent_project"])
        self.importprojectMenu.setText(lan[self.language]["import_project"])
        self.exportprojectMenu.setText(lan[self.language]["export_project"])
        # self.aboutMenu.setText(lan[self.language]["about"])
        # self.usageMenu.setText(lan[self.language]["usage"])
        self.chineseMenu.setText(lan[self.language]["chinese"])
        self.englishMenu.setText(lan[self.language]["english"])
        global language_tab
        language_tab = language
        global editor_list
        for tab in [self.tab_widget.widget(_) for _ in range(self.tab_widget.count())]:
            editor_list[tab.id].text_edit.analyze_button.setText(lan[language_tab]["analyse"])
            editor_list[tab.id].text_edit.clear_button.setText(lan[language_tab]["clear"])
            editor_list[tab.id].viewer.viewer.save_as_action.setText(lan[language_tab]["save_as"])

    def new_project(self):
        global editor_list
        editor = customMainWindow(len(editor_list))
        editor.text_edit.text_edit.setPlainText(lan[self.language]["text_tip"])
        self.tab_widget.addTab(editor, lan[self.language]["unnamed"] + str(self.file_index))
        self.tab_widget.setCurrentWidget(editor)
        self.tab_widget.set_id(len(editor_list))
        self.file_index += 1
        editor_list.append(editor)

    def import_project(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # 防止使用本地对话框

        file_dialog = QFileDialog()
        file_dialog.setOptions(options)

        # 设置文件对话框的标题和过滤器
        file_dialog.setWindowTitle("Open File")
        file_dialog.setNameFilter("Text Files (*.acg);;All Files (*)")

        # 获取用户选择的文件路径
        file_path, _ = file_dialog.getOpenFileName(self, "Open File", "", "Text Files (*.acg);;All Files (*)")

        if file_path:
            global editor_list
            editor = customMainWindow(len(editor_list))
            self.tab_widget.addTab(editor, os.path.basename(file_path)[:-4])
            self.tab_widget.setCurrentWidget(editor)
            self.tab_widget.set_id(len(editor_list))
            editor_list.append(editor)
            text, img_data = self.load_data_from_file(file_path)
            editor_list[self.tab_widget.id].text_edit.text_edit.setText(text)
            editor_list[self.tab_widget.id].viewer.viewer.load_image_by_binary(img_data)

    def export_project(self):
        currentIndex = self.tab_widget.currentIndex()
        if currentIndex == -1:
            # QMessageBox.warning(self, '警告', '请先新建项目', QMessageBox.Ok)
            return 
        filename = self.tab_widget.tabText(currentIndex)
        # print(filename)
        # print(currentIndex)
        global editor_list
        text = editor_list[self.tab_widget.id].text_edit.text_edit.toPlainText()
        # print(text)
        img_path = editor_list[self.tab_widget.id].viewer.viewer.image_path

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog  # 防止使用本地对话框

        file_dialog = QFileDialog()
        file_dialog.setOptions(options)

        # 设置文件对话框的标题和过滤器
        file_dialog.setWindowTitle("Save File")
        file_dialog.setNameFilter("Text Files (*.acg);;All Files (*)")

        # 获取用户选择的文件路径
        file_path, _ = file_dialog.getSaveFileName(self, "Save File", filename, "Text Files (*.acg);;All Files (*)")

        if file_path:
            self.save_data_to_file(text,img_path,file_path)
    
    def save_data_to_file(self, text_data, image_path, output_file):
        # 读取图像文件
        with open(image_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # 组合文本和图像数据
        data_to_save = {
            'text_data': text_data,
            'image_data': image_data
        }

        # 将数据写入文件
        with open(output_file, 'w') as file:
            json.dump(data_to_save, file)

    def load_data_from_file(self,input_file):
        # 从文件加载数据
        with open(input_file, 'r') as file:
            data = json.load(file)

        # 解析文本和图像数据
        text_data = data['text_data']
        image_data = base64.b64decode(data['image_data'])

        return text_data, image_data

    def center(self):
        qr = self.frameGeometry()
        # 得到了主窗口大小
        # print('qr:',qr)
        cp = QDesktopWidget().availableGeometry().center()
        # 获取显示器的分辨率,然后得到中间点的位置
        # print('cp:',cp)
        qr.moveCenter(cp)
        # 然后把自己的窗口的中心点放到qr的中心点
        self.move(qr.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo1 = Ex()
    sys.exit(app.exec_())
