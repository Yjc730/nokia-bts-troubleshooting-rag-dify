# Nokia 基地台錯誤排除問答平台（Dify + Ollama + RAG） — Starter

這是 **Week 1 可重現 & 資料入庫** 的起始專案骨架。跟著下面步驟，你能：
1) 建立可重現的目錄與環境
2) 將 `data/raw/` 的原始檔切成段落到 `data/processed/`
3)（選配）把段落批量上傳到 Dify 知識庫（需填好 .env 參數）

---

## 快速開始

```bash
# 0) 下載後解壓並進入資料夾
cd nokia-bts-troubleshooting-rag-dify

# 1) 建立虛擬環境（可選）
python3 -m venv .venv && source .venv/bin/activate

# 2) 安裝套件
pip install -r requirements.txt

# 3) 準備環境變數
cp .env.example .env
# 編輯 .env，填入你的 Dify 主機、API Key、知識庫 ID 等

# 4) 放資料到 data/raw/
# 支援 csv / txt 檔。CSV 需包含欄位：id,title,section,page,content（可只放 content 與 id）

# 5) 前處理（切段與正規化）
python scripts/prepare_data.py --src data/raw --out data/processed --chunk 800 --overlap 120

# 6)（選配）上傳到 Dify 知識庫
python scripts/push_kb.py --kb $DIFY_KB_ID --glob "data/processed/*.jsonl"
```

---

## 專案結構
```
nokia-bts-troubleshooting-rag-dify/
├─ README.md
├─ .env.example              # 複製成 .env 後填入值
├─ requirements.txt
├─ docker-compose.yml        # 參考：若你要一鍵起 Dify + Ollama
├─ data/
│  ├─ raw/                   # 放原始資料（csv/txt）
│  └─ processed/             # 產生的段落 jsonl
├─ scripts/
│  ├─ prepare_data.py        # 切段/正規化
│  └─ push_kb.py             # 上傳段落到 Dify 知識庫（REST API）
└─ docs/
   └─ architecture.png       # 佔位圖（之後替換）
```

---

## 常見問題
- Dify API 路徑可能因版本不同略有差異，本範例使用 `/v1/datasets/{dataset_id}/document/create_by_text`；若報 404，請到 Dify 文件查「Datasets / Documents API」並調整 `push_kb.py` 內的 `create_url`。
- 若你的原始資料是 PDF，請先另行轉成 txt 或 csv；或自行擴充 `prepare_data.py`。

MIT License.
