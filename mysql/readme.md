### バージョン確認
```bash
mysql --version
```

### 接続
```bash
mysql -u ${user-name} -h ${db-domain} -P ${port-num} -e '${SQL}'        # -eオプションを消すと対話モード
mysql -u root -h localhost -P 3306
```

### ユーザー情報
```sql
-- 現在のユーザー
SELECT user();
SELECT current_user();
-- ユーザー一覧
SELECT Host, User FROM mysql.user;
-- 現在のユーザーの権限
SHOW grants;
```

https://tcd-theme.com/2021/10/wordpress-markdown.html