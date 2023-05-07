# coding:utf-8
import csv
import os
import sqlite3
import sys
from datetime import datetime

from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from qfluentwidgets import (SettingCardGroup, OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, setTheme, setThemeColor, RangeSettingCard)

from app.common.log import logs
from app.core.ed2k_decode import ed2k_infos_to_db, get_txt_files, txt_to_ed2k_info_list
from my_fluent_widget import myFolderListSettingCard, myCustomColorSettingCard, \
    mySwitchSettingCard, myMessageBox
from my_fluent_widget import show_infoBar
from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, SQLITESUDIO_URL
from ..common.my_icons import MyIcon
from ..common.style_sheet import StyleSheet

from  app.resource import  resouce_rc

class SettingInterface(ScrollArea):
    """ Setting interface """

    checkUpdateSig = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel(self.tr("设置"), self)

        # music folders
        self.databaseSettingGroup = SettingCardGroup(
            self.tr("数据库"), self.scrollWidget)
        self.scanFolderCard = myFolderListSettingCard(
            cfg.scanFolders,
            self.tr("扫描路径"),
            self.tr(f'设置扫描 ed2k 文件夹'),
            parent=self.databaseSettingGroup
        )
        self.saveFolderCard = PushSettingCard(
            self.tr('选择文件夹'),
            FIF.SAVE,
            self.tr("保存目录"),
            self.tr(f'数据库保存目录，暂时固定为 data 文件夹，更改无效'),
            self.databaseSettingGroup
        )

        # //DONE set icon
        self.scanCard = PushSettingCard(
            self.tr('扫描'),
            FIF.SYNC,
            self.tr("扫描"),
            self.tr(f'从文件夹中扫描 ed2k 链接导入数据库中'),
            self.databaseSettingGroup
        )

        self.cleanCard = PushSettingCard(
            self.tr('整理'),
            MyIcon.CLEAR,
            self.tr("整理"),
            self.tr(f'清理无效数据，释放存储空间'),
            self.databaseSettingGroup
        )

        self.resetCard = PushSettingCard(
            self.tr('重置'),
            FIF.HISTORY,
            self.tr("重置"),
            self.tr(f'初始化数据库，将会清空所有数据'),
            self.databaseSettingGroup
        )

        self.exportCard = PushSettingCard(
            self.tr('导出'),
            FIF.EMBED,
            self.tr("导出"),
            self.tr(f'导出数据库内 ed2k 为 txt 和 csv  '),
            self.databaseSettingGroup
        )

        # self.quadButtonCard = quadButtonsSettingCard(
        #     self.tr(f'扫描数据库'), self.tr(f'整理数据库'), self.tr(f'重置数据库'), self.tr(f'导出数据库'))

        self.sqlitestudioCard = HyperlinkCard(
            SQLITESUDIO_URL,
            self.tr('前往获取'),
            FIF.TRANSPARENT,
            self.tr('高级操作'),
            self.tr(
                '获取 SQLiteStudio ，可视化管理您的数据库'),
            self.databaseSettingGroup
        )

        # personalization
        self.personalGroup = SettingCardGroup(
            self.tr('个性化'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('应用主题'),
            self.tr("调整你的应用的外观"),
            texts=[
                self.tr('浅色'), self.tr('深色'),
                self.tr('跟随系统设置')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = myCustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('主题色'),
            self.tr('调整你的应用的主题色'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("界面缩放"),
            self.tr("调整小部件和字体的大小"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("跟随系统设置")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('语言'),
            self.tr('选择界面所使用的语言'),
            texts=['简体中文', '繁體中文', 'English', self.tr('跟随系统设置')],
            parent=self.personalGroup
        )

        # material
        self.materialGroup = SettingCardGroup(
            self.tr('材料'), self.scrollWidget)
        self.blurRadiusCard = RangeSettingCard(
            cfg.blurRadius,
            FIF.ALBUM,
            self.tr('亚克力磨砂半径'),
            self.tr('磨砂半径越大，图像越模糊'),
            self.materialGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(
            self.tr("软件更新"), self.scrollWidget)
        self.updateOnStartUpCard = mySwitchSettingCard(
            FIF.UPDATE,
            self.tr('在应用程序启动时检查更新'),
            self.tr('新版本将更加稳定并拥有更多功能（建议启用此选项）'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('关于'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('打开帮助页面'),
            FIF.HELP,
            self.tr('帮助'),
            self.tr(
                '发现新功能并了解有关 Ed2k Manager 的使用技巧'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('提供反馈'),
            FIF.FEEDBACK,
            self.tr('提供反馈'),
            self.tr('通过提供反馈帮助我们改进 Ed2k Manager'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('检查更新'),
            FIF.INFO,
            self.tr('关于'),
            '© ' + self.tr('作者') + f" {YEAR}, {AUTHOR}. " +
            self.tr('当前版本') + f" {VERSION[1:]}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        self.updateOnStartUpCard.switchButton.setEnabled(False)
        self.aboutCard.button.setEnabled(False)

        StyleSheet.SETTING_INTERFACE.apply(self)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # add cards to group
        self.databaseSettingGroup.addSettingCard(self.scanFolderCard)
        self.databaseSettingGroup.addSettingCard(self.saveFolderCard)
        self.databaseSettingGroup.addSettingCard(self.scanCard)
        self.databaseSettingGroup.addSettingCard(self.cleanCard)
        self.databaseSettingGroup.addSettingCard(self.resetCard)
        self.databaseSettingGroup.addSettingCard(self.exportCard)
        # self.databaseSettingGroup.addSettingCard(self.quadButtonCard)
        self.databaseSettingGroup.addSettingCard(self.sqlitestudioCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.materialGroup.addSettingCard(self.blurRadiusCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.databaseSettingGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.materialGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('更新成功'),
            self.tr('配置在重启软件后生效'),
            duration=1500,
            parent=self
        )

    def __onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("选择文件夹"), "./")
        if not folder or cfg.get(cfg.saveFolder) == folder:
            return

        cfg.set(cfg.saveFolder, folder)
        self.saveFolderCard.setContent(folder)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(setTheme)

        # data
        self.scanFolderCard.folderChanged.connect(
            self.musicFoldersChanged)
        self.saveFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked)

        self.scanCard.clicked.connect(self.scan_db)
        self.cleanCard.clicked.connect(self.clean_db)
        self.resetCard.clicked.connect(self.reset_db)
        self.exportCard.clicked.connect(self.export_db)

        # self.quadButtonCard.button_1.clicked.connect(self.scan_db)
        # self.quadButtonCard.button_2.clicked.connect(self.clean_db)
        # self.quadButtonCard.button_3.clicked.connect(self.reset_db)
        # self.quadButtonCard.button_4.clicked.connect(self.export_db)

        # personalization
        self.themeColorCard.colorChanged.connect(setThemeColor)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

    def scan_db(self):
        folders = cfg.get(cfg.scanFolders)
        if not folders:
            # //DONE  优化提示
            logs.info(self.tr(f'扫描路径为空，取消扫描'))
            show_infoBar(self, self.tr(f'错误'), self.tr(
                f'扫描路径为空，请添加文件夹后开始扫描'), type='error')
            return
        txt_paths = get_txt_files(folders)

        if not txt_paths:
            show_infoBar(self, self.tr(f'错误'), self.tr(
                f'扫描路径内无文件，请添加文件后开始扫描'), type='error')
            return

        result = [item for txt_path in txt_paths for item in txt_to_ed2k_info_list(txt_path)[
            0]]

        deduplicate = True if cfg.get(cfg.checkDeduplicate) else False

        ed2k_infos_to_db(result, table_name='local_data',
                         init_delete=False, deduplicate=deduplicate)

        logs.info(self.tr(f'扫描数据完成'))
        show_infoBar(self, self.tr(f'操作成功'),
                     self.tr(f'扫描数据完成'), type='success')

    def clean_db(self):
        conn = sqlite3.connect( os.path.join(os.path.dirname(sys.argv[0]), 'data/database.db'))
        c = conn.cursor()
        c.execute("VACUUM")
        conn.close()
        logs.info(self.tr(f'清理数据完成'))
        show_infoBar(self, self.tr(f'操作成功'),
                     self.tr(f'整理数据完成'), type='success')

    def reset_db(self):
        table_name = 'local_data'

        w = myMessageBox(
            self.tr('警告'),
            self.tr('您确定要清空所有数据吗？此操作不可逆，请做好数据备份。'),
            self
        )
        if not w.exec():
            logs.info(self.tr(f'取消清空数据库操作'))
            show_infoBar(self, self.tr(f'提示'), self.tr(f'操作已取消'))
            return

        conn = sqlite3.connect( os.path.join(os.path.dirname(sys.argv[0]), 'data/database.db'))
        c = conn.cursor()

        c.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = c.fetchone()
        if not result:
            logs.info(self.tr(f'数据库为空'))
            show_infoBar(self, self.tr('提示'), self.tr('数据库为空，请先扫描数据'))
            return

        c.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        logs.info(self.tr(f'重置数据库完成'))
        show_infoBar(self, self.tr(f'操作成功'),
                     self.tr(f'已清空所有数据'), type='success')

    def export_db(self):

        os.makedirs('export', exist_ok=True)

        table_name = 'local_data'
        conn = sqlite3.connect( os.path.join(os.path.dirname(sys.argv[0]), 'data/database.db'))
        c = conn.cursor()

        c.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = c.fetchone()
        if not result:
            logs.info(self.tr(f'数据库为空'))
            show_infoBar(self, self.tr('提示'), self.tr('数据库为空，请先扫描数据'))
            return

        data = c.execute(f"SELECT * FROM {table_name}")

        time_now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")

        csv_ = os.path.abspath(f"export/{time_now}--{table_name}.csv")

        txt = os.path.abspath(f"export/{time_now}--{table_name}.txt")

        with open(csv_, "w", encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([description[0] for description in c.description])
            writer.writerows(data)

        data = c.execute(f"SELECT link FROM {table_name}")
        with open(txt, "w", encoding='utf-8-sig') as f:
            for row in data:
                f.write(row[0] + "\n")

        conn.close()

        logs.info(f'导出 {csv_}、{txt} 完成')

        w = myMessageBox(
            self.tr('提示'),
            self.tr('导出 csv 和 txt 成功，点击确认打开 txt') + ' 😉 ',
            self
        )

        if w.exec():
            os.startfile(txt)
            logs.info(f'打开 {txt}')
