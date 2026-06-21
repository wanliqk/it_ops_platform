# 企业 IT 报修与资产管理平台

后端项目骨架，基于 FastAPI、SQLAlchemy、Alembic、Pydantic 和 MySQL。

## 功能模块

- 用户与部门基础数据
- IT 资产台账
- 报修工单创建、流转与查询
- 健康检查与基础 API 版本路由

## MySQL 配置

先在 MySQL 中创建数据库和账号：

```sql
CREATE DATABASE it_ops_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'it_ops_user'@'%' IDENTIFIED BY 'it_ops_password';
GRANT ALL PRIVILEGES ON it_ops_platform.* TO 'it_ops_user'@'%';
FLUSH PRIVILEGES;
```

复制环境变量文件后，按你的本机 MySQL 地址、端口、账号和密码修改 `DATABASE_URL`：

```powershell
copy .env.example .env
```

示例：

```env
DATABASE_URL=mysql+pymysql://it_ops_user:it_ops_password@127.0.0.1:3306/it_ops_platform?charset=utf8mb4
```

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic revision --autogenerate -m "init"
alembic upgrade head
uvicorn app.main:app --reload
```

访问：

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

## 项目结构

```text
app/
  api/v1/          API 路由
  core/            配置与应用基础能力
  db/              数据库会话与基类
  models/          SQLAlchemy ORM 模型
  schemas/         Pydantic 入参/出参模型
  services/        业务服务层
tests/             测试
alembic/           数据库迁移目录
```

## 常用命令

```powershell
pytest
ruff check .
alembic revision --autogenerate -m "init"
alembic upgrade head
```
