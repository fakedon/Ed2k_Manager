# -*- coding: utf-8 -*-


import os

from PyQt5.QtCore import Qt, pyqtSignal, QDir
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QAction
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (RoundMenu,
                            TreeView)

from app.common.log import logs
from app.core.ed2k_decode import txt_to_ed2k_info_list


class myFileTreeView(TreeView):

    refleshSignal = pyqtSignal()
    editSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None

        self.setHeaderHidden(True)
        # self.setFixedWidth(200)

        self.tree_view_model = QFileSystemModel()
        _path = os.path.join(QDir.currentPath(), 'ed2k')
        self.tree_view_model.setRootPath(_path)

        self.setModel(self.tree_view_model)
        self.setRootIndex(
            self.tree_view_model.index(_path))
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.ed2k_tree_menu)

        '''connect signal to slot'''
        self.clicked.connect(self.on_item_clicked)

    def on_item_clicked(self, index):
        '''click txt'''

        self.setExpanded(index,
                         not self.isExpanded(index))

        filepath = self.tree_view_model.filePath(index)
        filename = index.data()

        if filename.endswith('.txt'):
            _, data = txt_to_ed2k_info_list(filepath)
            self.data = data
            logs.info(f'读取文件：{filepath}  成功！')

    def drawBranches(self, painter, rect, index):
        '''adjust file left padding'''
        rect.moveLeft(10)
        return QTreeView.drawBranches(self, painter, rect, index)

    def ed2k_tree_menu(self, pos):
        menu = RoundMenu(parent=self)
        #  add actions
        action = QAction(FIF.EDIT.icon(), self.tr('编辑'))
        action.triggered.connect(self.editSignal.emit)
        action.triggered.connect(self.edit_menu_clicked)
        menu.addAction(action)

        action = QAction(FIF.FOLDER.icon(), self.tr('打开'))
        action.triggered.connect(self.editSignal.emit)
        action.triggered.connect(self.edit_menu_clicked)
        menu.addAction(action)

        action = QAction(FIF.SYNC.icon(), self.tr('刷新'))
        action.triggered.connect(self.refleshSignal.emit)
        menu.addAction(action)

        # show menu
        pos = self.mapToGlobal(pos)
        # pos.setY(pos.y() + 20)
        # pos.setX(pos.x() + 10)
        menu.exec(pos, ani=True)

    def edit_menu_clicked(self):
        index = self.currentIndex()
        filepath = self.tree_view_model.filePath(index)
        os.startfile(filepath)
        logs.info(f'打开：{filepath}')
