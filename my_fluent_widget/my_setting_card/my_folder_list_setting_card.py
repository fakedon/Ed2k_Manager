# coding:utf-8
from pathlib import Path
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QPushButton, QFileDialog, QWidget, QLabel,
                             QHBoxLayout, QToolButton)
from qfluentwidgets import ConfigItem, qconfig
from qfluentwidgets import Dialog
from qfluentwidgets import ExpandSettingCard
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import drawIcon


class ToolButton(QToolButton):
    """ Tool button """

    def __init__(self, icon, size: tuple, iconSize: tuple, parent=None):
        super().__init__(parent=parent)
        self.isPressed = False
        self._icon = icon
        self._iconSize = iconSize
        self.setFixedSize(*size)

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setOpacity(0.63 if self.isPressed else 1)
        w, h = self._iconSize
        drawIcon(self._icon, painter, QRectF(
            (self.width()-w)/2, (self.height()-h)/2, w, h))


class PushButton(QPushButton):
    """ Push button """

    def __init__(self, icon, text: str, parent=None):
        super().__init__(parent=parent)
        self.isPressed = False
        self._icon = icon
        self.setText(text)

    def mousePressEvent(self, e):
        self.isPressed = True
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setOpacity(0.63 if self.isPressed else 1)
        drawIcon(self._icon, painter, QRectF(12, 8, 16, 16))


class FolderItem(QWidget):
    """ Folder item """

    removed = pyqtSignal(QWidget)

    def __init__(self, folder: str, parent=None):
        super().__init__(parent=parent)
        self.folder = folder
        self.hBoxLayout = QHBoxLayout(self)
        self.folderLabel = QLabel(folder, self)
        self.removeButton = ToolButton(FIF.CLOSE, (39, 29), (12, 12), self)

        self.setFixedHeight(53)
        self.hBoxLayout.setContentsMargins(48, 0, 60, 0)
        self.hBoxLayout.addWidget(self.folderLabel, 0, Qt.AlignLeft)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.removeButton, 0, Qt.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignVCenter)

        self.removeButton.clicked.connect(
            lambda: self.removed.emit(self))


class myFolderListSettingCard(ExpandSettingCard):
    """ Folder list setting card """

    folderChanged = pyqtSignal(list)

    def __init__(self, configItem: ConfigItem, title: str, content: str = None, directory="./", parent=None):
        """
        Parameters
        ----------
        configItem: RangeConfigItem
            configuration item operated by the card

        title: str
            the title of card

        content: str
            the content of card

        directory: str
            working directory of file dialog

        parent: QWidget
            parent widget
        """
        super().__init__(FIF.FOLDER, title, content, parent)
        self.configItem = configItem
        self._dialogDirectory = directory
        self.addFolderButton = PushButton(
            FIF.FOLDER_ADD, self.tr('添加文件夹'), self)

        self.folders = qconfig.get(configItem).copy()   # type:List[str]
        self.__initWidget()

    def __initWidget(self):
        self.addWidget(self.addFolderButton)

        # initialize layout
        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        for folder in self.folders:
            self.__addFolderItem(folder)

        self.addFolderButton.clicked.connect(self.__showFolderDialog)

    def __showFolderDialog(self):
        """ show folder dialog """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("选择文件夹"), self._dialogDirectory)

        if not folder or folder in self.folders:
            return

        self.__addFolderItem(folder)
        self.folders.append(folder)
        qconfig.set(self.configItem, self.folders)
        self.folderChanged.emit(self.folders)

    def __addFolderItem(self, folder: str):
        """ add folder item """
        item = FolderItem(folder, self.view)
        item.removed.connect(self.__showConfirmDialog)
        self.viewLayout.addWidget(item)
        self._adjustViewSize()

    def __showConfirmDialog(self, item: FolderItem):
        """ show confirm dialog """
        name = Path(item.folder).name
        title = self.tr('是否确认删除此文件夹?')
        content = self.tr("如果将 ") + f'"{name}"' + \
            self.tr(" 文件夹从列表中移除 "
                    "则该文件夹不会再出现在列表中，但不会被删除。")
        w = Dialog(title, content, self.window())
        w.yesButton.setText(self.tr(f'确认'))
        w.cancelButton.setText(self.tr(f'取消'))
        w.yesSignal.connect(lambda: self.__removeFolder(item))
        w.exec_()


    def __removeFolder(self, item: FolderItem):
        """ remove folder """
        if item.folder not in self.folders:
            return

        self.folders.remove(item.folder)
        self.viewLayout.deleteWidget(item)
        self._adjustViewSize()

        self.folderChanged.emit(self.folders)
        qconfig.set(self.configItem, self.folders)
