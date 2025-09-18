#!/usr/bin/env python3
import argparse, json, os, time
from pathlib import Path
from dotenv import load_dotenv
import requests
from tqdm import tqdm

load_dotenv()

DIFY_HOST = os.getenv("DIFY_HOST", "http://localhost")
API_KEY = os.getenv("DIFY_API_KEY", "")
DEFAULT_KB = os.getenv("DIFY_KB_ID", "")

def create_doc(dataset_id, text, title="chunk", metadata=None):
    # 可能因版本不同略有差異，若 404 請參考 Dify 最新文件調整路徑
    url = f"{DIFY_HOST}/v1/datasets/{dataset_id}/document/create_by_text"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "text": text,
        "title": title,
        "meta": metadata or {},
        "indexing_technique": "high_quality",
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    if r.status_code >= 300:
        raise RuntimeError(f"Upload failed: {r.status_code} {r.text}")
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", default=DEFAULT_KB, help="Dify 知識庫（Datasets）ID")
    ap.add_argument("--glob", default="data/processed/*.jsonl")
    ap.add_argument("--sleep", type=float, default=0.2, help="請求間隔秒數")
    args = ap.parse_args()

    if not API_KEY:
        raise SystemExit("請先在 .env 設定 DIFY_API_KEY")
    if not args.kb:
        raise SystemExit("請提供 --kb 或在 .env 設定 DIFY_KB_ID")

    files = list(Path().glob(args.glob))
    if not files:
        print("⚠️ 找不到處理後檔案；請先跑 prepare_data.py")
        return

    for path in files:
        with path.open("r", encoding="utf-8") as f:
            for line in tqdm(f, desc=f"Uploading {path.name}"):
                obj = json.loads(line)
                title = (obj.get("meta") or {}).get("title") or path.stem
                metadata = obj.get("meta") or {}
                create_doc(args.kb, obj["text"], title=title, metadata=metadata)
                time.sleep(args.sleep)
    print("✅ 全部段落已送出（請到 Dify 後台檢查處理狀態）。")

if __name__ == "__main__":
    main()
