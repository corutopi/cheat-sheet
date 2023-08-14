# Docker Cheat Sheet

## イメージビルド
```bash
docker build -t ${imange-name}:${tag-name} .
```

## コンテナを対話形式で起動
```bash
docker run --rm --entrypoint="" -it ${image-name}:${tag-name} /bin/bash
```

## 起動中のコンテナにSSHっぽく接続
```bash
docker exec -it ${container-name} /bin/bash
```