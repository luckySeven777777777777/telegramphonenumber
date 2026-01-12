# Telegram Railway Deploy（可直接部署模板）

## 使用说明（必须按顺序）

### 1️⃣ 本地生成 session（只做一次）
```bash
pip install -r requirements.txt
export API_ID=你的API_ID
export API_HASH=你的API_HASH
export LOGIN_PHONE=17408999258
python login.py
```

生成：
```
sessions/17408999258.session
```

### 2️⃣ 提交 session 到 Git
```bash
git add sessions/17408999258.session
git commit -m "add telegram session"
git push
```

### 3️⃣ Railway 设置环境变量
- API_ID
- API_HASH

### 4️⃣ Railway 启动命令
```bash
python main.py
```

> 注意：Railway 不能输入验证码，必须先在本地生成 session。