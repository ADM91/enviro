__author__ = 'masslab'

import sys
from serial import Serial
from serial.serialutil import SerialException
from threading import Thread
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import QObject, pyqtSignal
from sqlalchemy.sql import select
from sweep_thread import SweepThread
from database_orm import DatabaseORM
from error_message import ErrorMessage
from queues import sweep_q
from serial_ports import serial_ports
from config import software_name, slider_max
from widget_state import *
from instrument_tree import InstrumentTree


class MainUI(QObject):

    signal_pass = pyqtSignal(str)
    signal_fail = pyqtSignal(str)

    def __init__(self, window):
        super(QObject, self).__init__()
        window.setWindowTitle(software_name)
        self.ui = uic.loadUi('ui_xml/Enviro_ui_v3.ui', window)
        self.ui.freqLabel.setText('1 min')
        self.ui.freqSlider.setValue(int(slider_max*(float(1)/100)))

        # initialize the database object relational mapping
        self.db = DatabaseORM()
        self.table_dictionary = {'thermometer': self.db.thermometers,
                                 'hygrometer': self.db.hygrometers,
                                 'barometer': self.db.barometers}
        self.query_dictionary = {'thermometer': self.db.get_thermometers(),
                                 'hygrometer': self.db.get_hygrometers(),
                                 'barometer': self.db.get_barometers()}
        self.instr_test_dic = {}
        self.instr_list = []
        self.instrument_type = None
        self.instrument_id = None

        self.ui.portCombo.addItems(serial_ports())

        # Set widget initial states
        state_initial(self.ui)

        # Initiate instrument sweep timer
        self.sweep_timer = QtCore.QTimer()

        # Activate event callback functions
        self.callback_connector()

        MainWindow.show()

    def callback_connector(self):
        self.ui.recordRadio.clicked.connect(self.click_record_mode)
        self.ui.addRadio.clicked.connect(self.click_add_mode)
        self.ui.acquireButton.clicked.connect(self.click_acquire)
        self.ui.freqSlider.sliderReleased.connect(self.slider_callback)
        self.ui.freqSlider.sliderPressed.connect(self.slider_callback)
        self.ui.selectButton.clicked.connect(self.click_select)
        self.signal_pass.connect(self.signal_pass_slot)
        self.signal_fail.connect(self.signal_fail_slot)
        QtCore.QObject.connect(self.sweep_timer, QtCore.SIGNAL("timeout()"), self.on_sweep_signal)

    def click_select(self):
        tree = InstrumentTree(self.db)
        self.instrument_type = str(tree.instrument_type)
        self.instrument_id = int(tree.instrument_id)
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append('Instrument selected: %s' % tree.ui.instrumentTree.currentItem().text(0))
        state_instrument_selected(self.ui)

    def click_acquire(self):
        self.signal_pass.emit('Acquiring connection...')
        metadata = self.db.get_instrument_metadata(self.table_dictionary[self.instrument_type], self.instrument_id)

        if not metadata[0]:
            state_instrument_selected(self.ui)
            ErrorMessage('Instrument serial settings are not configured on the database!')
            return

        try:
            # Create connection object
            conn = Serial(port=str(self.ui.portCombo.currentText()),
                          baudrate=int(metadata[0]),
                          parity=str(metadata[1]),
                          bytesize=int(metadata[2]),
                          stopbits=int(metadata[3]),
                          timeout=int(metadata[4]))
            conn.close()
        except [ValueError, SerialException] as e:
            print e
            ErrorMessage('Connection failed in configuration')
            return
        else:
            # Populate test dictionary
            self.instr_test_dic = {'type': self.instrument_type,
                                   'id': self.instrument_id,
                                   'meta': metadata,
                                   'connection': conn,
                                   'test': True}

        try:
            # Start sweep thread to test communication
            t = Thread(target=SweepThread, args=(self.signal_pass, [self.instr_test_dic], self.db))
            t.start()
        except SerialException as e:
            print e
            print 'something didnt work'

        state_acquiring(self.ui)

    def signal_pass_slot(self, arg):
        self.ui.textBrowser.clear()
        self.ui.textBrowser.append(arg)

        if 'successful acquisition' in arg:
            self.add_instrument()
            state_after_add(self.ui)
        if 'acquisition unsuccessful' in arg:
            state_after_add(self.ui)

    def signal_fail_slot(self, arg):
        pass

    def on_sweep_signal(self):
        sweep_t = Thread(target=SweepThread, args=(self.signal_pass, self.instr_list, self.db))
        sweep_t.start()

    def click_record_mode(self):
        state_record_mode(self.ui)
        sweep_period_seconds = int(self.ui.freqLabel.text().split(' ')[0])*60
        print 'sweep period: %s' % sweep_period_seconds
        self.sweep_timer.setInterval(sweep_period_seconds*1000)
        self.sweep_timer.start()
        self.on_sweep_signal()
        self.signal_pass.emit('Sweeping...\n')

    def click_add_mode(self):
        self.sweep_timer.stop()
        state_initial(self.ui)
        self.signal_pass.emit('Add instruments')

    def slider_callback(self):
        val = float(self.ui.freqSlider.value() + int(float(100)/slider_max))
        mapping = slider_max*(val/100)
        self.ui.freqLabel.setText("%s min" % int(mapping))

    def add_instrument(self):

        # Indicate this dictionary is no longer for test
        self.instr_test_dic['test'] = False

        self.instr_list.append(self.instr_test_dic.copy())
        for i in self.instr_list:
            print i

        # Create new row in table
        row_num = self.ui.instrTable.rowCount()
        self.ui.instrTable.insertRow(row_num)

        # Populate row
        text_type = QtGui.QTextBrowser()
        text_type.setText(self.instr_list[-1]['type'])
        self.ui.instrTable.setCellWidget(row_num, 0, text_type)

        text_port = QtGui.QTextBrowser()
        text_port.setText(self.ui.portCombo.currentText())
        self.ui.instrTable.setCellWidget(row_num, 1, text_port)

        text_id = QtGui.QTextBrowser()
        text_id.setText(str(self.instr_list[-1]['id']))
        self.ui.instrTable.setCellWidget(row_num, 2, text_id)

        text_model = QtGui.QTextBrowser()
        text_model.setText(self.instr_list[-1]['meta'][9])
        self.ui.instrTable.setCellWidget(row_num, 3, text_model)

        text_Probe = QtGui.QTextBrowser()
        text_Probe.setText(self.instr_list[-1]['meta'][11])
        self.ui.instrTable.setCellWidget(row_num, 4, text_Probe)

        remove = QtGui.QPushButton()
        remove.setText('Remove')
        self.ui.instrTable.setCellWidget(row_num, 5, remove)
        remove.clicked.connect(self.click_remove_from_list)

        # Resize Columns
        self.ui.instrTable.resizeColumnToContents(3)

    def click_remove_from_list(self):
        click_me = QtGui.QApplication.focusWidget()
        index = self.ui.instrTable.indexAt(click_me.pos())
        self.ui.instrTable.removeRow(index.row())
        removed = self.instr_list.pop(index.row())
        self.signal_pass.emit('%s %s removed' % (removed['type'], removed['id']))

        print '\n instrument removed'
        for i in self.instr_list:
            print i

    # def activate_type(self):
    #     self.ui.instrCombo.clear()
    #     self.sql_query_instr_info(self.ui.typeCombo.currentText())
    #     if self.ui.instrCombo.currentText():
    #         self.ui.instrCombo.setEnabled(True)
    #         self.ui.acquireButton.setEnabled(True)
    #     else:
    #         self.ui.instrCombo.setEnabled(False)
    #         self.ui.acquireButton.setEnabled(False)

    def sql_query_instr_info(self, type):
        pass
        # print "now im here"
        # if type == "thermometer":
        #     instr_table = self.db.thermometers
        #     sql = select([instr_table.c.id,
        #                   instr_table.c.model,
        #                   instr_table.c.probe,
        #                   instr_table.c.room]).order_by(instr_table.c.id)
        #     result = self.db.engine.execute(sql)
        #     self.ui.instrCombo.addItems([str(r[0]) + " | " + r[1] + " | " + r[2] + " | " + r[3] for r in result])
        # else:
        #     if type == "barometer":
        #         instr_table = self.db.barometers
        #     elif type == "hygrometer":
        #         instr_table = self.db.hygrometers
        #     else:
        #         sweep_q.put('instrument type name error')
        #         return
        #     sql = select([instr_table.c.id,
        #                   instr_table.c.model,
        #                   instr_table.c.room]).order_by(instr_table.c.id)
        #     result = self.db.engine.execute(sql)
        #     self.ui.instrCombo.addItems([str(r[0]) + " | " + r[1] + " | " + r[2] for r in result])






if __name__ == "__main__":

    # Start application
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")
    MainWindow = QtGui.QMainWindow()
    main_ui = MainUI(MainWindow)
    sys.exit(app.exec_())


