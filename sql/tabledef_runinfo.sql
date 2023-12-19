CREATE TABLE IF NOT EXISTS runinfo (
run_number integer NOT NULL PRIMARY KEY,
start_time text NOT NULL,
end_time text NOT NULL,
cathodehv real,
wbps_eind1 real,
wbps_eind2 real,
wbps_ecoll real,
wbps_wind1 real,
wbps_wind2 real,
wbps_wcoll real,
configuration text,
tpc_components integer,
pmt_components integer,
crt_components integer
);
