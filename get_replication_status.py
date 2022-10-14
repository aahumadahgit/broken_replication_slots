import psycopg2
from psycopg2.extras import DictCursor
from get_db_parameters import db_parameters_list
from tabulate import tabulate


def make_conn():
    db_conn_parameters = db_parameters_list()
    db_host = db_conn_parameters['RDS_DATABASE_HOST']
    db_name = db_conn_parameters['RDS_DEFAULT_DATABASE_NAME']
    db_user = 'postgres'  # ??? check with Varjitt
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
        print("I am unable to connect to the database")
    return conn


def fetch_data(conn, query):
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute(query)
    raw = cursor.fetchall()
    return raw


def get_replication_slots():
    replication_slots_query = "SELECT active_pid as \"PID\", slot_name as \"Slot name\", " \
                              "pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) " \
                              "AS \"Replication slot lag\", active as \"Active\" FROM pg_replication_slots ;"
    conex = make_conn()
    query_result = fetch_data(conex, replication_slots_query)
    if len(query_result) > 0:
        for x in query_result:
            print("PID: " + str(x['PID']) + " Replication slot lag: " + x['Replication slot lag'] + " Slot name: " + x[
                'Slot name'] + " Active: " + str(x['Active']))
            # table = ["PID"[str(x['PID']), x['Replication slot lag'], x['Slot name'], str(x['Active'])]]
            # print(tabulate(table, headers=["PID", "Replication slot lag", "Slot name", "Active"]))
        terminate_slot = input('Do you wanna terminate a replication slot? (Type y, yes or n, no)\n').lower()
        if terminate_slot.lower() in ["y", "yes"]:
            replication_slot_pid = input('Please, insert PID of the replication slot that you want to terminate:\n')
            print('PID ' + replication_slot_pid + ' will be deleted')
            query_terminate_slots = f"SELECT pg_terminate_backend ({replication_slot_pid}) ;"
            terminate_query_result = fetch_data(conex, query_terminate_slots)
            print(terminate_query_result)
            # return replication_slot_pid
        elif terminate_slot.lower() in ["n", "no"]:
            print('No replication slot will be deleted')
            conex.close()
        else:
            print('Wrong input')
            conex.close()
    else:
        print("This instance doesn't have replication slots")
    conex.close()


get_replication_slots()
