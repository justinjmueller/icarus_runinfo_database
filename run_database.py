import sqlite3
import logging
import sys
from tools import command, update_triggerlog, update_triggerdata, update_runinfo

triggerlog_directory = '/icarus/data/users/mueller/logs/trigger_logs/'
daqinterface_log = '/icarus/data/users/mueller/logs/DAQInterface_partition1.log'
epics_conditions = '/icarus/data/users/mueller/logs/epics_runinfo.csv'

def main():
    # Configure logging.
    logging.basicConfig(filename='database.log',
                        level=logging.INFO,
                        format='%(levelname)s %(asctime)s: %(message)s',
                        datefmt='%a %b %d %H:%M:%S %Z %Y')
    logging.info('Call to run_database.py initiated.')

    # Open connection to the database.
    try:
        conn = sqlite3.connect('db/icarus_metadata.db')
        logging.info('Connection to database established.')
    except Exception as e:
        logging.error(str(e)+'\nConnection to database failed. Exit.')
        sys.exit(1)

    curs = conn.cursor()

    # Create tables.
    command(curs, 'sql/tabledef_triggerlog.sql')
    command(curs, 'sql/tabledef_triggerdata.sql')
    command(curs, 'sql/tabledef_runinfo.sql')

    # Update tables.
    update_triggerlog(conn, triggerlog_directory)
    update_triggerdata(conn, triggerlog_directory)
    update_runinfo(conn, daqinterface_log, epics_conditions)

if __name__ == '__main__':
    main()