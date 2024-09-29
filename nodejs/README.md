### npm install

```bash
# package.json に定義されているすべての依存関係をインストール
npm install

# パッケージを追加
npm install ${package-name}

# パッケージをバージョン指定して追加
npm install ${package-name}@${package-version:9.9.9}

# ローカル環境でだけ利用するパッケージのインストール(DevDependencies)
npm install ${package-name} --save-dev
npm i ${package-name} -D   # 短縮系

# パッケージを削除
npm uninstall ${package-name}

# パッケージを更新

```
