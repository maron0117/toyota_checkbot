import requests
from bs4 import BeautifulSoup
import hashlib
import os
import sys

# 設定項目
TARGET_URL = "https://cp.toyota.jp/rentacar/?padid=ag270_fr_sptop_onewayma"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
HASH_FILE = "previous_hash.txt"

def send_discord_notify(message):
    """Discordに通知を送る関数"""
    data = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def get_page_hash():
    """ページのテキストを取得し、ハッシュ値を生成する関数"""
    try:
        response = requests.get(TARGET_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        page_text = soup.get_text(strip=True)
        return hashlib.md5(page_text.encode('utf-8')).hexdigest()
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def main():
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URLが設定されていません。")
        sys.exit(1)

    # ★↓↓テスト用の通知↓↓★
    # Discordの連携が成功しているか確認するためのテスト送信です
    send_discord_notify("✅ テスト通知です！ボットのプログラムが正常に実行されました。")
    # ★↑↑テスト用の通知↑↑★

    current_hash = get_page_hash()
    if not current_hash:
        sys.exit(1)

    # 過去のハッシュ値を読み込む
    previous_hash = ""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            previous_hash = f.read().strip()

    # 比較して更新を検知
    if previous_hash and current_hash != previous_hash:
        print("更新を検知しました！")
        send_discord_notify(f"@everyone \n🚗 **片道GOのページが更新されました！**\nいますぐ確認してください: {TARGET_URL}")
    else:
        print("更新はありません。")

    # 新しいハッシュ値をファイルに書き込む
    with open(HASH_FILE, "w") as f:
        f.write(current_hash)

if __name__ == "__main__":
    main()
