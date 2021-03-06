# This will connnect to an AWS account and provide a report of resources that
# are not in compliance. 

from __future__ import print_function
import os
import sys
import logging
import traceback
import time
# import pprint
import boto3

LOG_LEVELS = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10}

AWS_REGION = ''
CONFIG_RULE = ''


def init_logging():
    # Setup loggin because debugging with print can get ugly.
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('nose').setLevel(logging.WARNING)

    return logger


def setup_local_logging(logger, log_level = 'INFO'):
    # Set the Logger so if running locally, it will print out to the main screen.
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if log_level in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[log_level])
    else:
        logger.setLevel(LOG_LEVELS['INFO'])

    return logger


def set_log_level(logger, log_level = 'INFO'):
    # There is some stuff that needs to go here.
    if log_level in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[log_level])
    else:
        logger.setLevel(LOG_LEVELS['INFO'])

    return logger


def process_global_vars():
    logger.info("Processing variables from environment.")
    try:
        global AWS_REGION
        AWS_REGION = os.environ.get('AWS_REGION', AWS_REGION)
        global CONFIG_RULE
        CONFIG_RULE = os.environ.get('CONFIG_RULE', '')
        if CONFIG_RULE is '':
            logger.error("CONFIG_RULE must be set.")
            sys.exit(1)
        logger.debug("Completed execution of process_global_vars")
    except SystemExit:
        sys.exit(1)
    except:
        logger.error("Unexpected error!\n Stack Trace:", traceback.format_exc())


def get_ec2_instance_details(connection, instance_id):
    response = connection.describe_instances(
        InstanceIds=[
            instance_id,
        ],
    )
    item = response['Reservations'][0]['Instances'][0]
    return item


def get_instance_name(tag_dict):
    name = ''
    for tag in tag_dict:
        if tag['Key'] == 'Name':
            name = tag['Value']
    return name


def lambda_handler(event, context):
    try:
        global logger
        logger = init_logging()
        logger = set_log_level(logger, os.environ.get('log_level', 'INFO'))

        logger.debug("Running function lambda_handler")
        process_global_vars()
        logger.info("Beginning Report Generation")

        logger.debug("Connecting to config service")
        client = boto3.client('config', region_name=AWS_REGION)

        compliance = client.get_compliance_details_by_config_rule(
                ConfigRuleName=CONFIG_RULE,
                ComplianceTypes=[
                    # 'COMPLIANT', 'NON_COMPLIANT', 'NOT_APPLICABLE',
                    'COMPLIANT',
                ],
                Limit=10,
                NextToken=''
        )
        ec2_instances = []
        ec2_client = boto3.client('ec2', region_name=AWS_REGION)
        rds_instances = []
        rds_client = boto3.client('rds', region_name=AWS_REGION)
        # response = client.describe_db_instances(
        #     DBInstanceIdentifier='string',
        #     Filters=[
        #         {
        #             'Name': 'string',
        #             'Values': [
        #                 'string',
        #             ]
        #         },
        #     ],
        #     MaxRecords=123,
        #     Marker='string'
        # )
        count = 0
        while True:
            # logger.debug(count);
            for evalItemIdentifier in compliance['EvaluationResults']:
                count = count + 1
                evalItem = evalItemIdentifier['EvaluationResultIdentifier']['EvaluationResultQualifier']
                # logger.debug("Type: %s ID: %s" % (evalItem['ResourceType'], evalItem['ResourceId']))
                logger.debug("Event: %s" % (evalItem))
                # print("%d:\tType: %s\tID: %s" % (count, evalItem['ResourceType'], evalItem['ResourceId']))
                if evalItem['ResourceType'] == 'AWS::EC2::Instance':
                    ec2_instances.append(get_ec2_instance_details(ec2_client, evalItem['ResourceId']))
                    instance = get_ec2_instance_details(ec2_client, evalItem['ResourceId'])
                    if "Tags" in instance:
                        tags = get_instance_name(instance['Tags'])
                    else:
                        tags = ""
                    print("%s:::%s:::%s:::%s" % (instance['InstanceId'], instance['InstanceType'], tags, instance['KeyName']))
                    time.sleep(1)
                    # pprint.pprint(ec2_instances)
                # elif evalItem['ResourceType'] == 'AWS::RDS::DBInstance':
                    # print("RDS Instance")
                
            if compliance.get("NextToken", None) is None:
                break
            else:
                compliance = client.get_compliance_details_by_config_rule(
                    ConfigRuleName=CONFIG_RULE,
                    ComplianceTypes=[
                        'COMPLIANT',
                        # 'NOT_APPLICABLE',
                    ],
                    Limit=10,
                    NextToken=compliance.get("NextToken")
                )

        # for instance in ec2_instances:
        #     print("%s:::%s:::%s" % (instance['InstanceId'], instance['InstanceType'], get_instance_name(instance['Tags'])))

    except SystemExit:
        logger.error("Exiting")
        sys.exit(1)
    except ValueError:
        exit(1)
    except:
        print ("Unexpected error!\n Stack Trace:", traceback.format_exc())
    exit(0)


if __name__ == "__main__":
    logger = init_logging()
    os.environ['log_level'] = os.environ.get('log_level', "INFO")

    logger = setup_local_logging(logger, os.environ['log_level'])

    event = {'log_level': 'INFO'}
    os.environ['AWS_REGION'] = os.environ.get('AWS_REGION', "us-east-2")


    # Add default level of debug for local execution
    lambda_handler(event, 0)