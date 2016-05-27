__author__ = 'masslab'

from nist_config import backup_file_directory,db_usr, db_pwd, db_host_server, db_schema

backup_file_name = 'for_database.csv'
software_name = 'Environment Monitor'
version = '0.1'


#-----------------------------------------------------------------------------------------------------------------------
# The dictionaries below give the program instructions on how to communicate with each individual instrument.
# The dictionary keys are instrument id's from the calibrations database
# If changes need to be made use the format:
# id: [(cmd, cmd, ...], (read start, read end)]

slider_max = 20

# Thermometers
commands_thermometers = {3: [['R1\r\n', 'U0\r\n', 'SA01\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A01
                         4: [['R1\r\n', 'U0\r\n', 'SA02\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A02
                         5: [['R1\r\n', 'U0\r\n', 'SA03\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A03
                         6: [['R1\r\n', 'U0\r\n', 'SA04\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A04
                         7: [['R1\r\n', 'U0\r\n', 'SA05\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A05
                         8: [['R1\r\n', 'U0\r\n', 'SA06\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A06
                         9: [['R1\r\n', 'U0\r\n', 'SA00\r\n', 'MI\r\n'], r'[-.\d]+'],  # ASL F250 A00
                         10: [['R1\r\n', 'U0\r\n', 'MJ\r\n'], r'[-.\d]+']}             # ASL F250 B00

# Barometers
commands_barometers = {3: ['*0100P3\r\n', [5, -1]]}  # Paroscientific 740-16B

# Hygrometers
commands_hygrometers = {2: ['A01/P1Q1\r\n', [0, -1]],
                        10: ['SEND\r', [5, 10]]}  # Vaisala HMI36


command_dictionary = {'thermometer': commands_thermometers,
                      'hygrometer': commands_hygrometers,
                      'barometer': commands_barometers}
#-----------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------
# This variable tells the program how long to wait to read after sending a command.
between_command_sleep = 0.2  # seconds
#-----------------------------------------------------------------------------------------------------------------------
