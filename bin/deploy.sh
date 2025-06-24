#!/bin/bash

# エラーが発生したら即座に終了
set -e

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# デプロイ先の設定
REMOTE_HOST="baby"
REMOTE_DIR="/home/baby"

# デプロイ実行
echo "デプロイを開始します..."
rsync -av "$PROJECT_ROOT/" "$REMOTE_HOST:$REMOTE_DIR/" --exclude='.git'

echo "デプロイが完了しました。" 