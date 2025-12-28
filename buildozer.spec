[app]

# アプリ名
title = SearchPilot

# パッケージ名（一意な名前にする）
package.name = searchpilot
package.domain = org.searchpilot

# メインのPythonファイル
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# バージョン情報
version = 3.2
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# 必要なPythonパッケージ
requirements = python3,kivy,requests

# Androidの権限
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# アプリのアイコン（オプション）
#icon.filename = %(source.dir)s/data/icon.png

# スプラッシュスクリーン（オプション）
#presplash.filename = %(source.dir)s/data/presplash.png

# 画面の向き（portrait=縦、landscape=横、sensor=自動）
orientation = portrait

# サポートするAndroidバージョン
android.minapi = 21
android.api = 33
android.ndk = 25b

# アーキテクチャ（arm64-v8aは最新、armeabi-v7aは古い端末用）
android.archs = arm64-v8a,armeabi-v7a

# fullscreen = 0にすることでステータスバー表示
fullscreen = 0

# Android build mode (debug または release)
android.release_artifact = apk

# ログレベル
log_level = 2

# Buildozerの警告を無視
warn_on_root = 1

[buildozer]

# ビルドディレクトリ
bin_dir = ./bin
build_dir = ./.buildozer

# ログファイル
log_level = 2
