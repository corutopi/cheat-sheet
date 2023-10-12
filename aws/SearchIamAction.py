"""
description:
    IAMリソースから所定のActionを持つリソースを列挙する

requirements:
    boto3
"""

import json
import pprint
import re

import boto3

client = boto3.client('iam')
target_action = 'tag:GetResources'

def listnize(obj) -> list:
    """
    obj を list にして返す.
    """
    return obj if isinstance(obj, list) else [obj]

def hasAction(document: dict, action: str) -> bool:
    """
    IAMポリシードキュメントが指定された action を許可しているかを返す.
    """
    statements = listnize(document['Statement'])
    for stm in statements:
        if stm['Effect'] == 'Deny': continue
        actions = listnize(stm['Action'])
        for act in actions:
            if re.search("^{}$".format(act.replace("*", ".*")), action):
                return True
    return False

# IAM Role
target_roles = []
roles = client.list_roles()
roles = [r['RoleName'] for r in roles['Roles']]
pprint.pprint(roles)
for role in roles:
    # インラインポリシー
    role_policies = client.list_role_policies(RoleName=role)['PolicyNames']
    
    # print(role)
    # pprint.pprint(role_policies)
    
    for role_policy in role_policies:
        if hasAction(client.get_role_policy(RoleName=role, PolicyName=role_policy)['PolicyDocument'], target_action):
            target_roles.append(role)
            break
    if role in target_roles : continue
    
    # アタッチポリシー
    attached_policies = client.list_attached_role_policies(RoleName=role)
    
    print(role)
    pprint.pprint(attached_policies)
    
    for attached_policy in attached_policies['AttachedPolicies']:
        policy = client.get_policy(PolicyArn=attached_policy['PolicyArn'])
        # pprint.pprint(policy)
        policy_document = client.get_policy_version(
            PolicyArn=attached_policy['PolicyArn'], 
            VersionId=policy['Policy']['DefaultVersionId']
        )['PolicyVersion']['Document']
        # pprint.pprint(policy_document)
        if hasAction(policy_document, target_action):
            target_roles.append(role)
            break
    
print('============================')
pprint.pprint(target_roles)

# todo: IAM User

# todo: (IAM Policy)