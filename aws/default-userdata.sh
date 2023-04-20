#!/bin/bash



# よく使うコマンドのインストール
yum -y install jq



# インスタンス名をタグ名に変更
hostnamectl set-hostname $(aws ec2 describe-instances \
    --query 'Reservations[].Instances[].Tags[?Key==`Name`].Value' \
    --filter "Name=instance-id,Values=`curl -s 'http://169.254.169.254/latest/meta-data/instance-id'`" \
    --region `curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed -e 's/.$//'` \
    --output text)



# SSHポート番号変更
TMP_PORT_NUM=XXXX
cp /etc/ssh/sshd_config /etc/ssh/sshd_config_bk
echo Port ${TMP_PORT_NUM} >> /etc/ssh/sshd_config
systemctl restart sshd.service
