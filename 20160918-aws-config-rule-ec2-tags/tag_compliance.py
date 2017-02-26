import json
import re

import boto3

config_service = boto3.client('config')
sns_service = boto3.client('sns')

ec2_regex = re.compile('^[a-z]+-[a-z0-9]+-[a-z-0-9]+[-a-z]*'),

ROLES = ('web', 'app', 'jumpbox', 'proxy', 'firewall', )
ENVIRONMENTS = ('shared', 'build', 'nonprod', 'prod', )


class ConfigResult(object):
    COMPLIANT = 'COMPLIANT'
    NON_COMPLIANT = 'NON_COMPLIANT'


def handler(event, context):
    invoking_event = event['invokingEvent']
    config_item = json.loads(invoking_event)['configurationItem']
    topic_arn = json.loads(event['ruleParameters'])['notification_topic_arn']
    resource_type = config_item['resourceType']

    if config_item['configurationItemStatus'] == 'ResourceDeleted' or \
       resource_type != 'AWS::EC2::Instance':
        return

    # the resource evaluation map, tells config the state of the resource
    # at the current point in time
    evaluation = {
        'ComplianceResourceType': config_item['resourceType'],
        'ComplianceResourceId': config_item['resourceId'],
        'ComplianceType': ConfigResult.NON_COMPLIANT,
        'OrderingTimestamp': config_item['configurationItemCaptureTime']
    }

    resource_id = config_item['resourceId']
    if 'Name' not in config_item['tags']:
        sns_message = 'This is a notification that the resource with ID' + \
            resource_id + 'has no Name tag.' + \
            'Please review and update the resource.\n'
    else:
        resource_name = config_item['tags']['Name']
        sns_message = 'ID: %s\nName Tag: %s\nRequired Format: %s\n' % \
            (resource_id, resource_name, ec2_regex) + \
            'The above resource does not follow the correct tag format,' + \
            'please review and update the resource.'
        # Check the name meets the regex rules for that resource
        resource_type = resource_regex_dict[resource_type]
        match_found = bool(resource_type.match(resource_name))
        resource_sections = resource_name.split('-')
        if match_found and len(resource_sections) > 2 and \
           resource_sections[0] in ROLES and \
           resource_sections[2] in ENVIRONMENTS:
            evaluation['ComplianceType'] = ConfigResult.COMPLIANT

    if evaluation['ComplianceType'] == ConfigResult.NON_COMPLIANT:
        resource_id = config_item['resourceId']
        sns_subject = 'Notification of non-compliant resource,' + \
            'Type: %s, ID: %s' % (resource_type.split('::')[-1], resource_id)
        sns_service.publish(
            TopicArn=topic_arn, Message=sns_message, Subject=sns_subject
        )

    config_service.put_evaluations(
        Evaluations=[evaluation], ResultToken=event['resultToken']
    )
    return evaluation['ComplianceType']
