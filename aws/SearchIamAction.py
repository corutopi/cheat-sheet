"""
requirements:
    boto3
"""

import boto3
import json
import pprint

client = boto3.client('iam')

# IAM Role
roles = client.list_roles()
roles = [r['RoleName'] for r in roles['Roles']]
pprint.pprint(roles)
for role in roles:
    # インラインポリシー
    role_policies = client.list_role_policies(RoleName=role)['PolicyNames']
    
    print(role)
    pprint.pprint(role_policies)
    
    for role_policy in role_policies:
        pprint.pprint(client.get_role_policy(RoleName=role, PolicyName=role_policy))
        

# todo: IAM User

# todo: (IAM Policy)