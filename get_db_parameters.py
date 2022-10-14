import boto3
from get_db_instance import search_db_instance

ssm_client = boto3.client('ssm')

instance_info = search_db_instance()

parameter_filters = [{'Key': 'Name', 'Option': 'Contains', 'Values': [instance_info['db_identifier']]}]
parameters_names = {'RDS_DATABASE_HOST', 'RDS_DEFAULT_DATABASE_NAME', 'RDS_DATABASE_PORT', 'ROOT_PASSWORD'}


def db_parameters_list():
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


db_parameters_list()
