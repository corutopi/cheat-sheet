"""
description:
    使用されていないログストリームをすべて削除する

requirements:
    boto3
    tqdm

todo:
    -
"""

import time
import pprint

import boto3
from botocore.exceptions import ClientError
import tqdm

client = boto3.client('logs', region_name='ap-northeast-1')

# dlg = client.describe_log_groups(limit=2)
# pprint.pprint(dlg)
# log_groups = [l['logGroupName'] for l in dlg['logGroups']]

log_groups = []
NOT_USED_CHAR_FOR_TOKEN = '%'
next_token_log_groups = NOT_USED_CHAR_FOR_TOKEN
while next_token_log_groups:
    if next_token_log_groups == NOT_USED_CHAR_FOR_TOKEN:
        dlg = client.describe_log_groups(limit=2)
    else:
        dlg = client.describe_log_groups(limit=2, nextToken=next_token_log_groups)
    next_token_log_groups = dlg.get('nextToken', None)        
    log_groups += [l['logGroupName'] for l in dlg['logGroups']]

print(log_groups)
result = []

for log_group in log_groups:
    next_token_log_streams = NOT_USED_CHAR_FOR_TOKEN
    cnt = 0
    print(f'LogGroup: {log_group} is processing...')
    while True:
        try:
            while next_token_log_streams:
                if next_token_log_streams == NOT_USED_CHAR_FOR_TOKEN:
                    log_streams = client.describe_log_streams(logGroupName=log_group)
                else:
                    log_streams = client.describe_log_streams(logGroupName=log_group, nextToken=next_token_log_streams)
                next_token_log_streams = log_streams.get('nextToken', None)
                for log_stream in tqdm.tqdm(log_streams['logStreams']):
                    if log_stream['storedBytes'] == 0:
                        client.delete_log_stream(logGroupName=log_group, logStreamName=log_stream['logStreamName'])
                        cnt += 1 
                print(f'{log_group}:: {cnt} LogStream deleted.')
            if cnt > 0:
                result.append({"logGroupName": log_group, "deleteLogStreamCount": cnt})
        except ClientError as e:
            # ログストリーム削除の連続実行で ThrottlingException が発生したらクールダウンさせる
            print(e)
            print('ThrottlingException cooling time exec.')
            time.sleep(10)
        else:
            break

pprint.pprint(result)
    

