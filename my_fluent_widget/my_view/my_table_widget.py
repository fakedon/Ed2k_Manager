# -*- coding: utf-8 -*-

import os
import shutil

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QAction
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (TableWidget,
                            RoundMenu)

from app.common.log import logs
from app.core.ed2k_decode import txt_to_ed2k_info_list


class myTableWidget(TableWidget):

    copySignal = pyqtSignal()
    addCompleteSignal=pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # read only
        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers)

        self.setAcceptDrops(True)

        '''connet signal to slot'''

        '''right click menu'''
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.ed2k_table_menu)

    def add_list_data(self, data: list):
        self.setRowCount(len(data))

        for row in range(len(data)):
            for column in range(len(data[row])):
                self.setItem(
                    row, column, QTableWidgetItem(str(data[row][column])))
        logs.info('添加数据至表格成功')
        
        self.addCompleteSignal.emit()       

    def dragEnterEvent(self, e):
        if not e.mimeData().hasUrls():
            return
        file: str = e.mimeData().urls()[0].toLocalFile()
        file.replace('\\', '/')
        name = os.path.basename(file)

        if file.endswith('.txt'):
            filepath = os.path.abspath(os.path.join('ed2k', name))

            if not os.path.exists(filepath):
                shutil.copy(file, 'ed2k')
                logs.info(f'复制文件到：{filepath}  成功！')
            else:
                logs.info(f'文件：{filepath}  已存在，不再复制')
            _, data = txt_to_ed2k_info_list(filepath)
            logs.info(f'读取文件：{filepath}  成功！')

            # data = [[info['filename'], info['extension'],
            #          info['size'], info['path']] for info in data]
            self.add_list_data(data)

    def ed2k_table_menu(self, pos):
        menu = RoundMenu(parent=self)
        #  add actions
        action = QAction(FIF.EDIT.icon(), self.tr('复制'))
        action.triggered.connect(self.copySignal.emit)
        menu.addAction(action)

        action = QAction(FIF.FOLDER.icon(), self.tr('全选'))
        action.triggered.connect(self.select_all)
        menu.addAction(action)

        # show menu
        pos = self.mapToGlobal(pos)
        pos.setY(pos.y() + 40)
        pos.setX(pos.x() + 5)
        menu.exec(pos, ani=True)

    def select_all(self):

        # create a key press event for Ctrl+A
        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_A, Qt.ControlModifier)
        # send the event to the QLineEdit widget
        QCoreApplication.postEvent(self, event)

    def sum_col_numbers(self, col):
        sum = 0
        for row in range(self.rowCount()):
            item = self.item(row, col)
            if item:
              sum += int(item.text())

        return sum
