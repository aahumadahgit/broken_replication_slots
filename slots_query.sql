'SELECT active_pid AS "PID", slot_name AS "Slot name", ' \
'pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) ' \
'AS "Replication slot lag", ' \
'CASE active WHEN True THEN "True (healthy)" WHEN False THEN "False (unhealthy)" END ' \
'AS "Active", pg_stat_replication.reply_time AS "Last reply from standby" ' \
'FROM pg_replication_slots JOIN pg_stat_replication ' \
'ON pg_replication_slots.active_pid = pg_stat_replication.pid ;'