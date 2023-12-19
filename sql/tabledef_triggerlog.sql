CREATE TABLE IF NOT EXISTS triggerlog (
log_name text NOT NULL PRIMARY KEY,
stub bool DEFAULT 0,
file_size integer DEFAULT 0,
run_number integer DEFAULT 0,
processed bool DEFAULT 0
);
