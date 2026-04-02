# 💌 For You - 韩式INS风表白网站

一个极简韩式Instagram风格的表白/恋爱网站，支持图片上传和留言板功能。

## 技术栈

- **前端**: Vue 3 + Vite (端口 3000)
- **后端**: Python FastAPI (端口 5000)
- **数据库**: MySQL (192.168.51.104:3307)

## 快速开始

### 1. 初始化数据库

在MySQL中执行 `backend/init.sql`：

```bash
mysql -h 192.168.51.104 -P 3307 -u theonemind -ptom123456 < backend/init.sql
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端运行在 http://localhost:5000

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:3000

## 功能

- 📷 图片上传 & 相册展示（INS风九宫格）
- 💬 留言板（支持心情标签）
- 📱 手机端完美适配
- 🤍 韩式极简INS风格设计
