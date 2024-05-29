
- フォルダ初期化
    ```bash
    git init
    ```
- リポジトリ関連
    ```bash
    # リモートリポジトリと接続
    git remote add origin ${URL}
    # 接続中のリモートリポジトリのURL確認
    git remote -v
    ``` 
- ブランチ関連
    ```bash
    # すべてのブランチを表示
    git branch -a
    # リモートトラッキングブランチを表示
    git branch -vv
    # リモートトラッキングブランチを変更
    git branch --set-upstream-to=origin/${branch-name}
    git branch -u origin/${branch-name}
    # ブランチを作成
    ## 現在のブランチから複製
    git branch ${branch-name}
    # ブランチを削除
    git branch -d ${branch-name}
    ```
- Diff
    ```bash
    # addした後に差分を見る
    git diff --cached ${file-name}
    ```
- コミット
    ```bash
    # 基本
    git commit --author "${user-name}<${user-mail-address}>" -m "${comment}"
    ```
- マージ
    ```bash
    # マージ時にコミットしない、fast-forwardしない
    git merge --no-commit --no-ff ${from-branch-name}
    ```
- Pull
    ```bash
    # リモートブランチの削除を反映
    git fetch --prune
    ```
- Push
    ```bash
    # リモートブランが指定されていないときのPush
    ## ローカルと同じ名称のリモートブランチを作成してPush
    git push -u origin ${local-branch-name}
    ```
- 入力した ID/Pass を記憶する
    ```bash
    git config credential.helper store
    ```