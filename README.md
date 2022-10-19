# Automation to fix broken_replication_slot alarms

From: [Write a script to automate fixing broken_replication_slot alerts STOPS-3740](https://jira.autodesk.com/browse/STOPS-3740)

## Dependencies

- boto3
- psycopg2
- tabulate

## You must know:
- Region (region_name) must be hardcoded when you run it in a bastion, so you must edit the file where boto3 is used, if you are not in a bastion, you must use the AWS_PROFILE tag instead
- Query replication slots will retrieve all slots, some of them can present Active as **True - healthy** (if this slot is currently actively being used) or **False - unhealthy** (not associated with any client connection) that could be filling the disk with WAL files 

## Run get_replication_status.py to terminate replication slots in RDS Postgres databases

Run **get_replication_status.py** with the AWS_PROFILE tag:

```console
AWS_PROFILE=infradev python get_replication_status.py
```

> Remember that to run python scripts with instance role permissions (such as on a bastion) you need to set the region (hardcoded) for boto3 scripts

1. Ask for an instance name (database identifier, hostname, or endpoint)
2. If found, look for the parameters to collect data for the connection string
3. If parameters are found, will try to connect to the database, if this works, will show the "Connected" message
4. When is connected to the database will query for all replication slots
5. Will ask you if you want to terminate a slot, and you need to confirm your decision
6. Will ask you for the PID of the replication slot that you want to terminate
7. Tries to terminate the replication slot, if this works, you will see the "PID {PID} was deleted" message

## Examples

```console
Insert database identifier, hostname or endpoint:
always-up-dev-fa1b1d7b
Connected
  PID  Slot name                                    Replication slot lag    Active          Last reply from standby
-----  -------------------------------------------  ----------------------  --------------  --------------------------------
11715  rds_us_east_2_db_tvqolnft47rmt674jcplwp2yna  0 bytes                 True (healthy)  2022-10-18 15:15:41.323285+00:00

Do you wanna terminate a replication slot? (Type y, yes or n, no)
n
No replication slot will be deleted
```

```console
Insert database identifier, hostname or endpoint:
always-up-dev-fa1b1d7b.c0nhb46jr1uw.us-east-2.rds.amazonaws.com
Connected
  PID  Slot name                                    Replication slot lag    Active          Last reply from standby
-----  -------------------------------------------  ----------------------  --------------  --------------------------------
21518  rds_us_east_2_db_tvqolnft47rmt674jcplwp2yna  0 bytes                 True (healthy)  2022-10-18 22:04:47.982116+00:00

Do you wanna terminate a replication slot? (Type y, yes or n, no)
Y
Please, insert PID of the replication slot that you want to terminate:
21518
PID 21518 was deleted
```
