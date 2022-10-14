import boto3

ssm_client = boto3.client('ssm')

parameter_filters = [{'Key': 'Name', 'Option': 'Contains', 'Values': ['admin-api-dev-69d3f3ad'], }]
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
        print(parameter_dict)


'''def db_parameters_list():
    paginator = ssm_client.get_paginator('describe_parameters')
    response_iterator = paginator.paginate(ParameterFilters=parameter_filters,
                                           PaginationConfig={'PageSize': 10, 'MaxItems': 20})
    parameter_dict = dict()
    for page in response_iterator['Parameters']:
        parameter_dict.update(page)
    print(parameter_dict)


    # return parameter_dict


def db_parameters_list():
    marker = None
    initial_page = True
    while marker is not None or initial_page:
        response = ssm_client.describe_parameters(NextToken=marker,
                                                  ParameterFilters=parameter_filters) if marker is not None else ssm_client.describe_parameters(
            ParameterFilters=parameter_filters)
        parameter_dict = dict()
        for x in response['Parameters']:
            for i in parameters_names:
                if x['Name'].endswith(i):
                    get_parameter = ssm_client.get_parameter(Name=x['Name'], WithDecryption=True)['Parameter']
                    parameter_dict.update({i: get_parameter['Value']})
                else:
                    continue
        marker = response['NextToken'] if 'NextToken' in response else None
        initial_page = False
    return parameter_dict'''

db_parameters_list()
