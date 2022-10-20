import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
from get_db_parameters import db_parameters_dict
from tabulate import tabulate


def make_conn() -> connection:
    db_conn_parameters: dict = db_parameters_dict()
    db_host = db_conn_parameters['RDS_DATABASE_HOST']
    db_name = db_conn_parameters['RDS_DEFAULT_DATABASE_NAME']
    db_user = 'postgres'
    db_pass = db_conn_parameters['ROOT_PASSWORD']
    db_port = db_conn_parameters['RDS_DATABASE_PORT']
    conn_string = "dbname='%s' user='%s' host='%s' port='%s' password='%s'" % (
        db_name, db_user, db_host, db_port, db_pass)
    try:
        conn = psycopg2.connect(conn_string)
        print('Connected!!')
        return conn
    except Exception as e:
        print(e)
        print('I am unable to connect to the database')


def fetch_data(conex: connection, query: str) -> list:
    cursor: DictCursor = conex.cursor(cursor_factory=DictCursor)
    cursor.execute(query)
    raw: list = cursor.fetchall()
    return raw


def get_replication_query(conex: connection) -> str:
    replication_slots_query = 'SELECT active_pid AS "PID", slot_name AS "Slot name", ' \
                              'pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) ' \
                              'AS "Replication slot lag", ' \
                              "CASE active WHEN True THEN 'True (healthy)' WHEN False THEN 'False (unhealthy)' END " \
                              'AS "Active", pg_stat_replication.reply_time AS "Last reply from standby" ' \
                              'FROM pg_replication_slots JOIN pg_stat_replication ' \
                              'ON pg_replication_slots.active_pid = pg_stat_replication.pid ;'
    replication_slots_query_pg11 = 'SELECT active_pid AS "PID", slot_name AS "Slot name", ' \
                                   'pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) ' \
                                   'AS "Replication slot lag", CASE active ' \
                                   "WHEN True THEN 'True (healthy)' WHEN False THEN 'False (unhealthy)' END " \
                                   'AS "Active", CASE WHEN pg_stat_replication.replay_lag IS NULL ' \
                                   "THEN 'Standby caught up' END " \
                                   'AS "Last reply from standby"  ' \
                                   'FROM pg_replication_slots JOIN pg_stat_replication ' \
                                   'ON pg_replication_slots.active_pid = pg_stat_replication.pid ;'
    query_pg_version = 'SELECT VERSION();'
    query_version_result = fetch_data(conex, query_pg_version)
    if query_version_result[0][0].startswith('PostgreSQL 11'):
        return replication_slots_query_pg11
    else:
        return replication_slots_query


def get_replication_slots(conex: connection) -> None:
    replication_slots_query = get_replication_query(conex)
    query_result = fetch_data(conex, replication_slots_query)
    if len(query_result) > 0:
        valid_pid_list = list()
        for x in query_result:
            table = [[str(x['PID']), x['Slot name'], x['Replication slot lag'], str(x['Active']),
                      str(x['Last reply from standby'])]]
            print(tabulate(table,
                           headers=["PID", "Slot name", "Replication slot lag", "Active",
                                    "Last reply from standby"]) + '\n')
            valid_pid_list.append(str(x['PID']))
        slots_query_result = input('Do you wanna terminate a replication slot? (Type y, yes or n, no)\n').lower()
        if slots_query_result.lower() in ['y', 'yes']:
            terminate_replication_slot(conex, valid_pid_list)
        elif slots_query_result.lower() in ['n', 'no']:
            print('No replication slot will be deleted')
        else:
            print('Wrong input')
    else:
        print("This instance doesn't have replication slots")


def terminate_replication_slot(conex: connection, valid_pid_list: list) -> None:
    replication_slot_pid = input(
        'Please, insert PID of the replication slot that you want to terminate:\n').strip()
    if replication_slot_pid.isdigit() and replication_slot_pid in valid_pid_list:
        query_terminate_slots = f"SELECT pg_terminate_backend ({replication_slot_pid});"
        try:
            terminate_query_result = fetch_data(conex, query_terminate_slots)
            if terminate_query_result[0][0]:
                print('PID ' + replication_slot_pid + ' was deleted')
        except Exception as e:
            print(e)
    else:
        print('Invalid input or PID, retry')


def main():
    conex = make_conn()
    get_replication_query(conex)
    get_replication_slots(conex)
    conex.close()


main()
