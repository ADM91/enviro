__author__ = 'masslab'

from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, Table, MetaData, select, text
from sqlalchemy.ext.declarative import declarative_base
from config import db_usr, db_pwd, db_host_server, db_schema
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import expression


Base = declarative_base()

class DatabaseORM:

    def __init__(self):

        # Generate engine and session class for calibrations_v2 schema
        self.engine = create_engine("mysql://%s:%s@%s/%s" % (db_usr, db_pwd, db_host_server, db_schema), echo=False)

        # Get metadata and reflect database to "meta"
        meta = MetaData()
        meta.reflect(bind=self.engine)

        # Instrument object tables
        self.thermometers = Table("thermometers", meta)
        self.barometers = Table("barometers", meta)
        self.hygrometers = Table("hygrometers", meta)
        self.thermometers_data = Table("thermometers_data", meta)
        self.barometers_data = Table("barometers_data", meta)
        self.hygrometers_data = Table("hygrometers_data", meta)

    def add_temperature_data(self, identifier, temp):
        self.engine.execute(self.thermometers_data.insert(), thermometer_id=identifier, temperature=temp)

    def add_pressure_data(self, identifier, press):
        self.engine.execute(self.barometers_data.insert(), barometer_id=identifier, pressure=press)

    def add_humidity_data(self, identifier, humid):
        self.engine.execute(self.hygrometers_data.insert(), hygrometer_id=identifier, humidity=humid)

    def get_thermometers(self):
        sql = select([self.thermometers.c.id,
                     self.thermometers.c.model,
                     self.thermometers.c.serial,
                     self.thermometers.c.probe,
                     self.thermometers.c.room])
        return self.engine.execute(sql).fetchall()

    def get_hygrometers(self):
        sql = select([self.hygrometers.c.id,
                     self.hygrometers.c.model,
                     self.hygrometers.c.serial,
                     self.hygrometers.c.probe,
                     self.hygrometers.c.room])
        return self.engine.execute(sql).fetchall()

    def get_barometers(self):
        sql = select([self.barometers.c.id,
                     self.barometers.c.model,
                     self.barometers.c.serial,
                     self.barometers.c.room])
        return self.engine.execute(sql).fetchall()

    def get_instrument_metadata(self, table, identifier):
        sql = select([table.c.baudrate,
                      table.c.parity,
                      table.c.bytesize,
                      table.c.stopbits,
                      table.c.timeout,
                      table.c.coeff_a,
                      table.c.coeff_b,
                      table.c.coeff_c,
                      table.c.id,
                      table.c.model,
                      table.c.serial,
                      table.c.probe,
                      table.c.serial]).\
              where(table.c.id == identifier)
        return self.engine.execute(sql).fetchall()[0]

    def check_db(self):
        try:
            sql = select([self.thermometers.c.baudrate])
            self.engine.execute(sql).fetchone()
            print 'database online :)'
            return True
        except OperationalError:
            print 'database offline :('
            return False

# db = DatabaseORM()
#
# t = db.get_thermometers()
# for therm in t:
#     print therm
