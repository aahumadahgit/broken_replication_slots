import boto3

rds_client = boto3.client('rds')

# db_instance_filters = [{'Name': 'engine', 'Values': ['postgres']}]
AWS_RDS_DNS = 'rds.amazonaws.com'


def get_db_identifier():
    db_host = input('Insert database identifier, hostname or endpoint: \n').lower().replace(" ", "")
    if 'replica' in db_host:
        print('This is a read replica instance, check the primary instance')
    else:
        return db_host


def search_db_instance():
    db_host = get_db_identifier()
    if db_host:
        if AWS_RDS_DNS in db_host:
            db_endpoint = db_host
            db_identifier = db_host.split('.')[0]
        else:
            db_identifier = db_host
            db_endpoint = ''
        try:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)['DBInstances'][0]
            db_rds_endpoint = response['Endpoint']['Address']
            if not db_endpoint or db_endpoint == db_rds_endpoint:
                db_port = response['Endpoint']['Port']
                rds_db_info = {'db_identifier': db_identifier, 'db_endpoint': db_rds_endpoint, 'db_port': db_port}
                return rds_db_info
            else:
                print("Endpoint address doesn't match with any existed database")
        except Exception as e:
            print(e)
    else:
        print('Please, indicate a valid instance')
