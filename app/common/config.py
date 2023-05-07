# coding:utf-8
import os
import sys
from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, FolderValidator, ConfigSerializer)


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # folders
    scanFolders = ConfigItem(
        "Folders", "LocalMusic", [ os.path.join(os.path.dirname(sys.argv[0]), 'ed2k')], FolderListValidator())
    saveFolder = ConfigItem(
        "Folders", "Download", "data", FolderValidator())

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.CHINESE_SIMPLIFIED, OptionsValidator(Language), LanguageSerializer(), restart=True)

    # Material
    blurRadius = RangeConfigItem(
        "Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", False, BoolValidator())

    # option checkbox
    checkDeduplicate = ConfigItem(
        "Option", "Deduplicate", False, BoolValidator())
    checkDatabase = ConfigItem(
        "Option", "Database", False, BoolValidator())
    checkImageMode = ConfigItem(
        "Option", "ImageMode", False, BoolValidator())


YEAR = 2023
AUTHOR = "Mai Ephemeral"
VERSION = "v1.1.0"

PyQt_Fluent_Widgets_URL = "https://github.com/zhiyiYo/PyQt-Fluent-Widgets"

HELP_URL = "https://github.com/Ephemeralwanning/Ed2k_Manager"

RELEASE_URL = "https://github.com/Ephemeralwanning/Ed2k_Manager/releases"

SQLITESUDIO_URL = 'https://github.com/pawelsalawa/sqlitestudio'

FEEDBACK_URL = "https://github.com/Ephemeralwanning/Ed2k_Manager/issues"
REPO_URL = "https://github.com/Ephemeralwanning/Ed2k_Manager"
GITHUB_URL = "https://github.com/Ephemeralwanning/Ed2k_Manager"

cfg = Config()
qconfig.load( os.path.join(os.path.dirname(sys.argv[0]), 'app/config/config.json'), cfg)
