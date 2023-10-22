"""
description:
    IAMリソースから所定のActionを持つリソースを列挙する

requirements:
    boto3
    tqdm

todo:
    ログ改善: funcNameが常にmy_loggingになってしまう件
"""

import sys
import argparse
import json
import pprint
import re
import logging
import tqdm

import boto3

client = boto3.client('iam')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s'
    # stream=sys.stdout
    )
log_flg = True
# target_action = 'tag:GetResources'

def my_logging(message: str):
    """
    ログ出力する.
    """
    if not log_flg: return
    logging.log(logging.INFO, message)

def my_progress_bar(tar: list):
    """
    listでforループさせるとプログレスバーが表示されるようにする.
    """
    return tqdm.tqdm(tar) if log_flg else tar
    

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

def main(target_action: str):
    re = dict()
    # IAM Role
    target_roles = []
    roles = client.list_roles()
    roles = [r['RoleName'] for r in roles['Roles']]
    
    my_logging('check iam roles start.')
    for role in my_progress_bar(roles):
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
        
        # print(role)
        # pprint.pprint(attached_policies)
        
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
    my_logging('check iam roles end.')
    
    # todo: IAM User
    target_users = []
    users = [u['UserName'] for u in client.list_users()['Users']]
    
    my_logging('check iam users start.')
    for user in my_progress_bar(users):
        # インラインポリシー
        user_policies = client.list_user_policies(UserName=user)['PolicyNames']
        # pprint.pprint(user_policies)
        for user_policy in user_policies:
            policy = client.get_user_policy(UserName=user, PolicyName=user_policy)
            if hasAction(policy['PolicyDocument'], target_action):
                target_users.append(user)
                break
        if user in target_users: continue
    
        # アタッチポリシー
        attached_policies = client.list_attached_user_policies(UserName=user)
        # pprint.pprint(attached_policies)
        
        for attached_policy in attached_policies['AttachedPolicies']:
            policy = client.get_policy(PolicyArn=attached_policy['PolicyArn'])
            # pprint.pprint(policy)
            policy_document = client.get_policy_version(
                PolicyArn=attached_policy['PolicyArn'], 
                VersionId=policy['Policy']['DefaultVersionId']
            )['PolicyVersion']['Document']
            # pprint.pprint(policy_document)
            if hasAction(policy_document, target_action):
                target_users.append(user)
                break
        
        # 所属グループポリシー
        groups = [g['GroupName'] for g in client.list_groups_for_user(UserName=user)['Groups']]
        # print(f'groups={groups}')
        for group in groups:
            # インラインポリシー
            group_policies = client.list_group_policies(GroupName=group)
            # pprint.pprint(group_policies)
            for group_policy in group_policies['PolicyNames']:
                policy = client.get_group_policy(GroupName=group, PolicyName=group_policy)
                if hasAction(policy['PolicyDocument'], target_action):
                    target_users.append(user)
                    break
            if user in target_users: continue
            
            # アタッチポリシー
            attached_policies = client.list_attached_group_policies(GroupName=group)
            # pprint.pprint(attached_policies)
            
            for attached_policy in attached_policies['AttachedPolicies']:
                policy = client.get_policy(PolicyArn=attached_policy['PolicyArn'])
                # pprint.pprint(policy)
                policy_document = client.get_policy_version(
                    PolicyArn=attached_policy['PolicyArn'], 
                    VersionId=policy['Policy']['DefaultVersionId']
                )['PolicyVersion']['Document']
                # pprint.pprint(policy_document)
                if hasAction(policy_document, target_action):
                    target_users.append(user)
                    break
    my_logging('check iam users end.')

    re['roles'] = target_roles
    re['users'] = target_users
    return re
    # todo: IAM Policy

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        prog='SearchIamAction',
        description='list iam role and user with the privileges specified in arg',
        )
    parser.add_argument('target_action')
    parser.add_argument('-l', '--logging', action='store', default='True', choices=['True', 'False'], help='when True (default), outputs the processing progress as a log.')

    args = vars(parser.parse_args())
    # target_action = args.get('target_action', 'tag:GetResources')
    log_flg = True if args['logging'] != 'False' else False
    
    pprint.pprint(main(args['target_action']))
    