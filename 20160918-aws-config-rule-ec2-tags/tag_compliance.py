import boto3
import json
import re

from datetime import datetime, timedelta

config_service = boto3.client('config')
sns_service = boto3.client('sns')

ec2_regex = re.compile('^[a-z]+-[a-z0-9]+-[a-z-0-9]+[-a-z]*'),

roles = ('web', 'app', 'jumpbox', 'proxy', 'firewall', )
environments = ('shared', 'build', 'nonprod', 'prod', )


class ConfigResult:
    COMPLIANT = 'COMPLIANT'
    NON_COMPLIANT = 'NON_COMPLIANT'


def handler(event, context):
    configuration_item = json.loads(event['invokingEvent'])['configurationItem']
    topic_arn = json.loads(event['ruleParameters'])['notification_topic_arn']
    resource_type = configuration_item['resourceType']

    if configuration_item['configurationItemStatus'] == 'ResourceDeleted' or \
       resource_type != 'AWS::EC2::Instance':
        return

    # the resource evaluation map, tells config the state of the resource at the
    # current point in time
    evaluation = {
        'ComplianceResourceType': configuration_item['resourceType'],
        'ComplianceResourceId': configuration_item['resourceId'],
        'ComplianceType': ConfigResult.NON_COMPLIANT,
        'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
    }

    resource_id = configuration_item['resourceId']
    if 'Name' not in configuration_item['tags']:
        sns_message = 'This is a notification that the resource with ID' + \
        	resource_id + 'has no Name tag. Please review and update the resource.\n'
    else:
        resource_name = configuration_item['tags']['Name']
        sns_message = 'ID: %s\nName Tag: %s\nRequired Format: %s\n' % \
        	(resource_id, resource_name, ec2_regex) + \
            'The above resource does not follow the correct tag format,' + \
            'please review and update the resource.'
        #Check the name meets the regex rules for that resource
        match_found = bool(resource_regex_dict[resource_type].match(resource_name))
        resource_sections = resource_name.split('-')
        if match_found and len(resource_sections) > 2 and \
           resource_sections[0] in roles and resource_sections[2] in environments:
            evaluation['ComplianceType'] = ConfigResult.COMPLIANT

    if evaluation['ComplianceType'] == ConfigResult.NON_COMPLIANT:
        resource_id = configuration_item['resourceId']
        sns_subject = 'Notification of non-compliant resource,' + \
        	'Type: %s, ID: %s' % (resource_type.split('::')[-1], resource_id)
        sns_service.publish(
        	TopicArn=topic_arn, Message=sns_message, Subject=sns_subject
        )

    result = config_service.put_evaluations(
    	Evaluations=[evaluation], ResultToken=event['resultToken']
    )
    return evaluation['ComplianceType']

