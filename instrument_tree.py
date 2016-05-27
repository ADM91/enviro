__author__ = 'masslab'

from PyQt4 import QtGui, QtCore, uic


class InstrumentTree:
    def __init__(self, db):
        self.window = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint |
                                    QtCore.Qt.WindowTitleHint |
                                    QtCore.Qt.WindowMinMaxButtonsHint)
        self.ui = uic.loadUi('ui_xml/select_instrument.ui', self.window)
        self.db = db
        self.populate_tree()
        self.ui.confirmButton.clicked.connect(self.confirm)
        self.instrument_type = ''
        self.instrument_id = ''
        self.window.exec_()

    def general_tree(self, top_title, db_query):
        # Generate
        top = QtGui.QTreeWidgetItem(self.ui.instrumentTree)
        top.setText(0, top_title)
        for t in db_query:
            child = QtGui.QTreeWidgetItem()
            child.setText(0, ' | '.join([str(i) for i in t]))
            top.addChild(child)
        return

    def populate_tree(self):
        self.ui.instrumentTree.setHeaderLabel('')
        self.ui.instrumentTree.addTopLevelItem(self.general_tree('thermometer', self.db.get_thermometers()))
        self.ui.instrumentTree.addTopLevelItem(self.general_tree('hygrometer', self.db.get_hygrometers()))
        self.ui.instrumentTree.addTopLevelItem(self.general_tree('barometer', self.db.get_barometers()))

    def confirm(self):
        text = self.ui.instrumentTree.currentItem().text(0)
        if not self.ui.instrumentTree.currentItem().parent():
            return
        else:
            self.instrument_id = text.split(' | ')[0]
            self.instrument_type = self.ui.instrumentTree.currentItem().parent().text(0)

        print self.instrument_type, self.instrument_id
        self.window.close()





# import sys
# from database_orm import DatabaseORM
# dbase = DatabaseORM()
#
# app = QtGui.QApplication(sys.argv)
# it = InstrumentTree(dbase)

