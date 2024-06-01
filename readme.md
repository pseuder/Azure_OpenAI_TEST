# Azure OpenAI 與 Flask 伺服器應用

這個專案是一個使用 Azure OpenAI 和 Flask 伺服器的應用。使用者可以透過前端網頁輸入 Azure OpenAI 的參數，然後這些參數會被傳送到後端的 Flask 伺服器。

## 安裝

首先，你可以使用以下的指令來安裝必要套件：

```bash
pip install -r requirements.txt
```

## 使用

啟動 Flask 伺服器：

```python
python service.py
```

然後，在你的瀏覽器中打開 http://localhost:5000，並輸入你的 Azure OpenAI 參數。

