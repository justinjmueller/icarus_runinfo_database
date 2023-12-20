# I. Introduction
Detailed information about each DAQ run and trigger is an essential input to physics analyses. This repository organizes code that is used for extracting information from various sources (primarily log files, hardware databases, and configuration files) and placing the results in a SQLite database.

# II. Tables
## Run Info
The `runinfo` table encapsulates information that exists at the per-run level. This includes timing, configuration details, and some information about the cathode and wire bias systems.
* `run_number` (integer) - The DAQ run number.
* `start_time` (text) - The time stamp associated with the START transition.
* `end_time` (text) - The time stamp associated with the STOP transition.
* `cathodehv` (real) - The average voltage on the cathode (Volts).
* `wbps_eind1` (real) - The average readback voltage of the East IND1 wire bias (Volts). 
* `wbps_eind2` (real) - The average readback voltage of the East IND2 wire bias (Volts).
* `wbps_ecoll` (real) - The average readback voltage of the East COLL wire bias (Volts).
* `wbps_wind1` (real) - The average readback voltage of the West IND1 wire bias (Volts).
* `wbps_wind2` (real) - The average readback voltage of the West IND2 wire bias (Volts).
* `wbps_wcoll` (real) - The average readback voltage of the West COLL wire bias (Volts).
* `configuration` (text) - The name of the DAQ configuration.
* `tpc_components` (integer) - The number of TPC components with FHiCL configuration files in the Run Records directory for the run; a proxy for the number of TPC components included in the DAQ.
* `pmt_components` (integer) - The number of PMT components with FHiCL configuration files in the Run Records directory for the run; a proxy for the number of PMT components included in the DAQ.
* `crt_components` (integer) - The number of CRT components with FHiCL configuration files in the Run Records directory for the run; a proxy for the number of CRT components included in the DAQ.

## Trigger Data
The `triggerdata` table encapsulates all information that exists at the per-trigger level. At the most basic level, this is metadata about each trigger that describes the trigger decision, coarse timing, and trigger type.
* `run_number` (integer) - DAQ run number.
* `version` (integer) - Version numbering for the trigger string data.
* `tname` (text) - 
* `event_no` (integer) - Event number.
* `seconds` (integer) - 
* `nanoseconds` (integer) - 
* `wr_name` (text) - 
* `wr_event_no` (integer) - Event number from the White Rabbit.
* `wr_seconds` (integer) - Time stamp of the global trigger (seconds).
* `wr_nanoseconds` (integer) - Time stamp of the global trigger (nanoseconds).
* `enable_type` (integer) - 
* `enable_seconds` (integer) - 
* `enable_nanoseconds` (integer) - 
* `gate_id` (integer) - Number of the current gate.
* `gate_type` (integer) - Number encoding the type of gate (1: BNB, 2: NuMI, 3: BNBOffbeam, 4: NuMIOffbeam, 5: Calibration).
* `gate_id_bnb` (integer) - Gate ID (BNB).
* `gate_id_numi` (integer) - Gate ID (NuMI).
* `gate_id_bnboff` (integer) - Gate ID (offbeam BNB).
* `gate_id_numioff` (integer) - Gate ID (offbeam NuMI).
* `beam_seconds` (integer) - Time stamp of the beam gate (seconds).
* `beam_nanoseconds` (integer) - Time stamp of the beam gate (nanoseconds).
* `trigger_type` (integer) - Type of the trigger or trigger logic (0: Majority, 1: MinBias).
* `trigger_source` (integer) - Originating cryostat of the trigger (0: Undecided, 1: East, 2: West, 7: Both).
* `cryo1_e_conn_0` (text) - 64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the EE wall.
* `cryo1_e_conn_2` (text) - 64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the EW wall.
* `cryo2_w_conn_0` (text) - 64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the WE wall.
* `cryo2_w_conn_2` (text) - 64-bit word with the status of the pairs of PMT discriminated signals (LVDS) for the WW wall.
* `cryo1_east_counts` (integer) - Counters of other activity in coincidence with the gate (other potential global triggers in the event) for the East cryostat.
* `cryo2_west_counts` (integer) - Counters of other activity in coincidence with the gate (other potential global triggers in the event) for the Wast cryostat.

## Trigger Logs
The `triggerlog` table contains metadata associated with each trigger log file. Log files may be incomplete at the time of transfer, so it is necessary to keep track of the size on disk to reprocess the log file if it has been updated.
* `log_name` (text) - The name of the log file.
* `stub` (bool) - Boolean tagging the log file as containing no actual triggers.
* `file_size` (integer) - Size of the file on disk.
* `run_number` (integer) - Run number corresponding to the log file.
* `processed` (bool) - Boolean tagging the log file as processed/not processed.