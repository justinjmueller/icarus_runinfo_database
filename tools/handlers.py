import logging
import os
import pandas as pd
from glob import glob

from tools import parse_daqinterface_log, parse_trigger_log, command

def update_runinfo(conn, daqinterface_log, epics_conditions):
    """
    Populate and update the run information table. Run start and stop times
    are retrieved from the DAQ Interface log file. 

    Parameters
    ----------
    conn: sqlite3.Connection
        The SQLite connection handle.
    daqinterface_log: str
        The full path of the DAQ interface log.
    epics_conditions: str
        The full path of the EPICS conditions file.

    Returns
    -------
    None.
    """
    logging.info('Updating table `runinfo.`')
    curs = conn.cursor()

    res = parse_daqinterface_log(daqinterface_log)
    nfound = len(res)
    command(curs, 'sql/select_runinfo_allruns.sql')
    entered = [x[0] for x in curs]
    latest = max(entered)
    latest_update = [r for r in res if r[0] == latest][0]
    res = [r for r in res if r[0] not in entered]
    logging.info(f'Found {nfound} run entries ({len(res)} new) in DAQInterface log.')
    command(curs, 'sql/insert_runinfo_startend.sql', res)
    command(curs, 'sql/update_runinfo_single.sql', (latest_update[1],latest_update[2],latest_update[0]))
    conn.commit()

    config_df = pd.read_csv('../logs/configurations.csv', header=None)
    runs = list(config_df[0])
    configs = list(config_df[1])
    tpc, pmt, crt = list(config_df[2]), list(config_df[3]), list(config_df[4])
    ins_config = [(configs[i], tpc[i], pmt[i], crt[i], runs[i]) for i in range(len(runs))]
    command(curs, 'sql/update_runinfo_configuration.sql', ins_config)
    conn.commit()

    epics_df = pd.read_csv(epics_conditions)
    command(curs, 'sql/select_runinfo_epics.sql')
    runs = [x[0] for x in curs.fetchall()]
    wbps_c_notna = epics_df['cathodehv'].notna()
    wbps_e_notna = epics_df['wbps_eind1'].notna()
    wbps_w_notna = epics_df['wbps_wind1'].notna()
    epics_runs = epics_df['run'].to_numpy()
    ins_epics = [(round(epics_df['cathodehv'].iloc[i],2) if wbps_c_notna[i] else None,
                  round(epics_df['wbps_eind1'].iloc[i],2) if wbps_e_notna[i] else None,
                  round(epics_df['wbps_eind2'].iloc[i],2) if wbps_e_notna[i] else None,
                  round(epics_df['wbps_ecoll'].iloc[i],2) if wbps_e_notna[i] else None,
                  round(epics_df['wbps_wind1'].iloc[i],2) if wbps_w_notna[i] else None,
                  round(epics_df['wbps_wind2'].iloc[i],2) if wbps_w_notna[i] else None,
                  round(epics_df['wbps_wcoll'].iloc[i],2) if wbps_w_notna[i] else None,
                  int(epics_df['run'].iloc[i])) for i in range(len(epics_df)) if epics_df['run'][i] not in runs]
    command(curs, 'sql/update_runinfo_epics.sql', ins_epics)
    conn.commit()

def update_triggerdata(conn, triggerlog_directory):
    """
    Checks for unprocessed log files in the trigger log table, then parses any
    log files found. Information from the trigger log files will be stored to
    the `triggerdata` table. The parsed list of triggers is checked against
    existing entries for the run to ensure duplication does not occurr in the
    case of log files that have been updated on disk.

    Parameters
    ----------
    conn: sqlite3.Connection
        The SQLite connection handle.
    triggerlog_directory: str
        The path to the directory containing the trigger logs.

    Returns
    -------
    None.
    """
    logging.info('Updating table `triggerdata.`')
    curs = conn.cursor()
    command(curs, 'sql/select_triggerlog_process.sql')
    res = curs.fetchall()
    logging.info(f'Found {len(res)} log files with unprocessed status.')
    for r in res:
        triggers = parse_trigger_log(triggerlog_directory+r[0], r[3])
        run = r[3]
        command(curs, 'sql/select_triggerdata_runnumber.sql', (run,))
        existing_triggers = [(e[0], str(e[3])) for e in curs.fetchall()]
        triggers = [x for x in triggers if (x[0], x[3]) not in existing_triggers]
        if len(existing_triggers) != 0 and len(triggers) != 0:
            logging.info(f'Found {len(triggers)} new triggers for Run {run}.')
        command(curs, 'sql/insert_triggerdata_standard.sql', triggers)
        command(curs, 'sql/update_triggerlog_processed.sql', (r[0],))
        conn.commit()

def update_triggerlog(conn, triggerlog_directory):
    """
    Scans the trigger log directory for logs with no entry in table 'triggerlog.'
    If no matching entry is found, do a quick parsing of the log to verify that it
    isn't a "stub" (a failed run - no actual triggers) and retrieve the run number.

    Parameters
    ----------
    conn: sqlite3.Connection
        The SQLite connection handle.
    triggerlog_directory: str
        The path to the directory containing the trigger logs.

    Returns
    -------
    None.
    """
    logging.info('Updating table `triggerlog.`')
    curs = conn.cursor()
    log_files = glob(f'{triggerlog_directory}icarustrigger*.log')
    logging.info(f'Found {len(log_files)} files in trigger log directory ({triggerlog_directory}).')
    for f in log_files:
        log_name = f.split('/')[-1]
        command(curs, 'sql/select_triggerlog_logname.sql', (log_name,))
        file_size = os.path.getsize(f)
        res = curs.fetchall()
        if len(res) == 0:
            try:
                lines = [x.strip('\n') for x in open(f, 'r').readlines()]
                runs = [x for x in lines if 'Completed the Start transition (Started run) for run ' in x]
                run = runs[0][53:runs[0].find(',')]
                command(curs, 'sql/insert_triggerlog_standard.sql', (log_name, 0, file_size, run))
                conn.commit()
                logging.info(f'New trigger log entry for Run {run} (file: {log_name}).')
            except IndexError:
                command(curs, 'sql/insert_triggerlog_standard.sql', (log_name, 1, file_size, 0))
                conn.commit()
                logging.info(f'Trigger log file {log_name} is a stub.')
        elif res[0][2] != file_size:
            command(curs, 'sql/update_triggerlog_reprocess.sql', (log_name,))
            command(curs, 'sql/update_triggerlog_filesize.sql', (file_size, log_name))
            conn.commit()
            logging.info(f'Trigger log for Run {res[0][3]} ({log_name}) has new file size on disk and will be reprocessed.')