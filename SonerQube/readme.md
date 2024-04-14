
```
mkdir -p /opt/sonarqube/data && chmod 777 /opt/sonarqube/data
docker run -p 9000:9000 --name sonarqube -d --restart always -v /opt/sonarqube/data:/opt/sonarqube/data sonarqube:lts
```

## 参考
https://zenn.dev/whitecat_22/articles/5affdcb053c860
https://docs.sonarsource.com/sonarqube/latest/setup-and-upgrade/install-the-server/installing-sonarqube-from-docker/
