# Python チートシート

---

## 仮想環境の作り方

```powershell
# 仮装環境作成
python -m venv .venv

# 仮想環境有効化
.\.venv\Scripts\activate

# 無効化
## VSCodeでvenv読み込み設定をしている場合はうまく機能しないかも
.\.venv\Scripts\deactivate
```

### VSCode に venv の読み込み設定

```json
{
  "python.venvFolders": [".venv"]
}
```

- 不要かも？

### モジュール一括インストール

```shell
pip install -r requirements.txt
```

### 実行中の Python 環境を確認する

- PowerShell
  ```powershell
  # どっちでも可
  Get-Command python
  python -c "import sys; print(sys.executable)"
  ```

## 参考

https://qiita.com/fiftystorm36/items/b2fd47cf32c7694adc2e
https://qiita.com/startours777/items/2d35f2c6de12071a4c77
https://qiita.com/youichi_io/items/bc9382fdef30ccdaf0bd
