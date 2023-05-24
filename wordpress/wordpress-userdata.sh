#!/bin/bash
# AWS EC2(ami-052c9af0c988f8bbd) で検証



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



# Route53レコード自動更新バッチ作成
TMP_FILE=/opt/route53_change-resource-record-sets.sh
TMP_DOMAIN_NAME="*domain-name*"
TMP_HOSTED_ZONE_ID="*hostzone-id*"
## Route53更新バッチ作成
echo > ${TMP_FILE}
echo '#!/bin/bash' >> ${TMP_FILE}
echo >> ${TMP_FILE}
echo "DOMAIN_NAME=${TMP_DOMAIN_NAME}" >> ${TMP_FILE}
echo "HOSTED_ZONE_ID=${TMP_HOSTED_ZONE_ID}" >> ${TMP_FILE}
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
sleep 30    # DNS設定完了まで待機



# httpdの設定
DOMAIN_NAME="********"
MAIL_ADDRESS="********"
## インストール
sudo yum install -y httpd
## 自動起動
sudo systemctl start httpd
sudo systemctl enable httpd
## 証明書発行(Lets Encrypt)
sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm -y
sudo yum-config-manager --enable rhui-REGION-rhel-server-extras rhui-REGION-rhel-server-optional
sudo yum install certbot -y
sudo certbot certonly --webroot -w /var/www/html -d ${DOMAIN_NAME} --email ${MAIL_ADDRESS} --agree-tos --no-eff-email
## mod_ssl 導入
sudo yum install mod_ssl -y
sudo sed -i 's@^SSLCertificateFile.*$@SSLCertificateFile /etc/letsencrypt/live/blog.super-solt.com/cert.pem@' /etc/httpd/conf.d/ssl.conf
sudo sed -i 's@^SSLCertificateKeyFile.*$@SSLCertificateKeyFile /etc/letsencrypt/live/blog.super-solt.com/privkey.pem@' /etc/httpd/conf.d/ssl.conf
sudo sed -i 's@^#SSLCertificateChainFile.*$@SSLCertificateChainFile /etc/letsencrypt/live/blog.super-solt.com/fullchain.pem@' /etc/httpd/conf.d/ssl.conf
## httpポートリダイレクト設定
echo "RewriteEngine on" > /etc/httpd/conf.d/vhost.conf
echo "" >> /etc/httpd/conf.d/vhost.conf
echo "<VirtualHost *:80>" >> /etc/httpd/conf.d/vhost.conf
echo "  ServerName any" >> /etc/httpd/conf.d/vhost.conf
echo "  RewriteCond %{HTTPS} off" >> /etc/httpd/conf.d/vhost.conf
echo "  RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]" >> /etc/httpd/conf.d/vhost.conf
echo "</VirtualHost>" >> /etc/httpd/conf.d/vhost.conf
echo "" >> /etc/httpd/conf.d/vhost.conf
## サーバー再起動
sudo systemctl restart httpd
# -----------------------
# ## オレオレ証明書発行
# sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/pki/tls/private/localhost.key -out /etc/pki/tls/certs/localhost.crt -subj "/C=JP/ST=Tokyo/L=Chiyoda-ku/O=Example Inc./OU=Web/CN=localhost"
# sudo yum install mod_ssl -y
# sudo systemctl restart httpd
# ## httpポート閉鎖(localhostのみ許可)
# sudo sed -i 's/Listen 80/Listen 127.0.0.1:80/' /etc/httpd/conf/httpd.conf
# sudo systemctl restart httpd
# -----------------------



# mariadb(mysql)の設定
TMP_DB_ROOT_PASS='********'
TMP_DB_WORDPRESS_SCHEMA='********'
TMP_DB_WORDPRESS_USER='********'
TMP_DB_WORDPRESS_PASS='********'
## インストール
sudo amazon-linux-extras enable mariadb10.5
sudo yum install -y httpd mariadb-server
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
## php インストール
sudo amazon-linux-extras disable php8.0
sudo amazon-linux-extras enable php8.2
sudo yum install -y php php-mysqlnd
### サーバー再起動
sudo systemctl restart httpd
## wordpress 展開
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
