import sqlite3
import logging

def command(curs, comm, vals=None):
    """
    Execute a command defined in an SQL file.
    
    Parameters
    ----------
    curs: The SQLite cursor handle.
    comm: The file name and path for the sql command.
    vals: Values to use as arguments for the sql command (tuple).

    Returns
    -------
    None.
    """
    sql_command = open(comm, 'r').read()
    try:
        if isinstance(vals, list):
            curs.executemany(sql_command, vals)
        elif vals:
            curs.execute(sql_command, vals)
        else:
            curs.execute(sql_command)
    except Exception as e:
        logging.error(str(e)+f'\nCaught exception with command {comm} and values {vals}.')