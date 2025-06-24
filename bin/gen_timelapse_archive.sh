#!/bin/bash
set -e

# ==== 基本設定 ====
BASE_DIR="/home/baby/images/"
ARCHIVE_DIR="/tmp/timelapse_archive/"

# ==== 手動指定日（YYYYMMDD形式）を受け取る ====
if [ -z "$1" ]; then
  echo "⚠️ 日付を指定してください（例: 20250614）"
  exit 1
fi

TARGET_DATE="$1"
TARGETDAY_HYPHEN="$(date -d "${TARGET_DATE}" +'%Y-%m-%d')" || {
  echo "⚠️ 無効な日付形式です: ${TARGET_DATE}"
  exit 1
}

TARGET_DIR="${BASE_DIR}"
TAR_PATH="${ARCHIVE_DIR}${TARGETDAY_HYPHEN}.tar.gz"

if [ ! -d "${TARGET_DIR}" ]; then
  echo "⚠️ ターゲットディレクトリが存在しません: ${TARGET_DIR}"
  exit 0
fi

echo "📦 圧縮処理開始: ${TARGET_DIR} → ${TAR_PATH}"
mkdir -p "${ARCHIVE_DIR}"

# ==== 圧縮対象ファイルリスト作成 ====
FILE_LIST=$(find "${TARGET_DIR}" -type f -regextype posix-extended \
  -regex ".*/${TARGET_DATE}_[0-9]{6}\\.jpg" -size +0c)

if [ -z "$FILE_LIST" ]; then
  echo "⚠️ 対象ファイルが存在しません（${TARGET_DATE} のファイル）"
  exit 0
fi

if echo "$FILE_LIST" | tar -czf "${TAR_PATH}" -T - ; then
  echo "✅ 圧縮完了: ${TAR_PATH}"
  echo "$FILE_LIST" | xargs rm -f
  echo "🗑️ 元ファイルを削除しました"
  echo "🧹 古いアーカイブ削除中: ${ARCHIVE_DIR}"
  find "${ARCHIVE_DIR}" -name "*.tar.gz" -type f -mtime +10 -exec rm -v {} \;
else
  echo "❌ 圧縮失敗"
  exit 1
fi
