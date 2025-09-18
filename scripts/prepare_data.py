#!/usr/bin/env python3
import argparse, json, os, re
from pathlib import Path
import pandas as pd
from tqdm import tqdm

def chunk_text(text, chunk_size=800, overlap=120):
    text = re.sub(r'\s+', ' ', (text or '')).strip()
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n: break
        start = max(0, end - overlap)
    return chunks

def normalize_row(row):
    return {
        "id": str(row.get("id") or ""),
        "title": str(row.get("title") or ""),
        "section": str(row.get("section") or ""),
        "page": str(row.get("page") or ""),
        "content": str(row.get("content") or ""),
    }

def process_csv(path, out_dir, chunk_size, overlap):
    df = pd.read_csv(path)
    required = ["content"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"{path} 缺少必要欄位: {col}")
    out_path = out_dir / (path.stem + ".jsonl")
    with out_path.open("w", encoding="utf-8") as f:
        for _, row in tqdm(df.iterrows(), total=len(df), desc=f"CSV {path.name}"):
            r = normalize_row(row)
            for i, ch in enumerate(chunk_text(r["content"], chunk_size, overlap)):
                item = {
                    "meta": {k:v for k,v in r.items() if k!="content"},
                    "text": ch
                }
                f.write(json.dumps(item, ensure_ascii=False)+"\n")

def process_txt(path, out_dir, chunk_size, overlap):
    text = path.read_text(encoding="utf-8", errors="ignore")
    out_path = out_dir / (path.stem + ".jsonl")
    with out_path.open("w", encoding="utf-8") as f:
        for i, ch in enumerate(chunk_text(text, chunk_size, overlap)):
            item = {"meta": {"title": path.stem}, "text": ch}
            f.write(json.dumps(item, ensure_ascii=False)+"\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="data/raw")
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--chunk", type=int, default=800)
    ap.add_argument("--overlap", type=int, default=120)
    args = ap.parse_args()

    src = Path(args.src); out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    files = list(src.glob("**/*.csv")) + list(src.glob("**/*.txt"))
    if not files:
        print("⚠️ 未找到 raw 檔案（支援 csv/txt）。請放到 data/raw/ 後再執行。")
        return

    for p in files:
        if p.suffix.lower()==".csv":
            process_csv(p, out, args.chunk, args.overlap)
        else:
            process_txt(p, out, args.chunk, args.overlap)
    print(f"✅ 完成，輸出在 {out}")

if __name__ == "__main__":
    main()
