"""
description:
    IAMリソースから所定のActionを持つリソースを列挙する

requirements:
    boto3
    tqdm

todo:
    -
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

# ログ出力設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)
for h in logger.handlers:
    logger.removeHandler(h)
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s'))
logger.addHandler(_ch)


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
    
    logger.info('check iam roles start.')
    for role in my_progress_bar(roles):
        # インラインポリシー
        role_policies = client.list_role_policies(RoleName=role)['PolicyNames']
        for role_policy in role_policies:
            if hasAction(client.get_role_policy(RoleName=role, PolicyName=role_policy)['PolicyDocument'], target_action):
                target_roles.append(role)
                break
        if role in target_roles : continue
        
        # アタッチポリシー
        attached_policies = client.list_attached_role_policies(RoleName=role)
        for attached_policy in attached_policies['AttachedPolicies']:
            policy = client.get_policy(PolicyArn=attached_policy['PolicyArn'])
            policy_document = client.get_policy_version(
                PolicyArn=attached_policy['PolicyArn'], 
                VersionId=policy['Policy']['DefaultVersionId']
            )['PolicyVersion']['Document']
            if hasAction(policy_document, target_action):
                target_roles.append(role)
                break
    logger.info('check iam roles end.')
    
    # IAM User
    target_users = []
    users = [u['UserName'] for u in client.list_users()['Users']]
    
    logger.info('check iam users start.')
    for user in my_progress_bar(users):
        # インラインポリシー
        user_policies = client.list_user_policies(UserName=user)['PolicyNames']
        for user_policy in user_policies:
            policy = client.get_user_policy(UserName=user, PolicyName=user_policy)
            if hasAction(policy['PolicyDocument'], target_action):
                target_users.append(user)
                break
        if user in target_users: continue
    
        # アタッチポリシー
        attached_policies = client.list_attached_user_policies(UserName=user)
        for attached_policy in attached_policies['AttachedPolicies']:
            policy = client.get_policy(PolicyArn=attached_policy['PolicyArn'])
            policy_document = client.get_policy_version(
                PolicyArn=attached_policy['PolicyArn'], 
                VersionId=policy['Policy']['DefaultVersionId']
            )['PolicyVersion']['Document']
            if hasAction(policy_document, target_action):
                target_users.append(user)
                break
        
        # 所属グループポリシー
        groups = [g['GroupName'] for g in client.list_groups_for_user(UserName=user)['Groups']]
        for group in groups:
            # インラインポリシー
            group_policies = client.list_group_policies(GroupName=group)
            for group_policy in group_policies['PolicyNames']:
                policy = client.get_group_policy(GroupName=group, PolicyName=group_policy)
                if hasAction(policy['PolicyDocument'], target_action):
                    target_users.append(user)
                    break
            if user in target_users: continue
            
            # アタッチポリシー
            attached_policies = client.list_attached_group_policies(GroupName=group)
            for attached_policy in attached_policies['AttachedPolicies']:
                policy = client.get_policy(PolicyArn=attached_policy['PolicyArn'])
                policy_document = client.get_policy_version(
                    PolicyArn=attached_policy['PolicyArn'], 
                    VersionId=policy['Policy']['DefaultVersionId']
                )['PolicyVersion']['Document']
                if hasAction(policy_document, target_action):
                    target_users.append(user)
                    break
    logger.info('check iam users end.')

    re['roles'] = target_roles
    re['users'] = target_users
    # todo: IAM Policy
    return re


if __name__ == '__main__':
    # 引数定義
    parser = argparse.ArgumentParser(
        prog='SearchIamAction',
        description='list iam role and user with the privileges specified in arg',
        )
    parser.add_argument('target_action')
    parser.add_argument('-l', '--logging', action='store', default='True', choices=['True', 'False'], help='when True (default), outputs the processing progress as a log.')
    
    # オプション設定処理
    args = vars(parser.parse_args())
    log_flg = True if args['logging'] != 'False' else False
    logger.setLevel(logging.INFO if args['logging'] != 'False' else logging.WARN)

    # 実出力
    pprint.pprint(main(args['target_action']))
    