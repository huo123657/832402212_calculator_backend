# 832402212_calculator_backend

前后端分离计算器系统的**后端服务**（配套前端仓库：`832402212_calculator_frontend`）。

后端负责全部核心逻辑：接收表达式请求、输入校验、数学表达式解析与计算（**不使用 eval**）、异常处理、计算历史在数据库中的增删查。

## 技术栈

| 项目 | 选择 | 说明 |
| ---- | ---- | ---- |
| 语言 | Python 3.8+ | |
| Web 框架 | Flask | 轻量 HTTP 框架，负责 API 路由 |
| 数据库 | SQLite | 零配置文件数据库，通过标准库 `sqlite3` 访问 |
| 表达式解析 | 自实现 | 词法分析 + 递归下降语法分析，未使用 eval/exec |

## 运行环境

- Python 3.8 及以上
- 无需安装数据库软件（SQLite 内嵌于 Python 标准库）

## 安装方法

```bash
# 1. 进入后端项目根目录
cd 832402212_calculator_backend

# 2.（可选）创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. 安装依赖
pip install -r requirements.txt
```

## 启动方法

```bash
python src/app.py
```

启动后监听 `http://127.0.0.1:5000`（日志中会打印实际地址）。首次启动会自动建库建表。

运行自动化测试（基于 Flask test client，无需先启动服务）：

```bash
python tests/test_api.py
```

## 配置说明

| 配置项 | 默认值 | 说明 |
| ------ | ------ | ---- |
| 监听地址/端口 | `0.0.0.0:5000` | 在 `src/app.py` 最后一行修改 |
| 数据库文件位置 | 项目根目录 `calculator.db` | 可用环境变量 `CALCULATOR_DB_PATH` 覆盖 |
| 跨域 | 允许所有来源 | 前后端分离部署必需，见 `src/app.py` 的 `add_cors_headers` |

## 数据库初始化方法

无需手动初始化。应用启动时 `model/database.py` 的 `init_db()` 会自动执行 `CREATE TABLE IF NOT EXISTS`。

表结构（`calculation_history`）：

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | INTEGER | 主键，自增 |
| expression | TEXT | 计算表达式，如 `(1+2)*3` |
| result | TEXT | 计算结果（展示串，如 `9`、`0.3`） |
| created_at | TEXT | 计算时间 `YYYY-MM-DD HH:MM:SS` |

删除 `calculator.db` 文件即可重置数据库。

## 前后端连接方式

1. 启动本后端服务（默认 5000 端口）；
2. 前端页面中的 `API_BASE_URL`（前端仓库 `src/js/app.js` 顶部）指向本服务地址；
3. 后端已开启 CORS（`Access-Control-Allow-Origin: *`），支持前端跨域访问。

## API 一览

| 方法 | 路径 | 说明 | 成功 | 失败 |
| ---- | ---- | ---- | ---- | ---- |
| POST | `/api/calculate` | 计算表达式并存入历史 | 200 | 400 |
| GET | `/api/history` | 查询全部计算历史 | 200 | - |
| DELETE | `/api/history/{id}` | 删除指定 id 的历史 | 200 | 404 |
| DELETE | `/api/history` | 清空全部历史（扩展） | 200 | - |

### 请求/响应示例

```text
POST /api/calculate
请求体: {"expression": "(1+2)*3"}

成功 200:
{"success": true, "expression": "(1+2)*3", "result": 9, "id": 12, "time": "2026-10-06 15:48:39"}

失败 400:
{"success": false, "message": "Division by zero"}
```

## 目录结构

```text
832402212_calculator_backend/
├── src/
│   ├── app.py                    # 应用入口：创建 Flask 应用、CORS、全局异常
│   ├── controller/
│   │   └── api_controller.py     # API 路由层：参数校验、统一响应格式
│   ├── service/
│   │   ├── calculator_service.py # 计算业务：规范化 -> 求值 -> 存历史
│   │   ├── expression_parser.py  # 表达式解析器：词法分析 + 递归下降求值
│   │   └── history_service.py    # 历史业务：查询 / 删除 / 清空
│   └── model/
│       └── database.py           # 数据库访问层：建表、增、查、删（SQLite）
├── tests/
│   └── test_api.py               # API 自动化测试（30 个用例）
├── requirements.txt
├── README.md
└── codestyle.md
```
