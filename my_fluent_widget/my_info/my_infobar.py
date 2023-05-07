# -*- coding: utf-8 -*-

from typing import Literal

# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal
from qfluentwidgets import (InfoBar)
from qfluentwidgets import (MessageBox)
from qfluentwidgets.components.widgets.info_bar import InfoBarPosition


def show_infoBar(parent,   title='', content='', type: Literal['info', 'success', 'warning', 'error'] = 'info', position=InfoBarPosition.TOP, duration=2000, Closable=False):
    method = getattr(InfoBar, type)
    method(
        title=title,
        content=content,
        orient=Qt.Horizontal,
        isClosable=Closable,
        position=position,
        duration=duration,
        parent=parent
    )

class myMessageBox(MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)
        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')

