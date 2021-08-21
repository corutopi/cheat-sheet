# AWS CheetSheet

## EC2
- Nameタグ一覧取得
```
aws ec2 describe-instances --query 'Reservations[].Instances[].Tags[?Key==`Name`].Value[]'
```

## セキュリティグループ
- グループIDとグループ名
```
aws ec2 describe-security-groups --query 'SecurityGroups[].{GroupName: GroupName, GroupId: GroupId}' # --output table
```
- 使用中(NetworkInterfaceに紐づけられている)のグループ名
```
aws ec2 describe-network-interfaces --query 'NetworkInterfaces[].Groups[].GroupName[]' # --output json | jq '. | unique'
```

## CloudWatchログ
- ロググループ一覧
```
aws logs describe-log-groups --query "logGroups[].arn[]"
```