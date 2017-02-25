#!/bin/bash -e

AWS_REGION="--region ap-southeast-2"
hopper_stack_name=Hopper
s3_config_path=${1}
echo $(date -u +"%Y-%m-%dT%H:%M:%S") Deleting ${hopper_stack_name}.
aws cloudformation ${AWS_REGION} delete-stack --stack-name ${hopper_stack_name}
aws s3 rm ${AWS_REGION} s3://${s3_config_path}/hopper.zip
aws cloudformation ${AWS_REGION} wait stack-delete-complete --stack-name ${hopper_stack_name}
