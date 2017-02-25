#!/bin/bash -e

AWS_REGION="--region ap-southeast-2"
s3_config_path=${1}
lambda_function_name=${2}

zip -r9 hopper.zip handler.py
aws s3 cp ${AWS_REGION} ${zipfile} hopper.zip s3://${s3_config_path}/
hopper_stack_name=Hopper

cat << EOF > params.json
[
{"ParameterKey":"ConfigBucketName","ParameterValue":"${s3_config_path}"},
{"ParameterKey":"LambdaFunctionName","ParameterValue":"${lambda_function_name}"}
]
EOF

echo $(date -u +"%Y-%m-%dT%H:%M:%S") Creating ${hopper_stack_name}.
aws ${AWS_REGION} cloudformation create-stack \
  --capabilities CAPABILITY_IAM \
  --stack-name ${hopper_stack_name} \
  --template-body file://Hopper.yml \
  --parameters file://params.json
aws ${AWS_REGION} cloudformation wait stack-create-complete --stack-name ${hopper_stack_name}

rm params.json
rm hopper.zip
