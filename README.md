# 智慧傷口照護系統 (Smart Wound Care System)

本分支將 WoundCare+ 研究模型的影像分析接入既有 FastAPI 後端及管理員、護理師、病患 Web 介面。模型輸出須經護理師覆核。

---

## 🔗 原專案線上展示環境（未部署此分支）

- **系統入口網址**：[https://smart-wound-care.onrender.com/](https://smart-wound-care.onrender.com/)
- **服務狀態**：24/7 常駐在線（由 UptimeRobot 與 `/api/health` 心跳機制保活）

### 🔑 預設測試帳號（密碼皆為 `123456`）

| 角色名稱 | 登入帳號 | 預設密碼 | 核心功能介紹 |
| :--- | :--- | :--- | :--- |
| **系統管理員 (Admin)** | `admin01` | `123456` | 護病每日三班指派、人員帳號與臨床病歷管理、全院傷口紀錄稽核（比對 AI 與護理師判定差異） |
| **臨床護理師 (Nurse)** | `N001` / `N002` / `N003` | `123456` | 檢視今日負責病患、上傳傷口照片進行 AI 即時邊界偵測、填寫臨床分級與處置建議 |
| **就診病患 (Patient)** | `P001` / `P002` | `123456` | 查看個人歷史傷口照片與復原進度、傷口衛教專區（影片/專文）、智慧 AI 照護助理互動諮詢 |

---

## 🌟 核心功能特色

1. **👥 三端權限分流與安全驗證**
   - 採用 JWT (JSON Web Token) 進行身份驗證與 API 存取控制。
   - 單一登入入口（`/login.html`），登入後依角色自動導向專屬儀表板。

2. **🤖 WoundCare+ 研究模型影像分析**
   - 使用分類與分割模型；分割結果僅提供可能的影像區域提示。
   - 不自動產生臨床 Grade、感染判斷或處置建議，護理師須自行覆核。

3. **🩺 AI 與護理師雙軌評定 (Dual-Track Assessment)**
   - 護理師填寫臨床分級與處置紀錄，病患狀態依護理師分級更新。
   - 管理端將研究模型結果標記為待人工覆核。

4. **🔒 醫療病歷個資加密 (EMR Security)**
   - 採用 `cryptography.fernet` 對病患的病床號、過敏史、重大病史等敏感資料進行對稱加密儲存，保障醫療隱私。

5. **💬 智慧 AI 照護助理 (`/api/chat`)**
   - 自動將病患最新歷次傷口評估紀錄注入上下文，提供高度客製化的日常護理建議；若本機 LLM 離線則具備標準臨床 Fallback 提示。

---

## 🏗️ 系統架構與技術棧

- **後端 API**：Python 3.10、FastAPI、Uvicorn、SQLAlchemy、PyMySQL、PyJWT、Cryptography
- **AI 推論**：Ultralytics YOLO 分類與分割模型；記憶體需求需依部署環境實測。
- **前端介面**：原生 HTML5 / CSS3 / JavaScript、FontAwesome、Responsive Web Design
- **雲端資料庫**：Aiven Cloud MySQL（含 SSL 安全連線與自動表格遷移）
- **雲端部署**：Docker 容器化、Render Web Service

---

## 📂 專案目錄結構

```text
├── frontend/                     # 前端網頁介面
│   ├── login.html                # 系統登入頁
│   ├── admin_dashboard.html      # 管理員主控台
│   ├── admin_assignments.html    # 護病每日指派
│   ├── admin_history.html        # 全院傷口稽核歷程
│   ├── admin_users.html          # 使用者與病歷管理
│   ├── nurse_dashboard.html      # 護理師工作台
│   ├── wound_assessment.html     # 傷口拍照與雙軌評估
│   └── patient_dashboard.html    # 病患個人照護專區
├── main.py                       # FastAPI 核心伺服器與業務邏輯
├── woundcare_inference.py        # WoundCare+ 分類與分割推論
├── woundcare_integration.py      # 護理師評估頁的安全回應轉接
├── requirements.txt              # 後端相依套件清單
├── Dockerfile                    # 雲端容器化建置腳本
├── start_project.bat             # 本地端一鍵啟動腳本
└── fix_password.py               # 帳號密碼維護工具
```

---

## 💻 本地端開發與啟動

1. **安裝相依套件**：
   ```bash
   pip install -r requirements.txt
   ```

2. **啟動本機服務**：
   - 雙擊執行根目錄的 `start_project.bat`，或於終端機執行：
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. 開啟瀏覽器訪問 `http://127.0.0.1:8000/login.html` 即可開始使用。

### WoundCare+ 模型設定

此分支保留原有登入、MySQL、病患及交班紀錄後端，將 `/api/predict` 接到 WoundCare+ 的分類與分割推論。啟動前設定 `WOUNDCARE_CLS_MODEL` 與 `WOUNDCARE_SEG_MODEL` 為各自 `best.pt` 的絕對路徑。權重不納入 Git，也不複製進 Docker 映像；容器部署時需將權重唯讀掛載，並將這兩個變數設為容器內路徑。缺少任一權重時，預測 API 回傳 503，`/api/health` 的 `inference_ready` 為 `false`。

分類標籤屬研究提示，與 Grade 1–4 無直接對應；頁面與紀錄的 AI Grade 固定為「待人工判讀」，臨床分級及處置由護理師填寫。分割無可靠 ROI 時不顯示類別提示。這個串接沒有驗證模型品質、分布外影像或臨床安全，勿以此分支直接進行臨床決策。
