# 学习指认AI平台

K12阶段学生课业辅导AI产品，支持iPad学生端 + Android家长端双端协同。

## 项目结构

```
ai-study-platform/
├── doc/                    # 需求文档
├── server/                 # 后端服务 (Python FastAPI)
│   ├── app/
│   │   ├── api/            # REST API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── schemas/        # Pydantic 请求/响应模型
│   │   ├── services/       # 业务逻辑服务层
│   │   ├── utils/          # 工具函数
│   │   └── websocket/      # WebSocket 实时通信
│   ├── alembic/            # 数据库迁移
│   ├── static/uploads/     # 上传文件存储
│   ├── requirements.txt
│   └── main.py
├── mobile/                 # Flutter 移动端 (iPad + Android)
│   ├── lib/
│   │   ├── config/         # 应用配置
│   │   ├── models/         # 数据模型
│   │   ├── providers/      # 状态管理
│   │   ├── screens/        # 页面
│   │   ├── services/       # API/WebSocket 服务
│   │   ├── widgets/        # 通用组件
│   │   └── main.dart
│   └── pubspec.yaml
├── deploy/                 # 部署脚本 (裸机部署)
└── scripts/                # 辅助脚本
```

## 技术栈

| 层级 | 技术 |
|---|---|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy / Alembic |
| 数据库 | PostgreSQL 15+ / Redis 7+ |
| 移动端 | Flutter 3.x / Dart |
| 实时通信 | WebSocket |
| 视频通话 | 声网 Agora SDK |
| AI全能力 | DeepSeek API (含Vision多模态) — OCR+批改+讲解+错因分析+相似题 |
| 手指检测 | MediaPipe (端侧) |
| 文件存储 | MinIO |

## 快速开始

### 后端

```bash
cd server
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env      # 编辑配置
alembic upgrade head      # 初始化数据库
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 移动端

```bash
cd mobile
flutter pub get
flutter run  # 连接设备后运行
```

## API Keys 配置

在 `server/.env` 中配置：

```env
DEEPSEEK_API_KEY=your_key       # DeepSeek API（AI全能力：OCR+批改+讲解等）
AGORA_APP_ID=your_app_id        # 声网Agora（视频通话）
AGORA_APP_CERTIFICATE=your_cert
```

仅需 **DeepSeek + 声网Agora** 两个外部服务，无需额外OCR API。
