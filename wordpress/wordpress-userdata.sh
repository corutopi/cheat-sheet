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



# --- for wordpress ---
# ライブラリアップデート
sudo yum update -y

# httpd/php/mariadb のインストール
sudo amazon-linux-extras enable lamp-mariadb10.2-php7.2
sudo yum install -y httpd mariadb-server php php-mysqlnd

# httpdの設定
## 自動起動
sudo systemctl start httpd
sudo systemctl enable httpd
## オレオレ証明書発行
sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/pki/tls/private/localhost.key -out /etc/pki/tls/certs/localhost.crt -subj "/C=JP/ST=Tokyo/L=Chiyoda-ku/O=Example Inc./OU=Web/CN=localhost"
sudo yum install mod_ssl -y
sudo systemctl restart httpd
## httpポート閉鎖(localhostのみ許可)
sudo sed -i 's/Listen 80/Listen 127.0.0.1:80/' /etc/httpd/conf/httpd.conf
sudo systemctl restart httpd

# mariadb(mysql)の設定
TMP_DB_ROOT_PASS='***********'
TMP_DB_WORDPRESS_SCHEMA='********'
TMP_DB_WORDPRESS_USER='********'
TMP_DB_WORDPRESS_PASS='***********'
## 自動起動
sudo systemctl start mariadb
sudo systemctl enable mariadb
## rootパスワード設定
mysql -u root -h localhost -P 3306 -e "ALTER USER 'root'@'localhost' IDENTIFIED BY \"${TMP_DB_ROOT_PASS}\";"
## wordpress用スキーマ,ユーザー作成
mysql -u root -h localhost -P 3306 -p${TMP_DB_ROOT_PASS} -e "CREATE DATABASE ${TMP_DB_WORDPRESS_SCHEMA} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
mysql -u root -h localhost -P 3306 -p${TMP_DB_ROOT_PASS} -e "GRANT ALL PRIVILEGES ON ${TMP_DB_WORDPRESS_SCHEMA}.* TO '${TMP_DB_WORDPRESS_USER}'@'localhost' IDENTIFIED BY \"${TMP_DB_WORDPRESS_PASS}\";"
mysql -u root -h localhost -P 3306 -p${TMP_DB_ROOT_PASS} -e "FLUSH PRIVILEGES;"

# wordpressインストール
cd /var/www/html
sudo wget https://wordpress.org/latest.tar.gz
sudo tar -xzf latest.tar.gz
sudo mv wordpress/* .
sudo rm -rf wordpress latest.tar.gz
sudo chown -R apache:apache /var/www/html
sudo chmod 2775 /var/www/html
find /var/www/html -type d -exec sudo chmod 2775 {} \;
find /var/www/html -type f -exec sudo chmod 0664 {} \;
# ---------------------



# Route53レコード自動更新
TMP_FILE=/opt/route53_change-resource-record-sets.sh
DOMAIN_NAME="*domain-name*"
HOSTED_ZONE_ID="*hostzone-id*"
## Route53更新バッチ作成
echo > ${TMP_FILE}
echo "#!/bin/bash" >> ${TMP_FILE}
echo >> ${TMP_FILE}
echo "DOMAIN_NAME=${DOMAIN_NAME}" >> ${TMP_FILE}
echo "HOSTED_ZONE_ID=${HOSTED_ZONE_ID}" >> ${TMP_FILE}
echo "IP_ADDRESS=\`curl -s http://169.254.169.254/latest/meta-data/public-ipv4\`" >> ${TMP_FILE}
echo '
BATCH_JSON='"'"'{
  "Changes": [
    { "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "'"'"'${DOMAIN_NAME}'"'"'",
        "Type": "A",
        "TTL" : 300,
        "ResourceRecords": [
          { "Value": "'"'"'${IP_ADDRESS}'"'"'" }
        ]
      }
    }
  ]
}'"'"'
' >> ${TMP_FILE}
echo 'aws route53 change-resource-record-sets --hosted-zone-id ${HOSTED_ZONE_ID} --change-batch "${BATCH_JSON}"' >> ${TMP_FILE}
chmod 755 ${TMP_FILE}

## rc.local への登録
chmod 755 /etc/rc.d/rc.local
echo "sh ${TMP_FILE}" >> /etc/rc.d/rc.local

## 初回実行
sh ${TMP_FILE}