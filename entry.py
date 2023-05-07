# coding:utf-8
import os
import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from app.common.config import cfg
from app.view.main_window import MainWindow

# done: 相对路径改绝对路径！！

for i in ['ed2k', 'data', 'log']:
    os.makedirs( os.path.join(os.path.dirname(sys.argv[0]), i), exist_ok=True)

# enable dpi scale
if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# create application
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

font = app.font()
font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
app.setFont(font)

# //DONE 国际化

locale = cfg.get(cfg.language).value

Translator = QTranslator()

Translator.load(locale, 'language', '.', ':/i18n/language')

app.installTranslator(Translator)

# create main window
w = MainWindow()
w.show()

app.exec_()
