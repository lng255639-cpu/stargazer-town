# 星標鎮日報 Stargazer Town Daily

把 GitHub 熱門榜蓋成一座像素小鎮：榜上前 9 名變成鎮上的大樓，今天多的星星越多，樓就蓋得越高。小鎮日報記者「米拉」會一則一則介紹，右邊的《TOWN DAILY 小鎮日報》每天自動更新。

**線上版：** https://lng255639-cpu.github.io/stargazer-town/

## 功能

- 等角視角小鎮，用 canvas 即時繪製。大樓外牆顏色是專案的主要語言，天色跟窗戶燈光會跟著現在的時間變化，街上有人在走
- 原創像素角色米拉，打字機對話框，可以點「下一句／上一句」，或用鍵盤 ← →
- 點大樓或報紙上的專案名稱，就會跳到那個專案
- 單一 HTML 檔，不需要任何套件或建置步驟

## 資料怎麼更新

頁面會依序試這幾個來源，用第一個成功的：

1. `api/trending`：用本機 `server.py` 開啟時，由伺服器即時抓 github.com/trending
2. `trending.json`：GitHub Actions 每天台灣時間 09:00 抓一次並 commit 進 repo（線上版用這個）
3. GitHub Search API：近 7 天新建、星數最多的專案
4. 檔案裡內建的存檔：全部失敗時才顯示，會標「離線 · 顯示存檔」

想馬上更新，可以到 Actions 分頁手動執行「Update trending」。

## 在自己電腦上跑

需要 Python 3（只用標準函式庫）。

- Windows：雙擊 `開啟星標鎮.bat`
- 其他系統：`python server.py`，然後打開 http://localhost:8765/

直接雙擊 `index.html` 也能開，但瀏覽器通常會擋掉直接開檔時的網路請求，所以只會看到內建存檔。
