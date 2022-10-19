import boto3

# Run this script with the AWS_PROFILE tag and the name of the profile in the .aws/config, for example:
# AWS_PROFILE=infradev
rds_client = boto3.client('rds')
# Comment previous line and uncomment the following lines that contains the values from session and client,
# add the region to execute this script in the tf-bastion, for example: region_name='us-east-1'
# session = boto3.Session(region_name='region')
# rds_client = session.client('rds')

# db_instance_filters = [{'Name': 'engine', 'Values': ['postgres']}]
AWS_RDS_DNS = 'rds.amazonaws.com'


def get_db_identifier():
    db_host = input('Insert database identifier, hostname or endpoint:\n').lower().strip()
    if 'replica' in db_host:
        print('\nThis is a read replica instance, please, check the primary instance instead')
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
                print("\nEndpoint address doesn't match with any existed database")
        except Exception as e:
            print(e)
    else:
        print('\nPlease, indicate a valid instance')
