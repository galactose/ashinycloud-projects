#!/bin/bash -ex

#~/.aws/credentials
#[profile-name]
#aws_access_key_id = <KEYID>
#aws_secret_access_key = <SECRETKEYID>

#~/.aws/config
#[profile profile-name]
#mfa_serial = <MFAARN>
#output = json
#region = ap-southeast-2
#role_arn = <ROLE_ARN>
#s3 =
#    signature_version = s3v4
#source_profile = <CREDSPROFILE>

export AWS_REGION=your-region-here
export AWS_PROFILE=your-cli-access-profile-here

# Get your user ARN
aws iam get-user --query 'User.Arn'

# Get the list of key pairs available to an account sorted alphabetically
aws ec2 describe-key-pairs \
  --query 'KeyPairs[*].[KeyName] | sort(@)' \
  --output text

# List account role ARNs
aws iam list-roles --query 'Roles[Arn]' --output text

# List instance ID's by name tag using filter
aws ec2 describe-instances \
  --filter 'Name=tag:Name,Values=instance-name-here' \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text

# Create a volume from a snapshot ID and get the resulting volume ID
aws ec2 create-volume \
  --snapshot-id snap-id \
  --encrypted true \
  --availability-zone az \
  --query VolumeId \
  --output test

# List the available set of server cert ARNs
aws iam list-server-certificates \
  --query 'ServerCertificateMetadataList[*][Arn]' \
  --output text

# Get the first Cloudformation stack and return a specific output key value
aws cloudformation describe-stacks \
  --query "Stacks[0].Outputs[?OutputKey=='key'].OutputValue"

# Get AMIs that are available and have a substring in their name
aws ec2 describe-images \
  --filters Name=name,Values=*-name-contains-* Name=state,Values=available \
  --query 'Images[*].[ImageId,Name] | sort(@)' \
  --output text

# Get available Cloudformation stacks, sort by age
aws cloudformation list-stacks \
  --query 'StackSummaries[?StackStatus==`CREATE_COMPLETE`].[CreationTime,StackName] | sort(@)' \
  --output text

# Get the private IPs of a set of instances based on a shared tag*
# *only useful if you're expecting the instance to have only one ENI.
aws ec2 describe-instances \
  --filter Name=tag:Name,Values=tag \
  --query 'Reservations[*].Instances[].[NetworkInterfaces[0].PrivateIpAddress]' \
  --output text

# List record sets
aws route53 list-resource-record-sets \
  --hosted-zone-id id \
  --query 'ResourceRecordSets[*].[Name]'

# Get the availability zones of VPC subnets
aws ec2 describe-subnets \
  --query 'Subnets[*].[VpcId,SubnetId,AvailabilityZone]' --output text

# Get the volume ID of an instance knowing the mount point and instance ID
aws ec2 describe-volumes \
  --filters Name=attachment.instance-id,Values=instance-id \
  --query 'Volumes[*].Attachments[?Device==`/dev/sdh`].VolumeId' \
  --output text

# Get the userdata of an EC2 instance
aws ec2 describe-instance-attribute \
  --attribue userData \
  --instance-id instance-id \
  --query 'Userdata.Value' \
  --output text | base64 --decode

# Get account security groups and format the output as JSON
aws ec2 describe-security-groups \
  --query SecurityGroups[*].{ID: GroupId} \
  --output text

# Get the first security group ID alphabetically
aws ec2 describe-security-groups \
  --query 'SecurityGroups[*].GroupId | sort(@) | [0]' \
  --output text
