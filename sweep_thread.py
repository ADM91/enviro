__author__ = 'masslab'

import types
import re
import os
import time
import csv
from queues import sweep_q
from config import *
from sqlalchemy.sql import select
from _mysql_exceptions import OperationalError


class SweepThread:

    def __init__(self, signal, instr_list, db):
        self.signal = signal
        self.db = db
        self.signal = signal
        self.instr_list = instr_list
        self.table_dictionary = {'thermometer': self.db.add_temperature_data,
                                 'hygrometer': self.db.add_humidity_data,
                                 'barometer': self.db.add_pressure_data}
        self.message_data = ''
        self.sweep_instr()

    def sweep_instr(self):
        for inst_d in self.instr_list:
            # Get data point from given instrument
            value = self.read_instrument(inst_d)
            if value:
                # Enter data to database or file
                corrected_value = self.correct_data(value, inst_d)
                db_insert = self.table_dictionary[inst_d['type']]
                db_insert(inst_d['id'], corrected_value)
                # self.data_enter_logic(inst_d, value)

                # Append to message data string
                self.message_data += 'type: %s,   id: %s,  value: %.3f\n' % (inst_d['type'], inst_d['id'], value)
                # Place message in queue
                if not inst_d['test']:
                    self.signal.emit('Sweeping...\n' + self.message_data)
            elif inst_d['test']:
                self.message_data = ''
            else:
                self.signal.emit('No reading from %s %s' % (inst_d['type'], inst_d['id']))

        # Generate an appropriate message to send back to UI
        self.generate_message()

    def read_instrument(self, inst_d):
        try:
            inst_d['connection'].open()
            for index, command in enumerate(command_dictionary[inst_d['type']][inst_d['id']][0]):
                inst_d['connection'].write(command)
                time.sleep(between_command_sleep)
                if index == len(command_dictionary[inst_d['type']][inst_d['id']][0]) - 1:
                    data = self.parse(inst_d['connection'].read(100), command_dictionary[inst_d['type']][inst_d['id']][1])
                    inst_d['connection'].close()
                    return data
        except ValueError as e:
            print e

        # Close serial connection
        inst_d['connection'].close()
        return None

    def generate_message(self):
        try:
            if not self.instr_list[0]['test']:
                message = '-----------------results from last sweep-----------------\n' \
                          'DateTime: %s\n' % time.strftime("%Y-%m-%d %H:%M") + self.message_data
                print message
                self.signal.emit(message)
            else:
                if self.message_data == '':
                    message = 'Instrument acquisition unsuccessful'
                    print message
                else:
                    message = '-----------------successful acquisition!-----------------\n' \
                              'DateTime: %s\n' % time.strftime("%Y-%m-%d %H:%M") \
                              + self.message_data \

                    print message
                self.signal.emit(message)
        except IndexError:
            self.signal.emit('Instrument list is empty')

    @staticmethod
    def correct_data(value, instr_d):
        # If value is None, return None
        if not value:
            return None

        # Return a corrected value
        return '%.3f' % (float(instr_d['meta'][5])
                         + value*float(instr_d['meta'][6])
                         + value*float(instr_d['meta'][7])**2)

    @staticmethod
    def parse(string, parse_format):
        if isinstance(parse_format, types.StringType):
            return float(re.findall(parse_format, string)[0])
        elif isinstance(parse_format, types.ListType):
            return float(string[parse_format[0]:parse_format[1]])

        else:
            return None

    # def data_enter_logic(self, instr_d, value):
    #
    #     # Check if database backup file exists do this:
    #     if self.find(backup_file_name, backup_file_directory):
    #         # If database is online, send data from backup file to the database and delete the file
    #         if self.db.check_db():
    #             # Send data from file to the db
    #             self.file_to_database()
    #             # Correct value using coefficients
    #             corrected_value = self.correct_data(value, instr_d)
    #             # Send newest data to db
    #             self.table_dictionary[instr_d['type']](instr_d['type'], corrected_value)
    #             # Remove the file
    #             os.remove(self.find(backup_file_name, backup_file_directory))
    #         # If the database is offline, keep writing to the backup file
    #         else:
    #             # Correct value using coefficients
    #             corrected_value = self.correct_data(value, instr_d)
    #             # If db is offline, send data to backup file
    #             self.data_to_file(instr_d, corrected_value)
    #             sweep_q.put('Sweeping...\nDatabase is offline, data sent to backup file')
    #
    #     # If backup file does not exist do this:
    #     else:
    #         # If database is online commit new data
    #         if self.db.check_db():
    #             # Correct value using coefficients
    #             corrected_value = self.correct_data(value, instr_d)
    #             # if backup file does not exist, send data directly to db
    #             self.table_dictionary[instr_d['type']](instr_d['type'], corrected_value)
    #         # If database is offline, store data in backup file
    #         else:
    #             # Correct value using coefficients
    #             corrected_value = self.correct_data(value, instr_d)
    #             # if backup file does not exist and database is offline, start a backup file
    #             self.data_to_file(instr_d, corrected_value)
    #             sweep_q.put('Sweeping...\nDatabase is offline, data backup file has been created')



    # def get_instrument_coeff(self, instrument):
    #     if instrument['type'] == 'thermometer':
    #         instr_table = self.db.thermometers
    #     elif instrument['type'] == 'barometer':
    #         instr_table = self.db.barometers
    #     elif instrument['type'] == 'hygrometer':
    #         instr_table = self.db.hygrometers
    #     else:
    #         print 'instrument type error'
    #         return
    #     sql = select([instr_table.c.coeff_a,
    #                   instr_table.c.coeff_b,
    #                   instr_table.c.coeff_c]).\
    #             where(instr_table.c.id == instrument['id'])
    #     return self.db.engine.execute(sql).fetchall()[0]

    # def file_to_database(self):
    #     with open(backup_file_directory + backup_file_name, 'r') as csvfile:
    #         reader = csv.reader(csvfile, delimiter=',')
    #         for row in reader:
    #             self.db.data_to_db(row[0], row[1], row[2], row[3])



        # if instrument['type'] == 'barometer' and int(instrument['id']) == 3:
        #     # Paroscientific 740-16B
        #     for item in commands_Paroscientific74016B:
        #         instrument['connection object'].write(item)
        #         time.sleep(between_command_sleep)
        #     data = instrument['connection object'].read(100)[5:]
        #     print 'raw value: ' + str(data)
        #
        # elif instrument['type'] == 'thermometer'\
        #         and instrument['probe'] in ['A00', 'A01', 'A02', 'A03', 'A04', 'A05', 'A06']:
        #     # ASL F250 probes A00-A06
        #     for item in commands_ASLF250A:
        #         if '%s' in item:
        #             instrument['connection object'].write(item % instrument['probe'])
        #         else:
        #             instrument['connection object'].write(item)
        #         time.sleep(between_command_sleep)
        #     data = instrument['connection object'].read(100)[2:8]
        #     print 'raw value: ' + str(data)
        #
        # elif instrument['type'] == 'thermometer' and instrument['probe'] == 'B00':
        #     # ASL F250 probe B00
        #     for item in commands_ASLF250B:
        #         if '%s' in item:
        #             instrument['connection object'].write(item % instrument['probe'])
        #         else:
        #             instrument['connection object'].write(item)
        #         time.sleep(between_command_sleep)
        #     data = instrument['connection object'].read(100)[2:8]
        #     print 'raw value: ' + str(data)
        #
        # else:
        #     print 'Instrument does not meet hard coded criteria'
        #     instrument['connection object'].close()
        #     return None

        # if instrument['type'] == 'thermometer':
        #     for item in commands_thermometers[instrument['id'][0]]:
        #         instrument['connection object'].write(item)
        #         time.sleep(between_command_sleep)
        #     (a, b) = commands_thermometers[instrument['id']][1]
        #     data = instrument['connection object'].read(100)[a:b]
        #     print 'raw value: ' + str(data)
        # elif instrument['type'] == 'barometer':
        #     for item in commands_barometers[instrument['id'][0]]:
        #         instrument['connection object'].write(item)
        #         time.sleep(between_command_sleep)
        #     (a, b) = commands_barometers[instrument['id']][1]
        #     data = instrument['connection object'].read(100)[a:b]
        #     print 'raw value: ' + str(data)
        # elif instrument['type'] == 'hygrometer':
        #     for item in commands_hygrometers[int(instrument['id'])][0]:
        #         instrument['connection object'].write(item)
        #         time.sleep(between_command_sleep)
        #     (a, b) = commands_hygrometers[int(instrument['id'])][1]
        #     data = instrument['connection object'].read(100)[a:b]
        #     print 'raw value: ' + str(data)
        # else:
        #     print 'Instrument does not meet hard coded criteria'
        #     instrument['connection object'].close()
        #     return None
        #
        # # Close serial connection
        # instrument['connection object'].close()
        #
        # try:
        #     data = float(data)
        # except ValueError:
        #     print 'ValueError in data'
        #     data = None
        #     return data
        #
        # return data

    # @staticmethod
    # def data_to_file(instrument, value):
    #
    #     with open(backup_file_directory + backup_file_name, 'a') as csvfile:
    #         writer = csv.writer(csvfile, delimiter=',')
    #         writer.writerow([instrument['type'], time.strftime('%Y-%m-%d %H:%M:%S'), int(instrument['id']), value])
    #         csvfile.close()
    #
    # @staticmethod
    # def find(name, path):
    #     for root, dirs, files in os.walk(path):
    #         if name in files:
    #             return os.path.join(root, name)


