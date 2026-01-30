# Zeus Medical Data Platform

一个基于 FastAPI 和 Celery 的医疗数据处理平台，支持用户认证、权限控制和异步任务执行。

## 功能特性

- ✅ 完整的前后端应用
- ✅ 用户登录认证系统（JWT Token）
- ✅ 基于角色的权限控制
- ✅ 三个医疗数据处理模块：
  - 模块1：患者数据分析
  - 模块2：医学影像处理
  - 模块3：药物相互作用分析
- ✅ 异步任务执行（Celery + Redis）
- ✅ 任务状态查询和监控
- ✅ Docker 容器化部署

## 技术栈

### 后端
- **FastAPI**: 现代化的异步 Web 框架
- **Celery**: 分布式任务队列
- **Redis**: 消息代理和结果存储
- **Python-Jose**: JWT 认证
- **Passlib**: 密码哈希

### 前端
- **HTML5/CSS3/JavaScript**: 原生 Web 技术
- **Nginx**: Web 服务器

### 部署
- **Docker & Docker Compose**: 容器化部署

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆仓库：
```bash
git clone https://github.com/whan6795/Zeus.git
cd Zeus
```

2. 启动所有服务：
```bash
docker-compose up --build
```

3. 访问应用：
- 前端界面: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 测试账号

系统预置了以下测试账号（密码均为 `secret`）：

| 用户名 | 密码 | 权限 |
|--------|------|------|
| admin  | secret | 所有模块 (module1, module2, module3) |
| user1  | secret | 模块1, 模块2 (module1, module2) |
| user2  | secret | 模块3 (module3) |

## 项目结构

```
Zeus/
├── backend/                 # 后端应用
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   ├── auth.py     # 认证接口
│   │   │   └── modules.py  # 模块接口
│   │   ├── core/           # 核心功能
│   │   │   ├── config.py   # 配置
│   │   │   ├── security.py # 安全认证
│   │   │   ├── celery_app.py # Celery 配置
│   │   │   └── tasks.py    # 异步任务
│   │   ├── models/         # 数据模型
│   │   │   └── user.py     # 用户模型
│   │   ├── schemas/        # Pydantic 模式
│   │   │   └── schemas.py  # 请求/响应模式
│   │   ├── scripts/        # 医疗数据脚本
│   │   │   └── medical_scripts.py # 模拟脚本
│   │   └── main.py         # FastAPI 应用入口
│   ├── Dockerfile          # 后端 Docker 配置
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端应用
│   ├── public/
│   │   ├── index.html      # 主页面
│   │   ├── styles.css      # 样式
│   │   └── app.js          # JavaScript 逻辑
│   ├── Dockerfile          # 前端 Docker 配置
│   └── nginx.conf          # Nginx 配置
├── docker-compose.yml      # Docker Compose 配置
└── README.md              # 项目文档
```

## API 接口

### 认证接口

#### 登录
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=secret
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

### 模块接口

#### 执行模块任务
```http
POST /api/v1/modules/{module_name}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "module_name": "module1",
  "parameters": {}
}
```

响应：
```json
{
  "task_id": "abc-123-def",
  "status": "pending",
  "message": "Task submitted successfully"
}
```

#### 查询任务状态
```http
GET /api/v1/modules/tasks/{task_id}
Authorization: Bearer <token>
```

响应：
```json
{
  "task_id": "abc-123-def",
  "status": "success",
  "result": {
    "module": "module1",
    "status": "completed",
    "patients_processed": 150,
    "anomalies_detected": 3
  },
  "error": null
}
```

#### 获取可用模块列表
```http
GET /api/v1/modules/list
Authorization: Bearer <token>
```

## 本地开发

### 后端开发

1. 创建虚拟环境：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动 Redis（需要 Docker）：
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

4. 启动后端服务：
```bash
uvicorn app.main:app --reload
```

5. 启动 Celery Worker：
```bash
celery -A app.core.celery_app worker --loglevel=info
```

### 前端开发

前端是静态文件，可以直接用浏览器打开 `frontend/public/index.html`，或使用任何 Web 服务器。

使用 Python 的简单 HTTP 服务器：
```bash
cd frontend/public
python -m http.server 3000
```

## 架构说明

### 认证流程
1. 用户通过登录接口提交用户名和密码
2. 后端验证凭证并生成 JWT Token
3. 前端存储 Token 并在后续请求中携带
4. 后端验证 Token 并检查用户权限

### 任务执行流程
1. 用户点击执行按钮
2. 前端发送任务执行请求
3. 后端验证用户权限
4. 后端将任务提交到 Celery 队列
5. Celery Worker 异步执行任务
6. 前端轮询任务状态
7. 任务完成后显示结果

### 权限控制
- 每个用户有不同的模块访问权限
- 前端根据权限显示/隐藏对应模块
- 后端 API 强制验证权限，防止越权访问

## 扩展建议

1. **数据库集成**: 当前使用内存存储用户数据，可以集成 PostgreSQL 或 MySQL
2. **实际医疗脚本**: 替换模拟脚本为真实的数据处理逻辑
3. **文件上传**: 添加文件上传功能，支持处理医疗数据文件
4. **任务历史**: 记录所有任务执行历史
5. **监控面板**: 添加 Celery Flower 监控任务执行情况
6. **日志系统**: 集成完整的日志记录和分析系统

## 许可证

MIT License