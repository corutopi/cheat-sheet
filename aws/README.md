# AWS CheetSheet

## EC2
- Nameタグ一覧取得
```
aws ec2 describe-instances --query 'Reservations[].Instances[].Tags[?Key==`Name`].Value[]'
```
