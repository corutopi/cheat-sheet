"""
description:
    使用されていないログストリームをすべて削除する

requirements:
    boto3
"""

import pprint

import boto3

client = boto3.client('logs', region_name='ap-northeast-1')

dlg = client.describe_log_groups(limit=10)
pprint.pprint(dlg)
log_groups = [l['logGroupName'] for l in dlg['logGroups']]

for log_group in log_groups:
    log_streams = client.describe_log_streams(logGroupName=log_group,limit=10)['logStreams']
    for log_stream in log_streams:
        if log_stream['storedBytes'] == 0:
            client.delete_log_stream(logGroupName=log_group, logStreamName=log_stream['logStreamName'])
            print(f'delete log stream (LogGroup: {log_group}, LogStream:{log_stream["logStreamName"]})')
    break

