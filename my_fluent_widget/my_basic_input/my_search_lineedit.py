# coding:utf-8


from qfluentwidgets import (SearchLineEdit)


class mySearchLineEdit(SearchLineEdit):
    """ Search line edit """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(self.tr('搜索 ed2k'))
        self.textChanged.connect(self.search)

