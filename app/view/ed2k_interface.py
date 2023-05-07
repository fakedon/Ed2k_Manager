# -*- coding: utf-8 -*-

import os
import pickle
import sqlite3
import sys
from time import sleep

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (ScrollArea, FluentIcon, isDarkTheme, Theme, ToolTipFilter)

from app.common.log import logs
from app.common.my_icons import MyIcon
from app.core.ed2k_decode import convert_bytes
from app.view.custom_view.UI_ed2k_interface import Ui_Form
from my_fluent_widget import show_infoBar
from ..common.config import cfg, FEEDBACK_URL, PyQt_Fluent_Widgets_URL, GITHUB_URL
from ..common.signal_bus import signalBus
from ..common.style_sheet import myStyleSheet


class ed2kInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.adjustTableColumns()

        '''connect signal to slot'''
        self.ui.search_lineEdit.searchSignal.connect(self.search_ed2k)
        self.ui.search_lineEdit.clearSignal.connect(lambda: [self.ui.tableWidget.showRow(
            i) for i in range(self.ui.tableWidget.rowCount())])

        self.ui.treeView.clicked.connect(self.read_txt_to_table)
        self.ui.treeView.editSignal.connect(
            lambda: show_infoBar(self, self.tr('提示'), self.tr('打开成功！')))
        self.ui.treeView.refleshSignal.connect(
            lambda: show_infoBar(self, self.tr('提示'), self.tr('刷新文件列表成功')))

        self.ui.tableWidget.copySignal.connect(self.copy_ed2k)
        self.ui.tableWidget.copySignal.connect(
            lambda: setattr(self, 'ed2k_info_mode', 'dragTable'))
        self.ui.tableWidget.addCompleteSignal.connect(self.adjustTableColumns)
        self.ui.tableWidget.addCompleteSignal.connect(self.set_item_toopTip)

        cfg.themeChanged.connect(self.__setQss)

        '''init widget'''  # //DONE  修正tooltip
        self.ui.change_theme_toolbutton.installEventFilter(
            ToolTipFilter(self.ui.change_theme_toolbutton))
        self.ui.change_theme_toolbutton.setIcon(FluentIcon.CONSTRACT)
        self.ui.change_theme_toolbutton.setToolTip(self.tr('切换主题'))
        self.ui.change_theme_toolbutton.clicked.connect(self.toggleTheme)

        self.ui.feedback_toolbutton.installEventFilter(
            ToolTipFilter(self.ui.feedback_toolbutton))
        self.ui.feedback_toolbutton.setIcon(FluentIcon.FEEDBACK)
        self.ui.feedback_toolbutton.setToolTip(self.tr('提供反馈'))
        self.ui.feedback_toolbutton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

        self.ui.document_pushbutton.setIcon(QIcon(':/gallery/images/logo.png'))
        self.ui.document_pushbutton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(PyQt_Fluent_Widgets_URL)))
        self.ui.document_pushbutton.installEventFilter(ToolTipFilter(
            self.ui.document_pushbutton))
        self.ui.document_pushbutton.setToolTip(self.tr(f'本工具基于此项目'))

        self.ui.github_pushbutton.setIcon(FluentIcon.GITHUB)
        self.ui.github_pushbutton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL)))

        self.ui.database_settings_pushButton.installEventFilter(ToolTipFilter(self.ui.database_settings_pushButton))
        self.ui.database_settings_pushButton.setIcon(MyIcon.DATABASE_SETTING)
        self.ui.database_settings_pushButton.setToolTip(self.tr(f'数据库设置'))
        self.ui.database_settings_pushButton.clicked.connect(
            lambda: signalBus.switchToSampleCard.emit('ed2kInterface', 0))

        self.__getConfig()
        myStyleSheet.ED2K_INTERFACE.apply(self)
        self.__setQss()
        self.last_time()
        self.__setSpacing()

    def last_time(self):
        __path =  os.path.join(os.path.dirname(sys.argv[0]), 'data/.ephemeral')
        if os.path.exists(__path):
            with open(__path, 'rb') as f:
                last__time = pickle.load(f)
                self.ui.fixed_label.setText(
                    self.tr(f'欢迎回来，上次使用时间：') + '\n' + last__time)

    def __getConfig(self):
        self.ui.img_checkBox.toggled.connect(lambda:
                                             cfg.set(cfg.checkImageMode, self.ui.img_checkBox.isChecked()))
        self.ui.deduplicate_checkBox.toggled.connect(lambda:
                                                     cfg.set(cfg.checkDeduplicate,
                                                             self.ui.deduplicate_checkBox.isChecked()))
        self.ui.database_checkBox.toggled.connect(self.read_sqlite
                                                  )

        self.ui.img_checkBox.setChecked(cfg.get(cfg.checkImageMode))
        self.ui.deduplicate_checkBox.setChecked(cfg.get(cfg.checkDeduplicate))
        self.ui.database_checkBox.setChecked(cfg.get(cfg.checkDatabase))

    def search_ed2k(self):
        target = self.ui.search_lineEdit.text()
        # 遍历表格中的所有单元格
        for i in range(self.ui.tableWidget.rowCount()):
            item = self.ui.tableWidget.item(i, 0)
            if target.lower() in item.text().lower():
                # 如果找到匹配的单元格，将其设置为当前单元格
                self.ui.tableWidget.showRow(i)
            else:
                self.ui.tableWidget.hideRow(i)

        n = self.ui.tableWidget.rowCount()
        for i in range(n):
            if self.ui.tableWidget.isRowHidden(i):
                n -= 1
        logs.info(f'搜索 {target} 完成, 包含{n}条结果')
        show_infoBar(self, self.tr(f'搜索完成'), self.tr(
            '包含') + str(n) + self.tr('条结果'), type='success')

    def read_sqlite(self):
        state = self.ui.database_checkBox.isChecked()
        cfg.set(cfg.checkDatabase, state)

        if not state:
            return

        conn = sqlite3.connect( os.path.join(os.path.dirname(sys.argv[0]), 'data/database.db'))

        c = conn.cursor()

        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='local_data'")
        if c.fetchone():
            c.execute('SELECT * FROM local_data')
            data = c.fetchall()
            data_list = [list(row) for row in data]
            self.ui.tableWidget.add_list_data(data_list)

            logs.info(self.tr('连接数据库成功！'))
            show_infoBar(self, self.tr('提示'), self.tr(
                '连接数据库成功！'), type='success')
            logs.info(self.tr('读取数据成功！'))

        else:
            sleep(1)
            logs.info(self.tr('数据库为空，请先扫描数据'))
            show_infoBar(self, self.tr('错误'), self.tr(
                '数据库为空，请先扫描数据'), type='error')

        conn.close()

    def read_txt_to_table(self):

        if self.ui.database_checkBox.isChecked():
            self.ui.database_checkBox.setChecked(False)

        data = self.ui.treeView.data

        if data:
            path = data[0][6]
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.add_list_data(data)
            logs.info(f'文件操作：{path}  完成！')
        else:
            logs.debug(f'读取失败，点击文件夹或发生未知错误')

    def copy_ed2k(self):
        '''copy clicked'''

        clipboard_ed2k_list = []

        # Get the row indices of selected rows
        selected_indexes = self.ui.tableWidget.selectedIndexes()
        selected_rows = list(set(index.row() for index in selected_indexes))
        selected_rows.sort()

        for i in selected_rows:
            ed2k = self.ui.tableWidget.item(i, 5).text()
            clipboard_ed2k_list.append(ed2k)

        text = '\n'.join(clipboard_ed2k_list)
        QApplication.clipboard().setText(text)
        show_infoBar(self, self.tr('提示'), self.tr('复制成功！'))
        logs.info(f'复制内容成功：\n{text}')

    def adjustTableColumns(self):
        hide = [2, 4, 5, 7]
        for i in hide:
            self.ui.tableWidget.hideColumn(i)

        if self.ui.tableWidget.columnWidth(0) < 200:
            self.ui.tableWidget.setColumnWidth(0, 200)
        width = self.ui.tableWidget.columnWidth(0)
        # self.ui.tableWidget.setColumnWidth(0, width * 0.3)
        self.ui.tableWidget.setColumnWidth(1, width * 0.5)
        self.ui.tableWidget.setColumnWidth(6, width * 0.5)

    def set_item_toopTip(self):
        for row in range(self.ui.tableWidget.rowCount()):
            for column in [0, 6]:
                item = self.ui.tableWidget.item(row, column)

                if item:
                    # //DONE  优化样式
                    item.setToolTip(item.text())

        row_number = self.ui.tableWidget.rowCount()
        sum_byte = self.ui.tableWidget.sum_col_numbers(2)
        sum = convert_bytes(sum_byte)

        logs.info(f'计算文件大小：{sum}    字节数：{sum_byte}  ')
        self.ui.label.setText(self.tr('文件数量：') + str(row_number))
        self.ui.label_2.setText(self.tr('文件大小：') + sum)
        self.__setSpacing()

    def toggleTheme(self):
        theme = Theme.LIGHT if isDarkTheme() else Theme.DARK
        cfg.set(cfg.themeMode, theme)

        theme = 'dark' if isDarkTheme() else 'light'
        logs.info(f'切换{theme} 主题成功')
        show_infoBar(self, self.tr('操作成功'), self.tr(
            f'已切换 ') + theme + self.tr(' 主题'), type='success')

        self.__setQss()

    def __setQss(self):
        """ set style sheet """

        if isDarkTheme():
            style = self.ui.tableWidget.styleSheet()
            style += " QToolTip { background-color: #333333; color: white; border: none;font: 13px 'Microsoft YaHei'; font-weight: bold;  }"
        else:
            style = self.ui.tableWidget.styleSheet()
            style += " QToolTip { font: 13px 'Microsoft YaHei'; font-weight: bold; }"
        self.ui.tableWidget.setStyleSheet(style)

    def __setSpacing(self):
        width = self.ui.frame_2.width()

        if width < 215:
            self.ui.fixed_label.setFixedWidth(215)
            return
        self.ui.fixed_label.setFixedWidth(width + 2)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.__setSpacing()
