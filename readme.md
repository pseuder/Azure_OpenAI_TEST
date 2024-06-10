# Azure OpenAI 與 Flask 伺服器應用

這個專案是一個使用 Azure OpenAI 和 Flask 伺服器的應用。使用者可以透過前端網頁輸入 Azure OpenAI 的參數，然後這些參數會被傳送到後端的 Flask 伺服器。



## 後端服務

切換至service目錄：

```bash
cd ./service
```

你可以使用以下的指令來安裝必要套件：

```bash
pip install -r requirements.txt
```

啟動 Flask 伺服器：

```python
python Service.py
```

## 前端頁面

後端服務開啟後即可打開 `web\index.html` 並填入Azure OpenAI參數