import numpy as np
import logging

def parse_daqinterface_log(log_name):
    """
    Parses the DAQ Interface log to retrieve the start/stop times of each run.

    Parameters
    ----------
    log_name: The name of the DAQ Interface log file.

    Returns
    -------
    A list of tuples containing (in order) the run number, start time, and end time.
    """
    lines = [x.strip('\n') for x in open(log_name, 'r').readlines()]
    transitions = {'boot0': 'BOOT transition underway',
                   'boot1': 'BOOT transition complete',
                   'conf0': 'CONFIG transition underway',
                   'conf1': 'CONFIG transition complete',
                   'star0': 'START transition underway for run',
                   'star1': 'START transition complete for run',
                   'reco0': 'RECOVER transition underway',
                   'reco1': 'RECOVER transition complete',
                   'stop0': 'STOP transition underway for run',
                   'stop0': 'STOP transition underway for run',
                   'dstop': 'DAQInterface in partition 1 launched and now in "stopped" state',
                   'dkill': 'DAQInterface on partition 1 caught kill signal 15',
                   'term0': 'TERMINATE transition underway',
                   'term1': 'TERMINATE transition complete'}
    find = lambda k: [(i, l, k) for i, l in enumerate(lines) if transitions[k] in l]
    tfound = list()
    for k in transitions.keys():
        tfound += find(k)
    tfound.sort(key=lambda x: x[0])
    boot0 = np.argwhere([x[2]=='boot1' for x in tfound])[:,0]
    missing_boot = [i for i in boot0 if tfound[i-1][2] != 'boot0']
    for m in missing_boot[::-1]:
        tfound.insert(m, (tfound[m][0], tfound[m][1][:28]+': BOOT transition underway\n', 'boot0'))

    group_starts = [i for i in range(len(tfound)) if tfound[i][2] == 'boot0']
    stop_trans = {int(tfound[i][1].split(' ')[-1]) : i for i in range(len(tfound)) if tfound[i][2]=='stop0'}
    group_starts.append(len(group_starts))
    data = {'run': list(), 'start': list(), 'end': list()}
    for g in range(len(group_starts)-1):
        data['run'].append(0)
        data['start'].append('---')
        data['end'].append('---')
        group = tfound[group_starts[g]:group_starts[g+1]]
        arg_under = np.argwhere([x[2]=='star0' for x in group])[:,0]
        arg_start = np.argwhere([x[2]=='star1' for x in group])[:,0]
        if len(arg_start) == 1:
            data['run'][-1] = int(group[arg_start[0]][1].split(' ')[-1])
            data['start'][-1] = group[arg_start[0]][1][:28]

        arg_stop = np.argwhere([x[2]=='stop0' for x in group])[:,0]
        arg_reco = np.argwhere([x[2]=='reco0' for x in group])[:,0]
        arg_kill = np.argwhere([x[2]=='dkill' for x in group])[:,0]
        arg_dstp = np.argwhere([x[2]=='dstop' for x in group])[:,0]

        if len(arg_stop) == 1:
            data['end'][-1] = group[arg_stop[0]][1][:28]
        elif len(arg_reco) >= 1 and len(arg_start) == 1:
            data['end'][-1] = group[arg_reco[0]][1][:28]
        elif len(arg_kill) >= 1 and len(arg_start) == 1:
            data['end'][-1] = group[arg_kill[0]][1][:28]
        elif len(arg_dstp) >= 1 and len(arg_start) == 1:
            data['end'][-1] = group[arg_dstp[0]][1][:28]
        elif data['run'][-1] != 0 and data['run'][-1] in stop_trans.keys():
            data['end'][-1] = tfound[stop_trans[data['run'][-1]]][1][:28]

        if len(arg_under) == 1:
            data['run'][-1] = int(group[arg_under[0]][1].split(' ')[-1])
            if len(arg_start) == 0 and data['end'][-1] != '---':
                data['start'][-1] = group[arg_under[0]][1][:28]
    run_list, counts = np.unique([x for x in data['run'] if x != 0], return_counts=True)
    for r in run_list[counts>1]:
        for i in np.argwhere(data['run']==r)[:,0][:-1]:
            data['run'].pop(i)
            data['start'].pop(i)
            data['end'].pop(i)
    return [(data['run'][i], data['start'][i], data['end'][i]) for i in range(len(data['run'])) if data['run'][i] != 0]

def parse_trigger_log(log_name, run):
    """
    Parses a single trigger log and returns a list containing the field information
    in each trigger string.

    Parameters
    ----------
    log_name: The name of the trigger log file.
    run: The run number corresponding to the log file.

    Returns
    -------
    A tuple containing the trigger string fields in the order that they appear.

    """
    fields = dict(version=1, name=2, event_no=3, seconds=4, nanoseconds=5, wr_name=6,
                  wr_event_no=7, wr_seconds=8, wr_nanoseconds=9, enable_type=11,
                  enable_seconds=14, enable_nanoseconds=15, gate_id=17, gate_type=27,
                  gate_id_BNB=19, gate_id_NuMI=21, gate_id_BNBOff=23, gate_id_NuMIOff=25,
                  beam_seconds=30, beam_nanoseconds=31, trigger_type=33, trigger_source=35,
                  cryo1_e_conn_0=37, cryo1_e_conn_2=39, cryo2_w_conn_0=41, cryo2_w_conn_2=43,
                  cryo1_east_counts=45, cryo2_west_counts=47)
    data = dict(zip(list(fields.values()), [list() for i in range(len(fields))]))

    lines = open(log_name, 'r').readlines()
    lines = [x.strip('\n') for x in lines]
    strings = [x for x in lines if 'string received' in x and ((x != 'string received:: ') and ('[RATE LIMIT]' not in x))]

    count = 0
    isfirst = True
    results = list()
    for r in range(len(strings)):
        res = strings[r][len('string received:: '):].replace(' ', '').split(',')
        for k in data.keys():
            if len(res) == 48:
                data[k].append(res[k])
            elif len(res) > 1:
                count += 1
            if(len(res) != 48 and len(res) > 1 and isfirst):
                isfirst=False
        if len(res) == 48:
            results.append(tuple([run]+[data[k][-1] for k in data.keys()]))

    if count > 0:
        logging.warning(f'There were {count} triggers not matching the trigger string template.')
    logging.info(f'Trigger log for Run {run} processed ({len(results)} triggers).')
    return results