# AWS CheetSheet

## EC2
- Nameタグ一覧取得
```
aws ec2 describe-instances --query "Reservations[].Instances[].Tags[?Key=='Name'].Value[]"
```

## セキュリティグループ
- グループIDとグループ名
```
aws ec2 describe-security-groups --query "SecurityGroups[].{GroupName: GroupName, GroupId: GroupId}" # --output table
```
- 使用中(NetworkInterfaceに紐づけられている)のグループ名
```
aws ec2 describe-network-interfaces --query "NetworkInterfaces[].Groups[].GroupName[]" # --output json | jq '. | unique'
```
- 使用中(他のSGでの許可に使用されている)のグループ名
```
@todo
```

## CloudWatchログ
- ロググループ一覧
```
aws logs describe-log-groups --query "logGroups[].arn[]" # --output json | jq 'map(split(":") | .[6])'
```

## ALB / NLB
- LB名一覧
```
aws elbv2 describe-load-balancers --query "LoadBalancers[].LoadBalancerName[]"
```
- LB名からARN取得
```
aws elbv2 describe-load-balancers --query "LoadBalancers[?LoadBalancerName=='lb-name'].LoadBalancerArn[]"
```

## TG
- TG名一覧
```
aws elbv2 describe-target-groups --query "TargetGroups[].TargetGroupName[]"
```
- TG名からARN取得
```
aws elbv2 describe-target-groups --query "TargetGroups[?TargetGroupName=='tg-name'].TargetGroupArn"
```

## Lambda
- Lambda名一覧
```
aws lambda list-functions --query "Functions[].FunctionName"
```
