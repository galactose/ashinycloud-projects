# -*- coding: utf-8 -*-

import json
import boto3

from botocore.exceptions import ClientError


class STS(object):
    """
    STS: Object to manage the persistence of authentication over multiple
        runs of an automation script. When testing a script this will
        save having to input an MFA token multiple times when using
        an account that requires it.
    """

    def __init__(self, role_arn, temporary_credentials_path, mfa_arn):
        self.temp_creds_path = temporary_credentials_path
        self.mfa_arn = mfa_arn
        self.role_arn = role_arn

    def get_temporary_session(self):
        """
        get_temporary_session: checks the temporary credentials stored
            on disk, if they fail to authenticate re-attempt to assume
            the role. The credentials requested last 15 minutes. For
            debugging purposes these can be persisted for up to an hour.
        """

        try:
            with open(self.temp_creds_path, 'r') as tmp_creds:
                credentials = json.loads(tmp_creds.read())
                client = boto3.client(
                    "sts",
                    aws_access_key_id=credentials['AccessKeyId'],
                    aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken']
                )
                _ = client.get_caller_identity()["Account"]
        except (IOError, ClientError):
            response = boto3.client('sts').assume_role(
                DurationSeconds=900,
                RoleArn=self.role_arn,
                RoleSessionName='multi-account automation script',
                SerialNumber=self.mfa_arn,
                TokenCode=raw_input('MFA_Token:')
            )
            credentials = response['Credentials']
            with open(self.temp_creds_path, 'w') as tmp_creds:
                tmp_creds.write(json.dumps({
                    'AccessKeyId': credentials['AccessKeyId'],
                    'SecretAccessKey': credentials['SecretAccessKey'],
                    'SessionToken': credentials['SessionToken']}))

        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )
