import os.path
import sys
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtGui import QShowEvent, QCloseEvent, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class CustomWebEnginePage(QWebEnginePage):
    sig_console_message = pyqtSignal(object, object, object, object)

    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, message, line, source):
        self.sig_console_message.emit(level, message, line, source)


class DartCrawlerWindow(QMainWindow):
    _dart_url: str = "https://dart.fss.or.kr/dsae001/main.do"

    def __init__(self):
        super().__init__()
        self._webview = QWebEngineView()
        self._btnStartCrawl = QPushButton('START')
        self._btnGetResult = QPushButton('GET RESULT')
        self._editConsole = QTextEdit()
        self.initControl()
        self.initLayout()

    def initLayout(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        vbox = QVBoxLayout(widget)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)

        subwgt = QWidget()
        subwgt.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout(subwgt)
        hbox.setContentsMargins(2, 4, 2, 0)
        hbox.addWidget(self._btnStartCrawl)
        hbox.addWidget(self._btnGetResult)
        vbox.addWidget(subwgt)
        vbox.addWidget(self._webview)
        vbox.addWidget(self._editConsole)

    def initControl(self):
        self._btnStartCrawl.clicked.connect(self.startCrawl)
        self._btnGetResult.clicked.connect(self.getResult)
        webpage = CustomWebEnginePage(self._webview)
        webpage.sig_console_message.connect(self.onWebPageConsoleMessage)
        self._webview.setPage(webpage)
        self._editConsole.setReadOnly(True)
        self._editConsole.setFixedHeight(100)
        self._editConsole.setLineWrapColumnOrWidth(-1)
        self._editConsole.setLineWrapMode(QTextEdit.FixedPixelWidth)

    def startCrawl(self):
        script_path = os.path.abspath('./run_code.js')
        with open(script_path, 'r', encoding='utf-8') as fp:
            script = fp.read()
            self._editConsole.clear()
            self._webview.page().runJavaScript(script, self.callbackJavascript)

    def getResult(self):
        self._webview.page().runJavaScript("arr_leaf_nodes;", self.callbackResult)

    def showEvent(self, a0: QShowEvent) -> None:
        self._webview.load(QUrl(self._dart_url))

    def closeEvent(self, a0: QCloseEvent) -> None:
        self._webview.close()
        self.deleteLater()

    def addTextMessage(self, message: str):
        cursor = QTextCursor(self._editConsole.textCursor())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(message + '\n')
        vscroll = self._editConsole.verticalScrollBar()
        vscroll.setValue(vscroll.maximum())

    def onWebPageConsoleMessage(self, level, message, line, source):
        text = f'{message} (lv:{level}, line:{line})'
        self.addTextMessage(text)

    def callbackJavascript(self, result: object):
        text = f'>> {result}'
        self.addTextMessage(text)

    def callbackResult(self, result: object):
        if isinstance(result, list):
            # self._editConsole.clear()
            ############################################################################################################
            # for test
            import pickle
            with open('result_list.pkl', 'wb') as fp:
                pickle.dump(result, fp)
            ############################################################################################################

            def parse_dict(obj: dict):
                """
                [dict 구조]
                node_id: str = jstree 노드 아이디
                node_text: str = jstree 노드 텍스트 = 업종분류
                parents: list of dict, dict element = {'id': 노드 아이디, 'text': 노드 텍스트 = 업종분류}
                corp_info_arr: list of dict, dict element = {'name': 기업명, 'code': 기업 고유 번호, 'sector': 업종 id}
                """
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = DartCrawlerWindow()
    wnd.resize(600, 800)
    wnd.show()
    app.exec_()
