import boto3
from get_db_instance import search_db_instance

# Run this script with the AWS_PROFILE tag and the name of the profile in the .aws/config, for example:
# AWS_PROFILE=infradev
ssm_client = boto3.client('ssm')
# Comment previous line and uncomment the following lines that contains the values from session and client,
# add the region to execute this script in the tf-bastion, for example: region_name='us-east-1'
# session = boto3.Session(region_name='region')
# ssm_client = session.client('ssm')

instance_info = search_db_instance()

parameter_filters = [{'Key': 'Name', 'Option': 'Contains', 'Values': [instance_info['db_identifier']]}]
parameters_names = {'RDS_DATABASE_HOST', 'RDS_DEFAULT_DATABASE_NAME', 'RDS_DATABASE_PORT', 'ROOT_PASSWORD'}


def db_parameters_dict():
    paginator = ssm_client.get_paginator('describe_parameters')
    response_iterator = paginator.paginate(ParameterFilters=parameter_filters,
                                           PaginationConfig={'PageSize': 10, 'MaxItems': 20})
    parameter_dict = dict()
    for page in response_iterator:
        for x in page['Parameters']:
            if x['Name'].rsplit('/', 1)[-1] in parameters_names:
                get_parameter = ssm_client.get_parameter(Name=x['Name'], WithDecryption=True)['Parameter']
                parameter_dict.update({x['Name'].rsplit('/', 1)[-1]: get_parameter['Value']})
            else:
                continue
    return parameter_dict


db_parameters_dict()
