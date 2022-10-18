import psycopg2
from psycopg2.extras import DictCursor
from get_db_parameters import db_parameters_list
from tabulate import tabulate


def make_conn():
    db_conn_parameters = db_parameters_list()
    db_host = db_conn_parameters['RDS_DATABASE_HOST']
    db_name = db_conn_parameters['RDS_DEFAULT_DATABASE_NAME']
    db_user = 'postgres'  # ??? check with Owen
    db_pass = db_conn_parameters['ROOT_PASSWORD']
    db_port = db_conn_parameters['RDS_DATABASE_PORT']
    conn_string = "dbname='%s' user='%s' host='%s' port='%s' password='%s'" % (
        db_name, db_user, db_host, db_port, db_pass)
    conn = None
    try:
        conn = psycopg2.connect(conn_string)
        print('Connected')
    except Exception as e:
        print(e)
        print('I am unable to connect to the database')
    return conn


def fetch_data(conn, query):
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(query)
    raw = cursor.fetchall()
    return raw


def get_replication_slots():
    replication_slots_query = "SELECT active_pid AS \"PID\", slot_name AS \"Slot name\", " \
                              "pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) " \
                              "AS \"Replication slot lag\", " \
                              "CASE active WHEN True THEN 'True (healthy)' WHEN False THEN 'False (unhealthy)' END " \
                              "AS \"Active\", pg_stat_replication.reply_time AS \"Last reply from standby\" " \
                              "FROM pg_replication_slots JOIN pg_stat_replication " \
                              "ON pg_replication_slots.active_pid = pg_stat_replication.pid ;"
    conex = make_conn()
    query_result = fetch_data(conex, replication_slots_query)
    if len(query_result) > 0:
        for x in query_result:
            table = [[str(x['PID']), x['Slot name'], x['Replication slot lag'], str(x['Active']),
                      str(x['Last reply from standby'])]]
            print(tabulate(table,
                           headers=["PID", "Slot name", "Replication slot lag", "Active",
                                    "Last reply from standby"]) + '\n')
        terminate_slot = input('Do you wanna terminate a replication slot? (Type y, yes or n, no)\n').lower()
        if terminate_slot.lower() in ['y', 'yes']:
            replication_slot_pid = input('Please, insert PID of the replication slot that you want to terminate:\n').strip()
            try:
                if replication_slot_pid.isdigit():
                    print('PID ' + replication_slot_pid + ' will be deleted')
                    query_terminate_slots = f"SELECT pg_terminate_backend ({replication_slot_pid}) ;"
                    terminate_query_result = fetch_data(conex, query_terminate_slots)
                    print(terminate_query_result)
                    conex.close()
                else:
                    print('Invalid input, retry')
                    conex.close()
            except Exception as e:
                print(e)
                conex.close()
        elif terminate_slot.lower() in ['n', 'no']:
            print('No replication slot will be deleted')
            conex.close()
        else:
            print('Wrong input')
            conex.close()
    else:
        print("This instance doesn't have replication slots")
    conex.close()


get_replication_slots()
