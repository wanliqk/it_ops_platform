# 企业内部 IT 报修与资产运维管理平台后端 API 接口文档

## 1. 项目说明

本项目为企业内部 IT 报修与资产运维管理平台，主要提供以下业务能力：

1. 员工登录系统并提交 IT 报修工单；
2. IT 运维人员查看、接单、处理、完成工单；
3. 管理员维护用户、资产分类、资产台账；
4. 系统记录工单状态流转、维修记录、操作日志；
5. 提供统计接口，用于首页看板展示。

后端要求使用：

```text
Python 3.11+
FastAPI
SQLAlchemy
Pydantic
MySQL 8.0
JWT Token 认证
APScheduler
```

接口统一前缀：

```text
/api/v1
```

本接口文档对应的主要数据库表：

```text
sys_user              用户表
sys_role              角色表
sys_permission        权限表
sys_user_role         用户角色关联表
sys_role_permission   角色权限关联表
it_asset_category     资产分类表
it_asset              资产表
it_ticket             报修工单表
it_ticket_record      工单流转记录表
it_repair_record      维修记录表
it_sla_rule           SLA规则表
it_faq                常见问题表
it_notification       站内通知表
sys_operation_log     操作日志表
```

---

# 2. 通用规范

## 2.1 统一响应格式

所有接口返回统一 JSON 格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

字段说明：

| 字段      | 类型                    | 说明                    |
| ------- | --------------------- | --------------------- |
| code    | int                   | 业务状态码，0 表示成功，非 0 表示失败 |
| message | string                | 响应提示信息                |
| data    | object / array / null | 具体业务数据                |

失败示例：

```json
{
  "code": 40001,
  "message": "用户名或密码错误",
  "data": null
}
```

---

## 2.2 HTTP 状态码规范

| HTTP 状态码 | 说明                   |
| -------- | -------------------- |
| 200      | 请求成功                 |
| 201      | 创建成功                 |
| 400      | 请求参数错误               |
| 401      | 未登录或 Token 无效        |
| 403      | 无权限访问                |
| 404      | 资源不存在                |
| 409      | 业务冲突，例如用户名重复、状态不允许流转 |
| 422      | 参数校验失败               |
| 500      | 服务器内部错误              |

---

## 2.3 业务错误码

| code  | 说明            |
| ----- | ------------- |
| 0     | 成功            |
| 40000 | 参数错误          |
| 40001 | 用户名或密码错误      |
| 40002 | 用户已被禁用        |
| 40100 | 未登录或 Token 无效 |
| 40300 | 无权限操作         |
| 40400 | 资源不存在         |
| 40900 | 业务状态冲突        |
| 50000 | 系统内部错误        |

---

## 2.4 分页请求参数

列表接口统一支持分页参数：

| 参数        | 类型  | 必填 | 默认值 | 说明          |
| --------- | --- | -- | --- | ----------- |
| page      | int | 否  | 1   | 当前页码        |
| page_size | int | 否  | 10  | 每页数量，最大 100 |

分页响应格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "pages": 10
  }
}
```

---

## 2.5 认证方式

除登录接口外，其他接口默认都需要携带 JWT Token。

请求头格式：

```http
Authorization: Bearer <access_token>
```

---

# 3. 枚举值定义

## 3.1 用户兼容角色 role

`sys_user.role` 为兼容字段，创建和查询用户时仍会返回该字段。

后端接口权限判断不再直接依赖 `sys_user.role`，必须基于 RBAC 表：

```text
sys_user -> sys_user_role -> sys_role -> sys_role_permission -> sys_permission
```

| 值        | 说明      |
| -------- | ------- |
| admin    | 管理员兼容值  |
| it_staff | IT 运维兼容值 |
| employee | 普通员工兼容值 |

---

## 3.2 用户状态 status

| 值 | 说明 |
| - | -- |
| 1 | 启用 |
| 0 | 禁用 |

---

## 3.3 工单状态 ticket.status

| 值          | 说明  |
| ---------- | --- |
| pending    | 待受理 |
| assigned   | 已派单 |
| processing | 处理中 |
| completed  | 已完成 |
| cancelled  | 已取消 |

第一版先使用以上 5 个状态，不要增加过多状态。

---

## 3.4 工单优先级 priority

| 值      | 说明 |
| ------ | -- |
| low    | 低  |
| normal | 普通 |
| high   | 高  |
| urgent | 紧急 |

---

## 3.5 故障类型 fault_type

| 值        | 说明     |
| -------- | ------ |
| hardware | 硬件故障   |
| software | 软件故障   |
| network  | 网络故障   |
| printer  | 打印机故障  |
| account  | 账号权限问题 |
| other    | 其他     |

---

## 3.6 资产状态 asset.status

| 值         | 说明  |
| --------- | --- |
| in_use    | 在用  |
| idle      | 闲置  |
| repairing | 维修中 |
| scrapped  | 已报废 |

---

## 3.7 维修结果 repair_result

| 值              | 说明      |
| -------------- | ------- |
| fixed          | 已修复     |
| replace_repair | 更换配件后修复 |
| scrapped       | 建议报废    |
| unresolved     | 未解决     |

---

## 3.8 FAQ 分类 faq.category

| 值       | 说明     |
| ------- | ------ |
| computer | 电脑问题   |
| network  | 网络问题   |
| printer  | 打印机问题  |
| account  | 账号系统问题 |
| other    | 其他问题   |

---

## 3.9 通知业务类型 notification.biz_type

| 值     | 说明    |
| ----- | ----- |
| ticket | 工单通知  |
| asset  | 资产通知  |
| sla    | SLA 提醒 |
| system | 系统通知  |

---

## 3.10 SLA 规则优先级 priority

| 值     | 说明 |
| ------ | -- |
| low    | 低  |
| medium | 普通 |
| high   | 高  |
| urgent | 紧急 |

说明：

```text
工单接口历史优先级使用 normal 表示普通；
SLA 规则使用 medium 表示普通；
后端计算 SLA 时会将工单 priority = normal 映射为 SLA priority = medium。
```

---

# 4. RBAC 权限规则

## 4.1 权限模型

后端统一通过 `permission_code` 做强制权限校验，前端只可根据 `/api/v1/auth/me`
返回的权限码控制页面展示，不能替代后端校验。

核心数据表：

| 表名                  | 说明       |
| ------------------- | -------- |
| sys_role            | 角色表      |
| sys_permission      | 权限表      |
| sys_user_role       | 用户角色关联表  |
| sys_role_permission | 角色权限关联表  |

权限判断链路：

```text
当前登录用户 -> 用户角色 -> 启用状态角色 -> 角色权限 -> 启用状态权限 -> permission_code
```

`sys_user.role` 仅用于兼容旧数据展示，不作为接口授权依据。

## 4.2 常用权限码

| 模块     | 权限码                                                                 |
| ------ | ------------------------------------------------------------------- |
| 用户管理   | user:view、user:create、user:update、user:status、user:reset_password、user:delete |
| 角色权限管理 | role:view、role:create、role:update、role:delete、role:assign_permission、permission:view、user:assign_role |
| 资产分类管理 | asset_category:view、asset_category:create、asset_category:update、asset_category:delete |
| 资产管理   | asset:view、asset:create、asset:update、asset:status、asset:delete、asset:repair_records |
| 工单管理   | ticket:create、ticket:view_all、ticket:view_self、ticket:update、ticket:assign、ticket:start、ticket:complete、ticket:cancel、ticket:delete、ticket:records |
| 维修记录   | repair_record:view、repair_record:update |
| FAQ 管理 | faq:view、faq:create、faq:update、faq:status、faq:delete、faq:stats |
| SLA规则管理 | sla:rule:list、sla:rule:create、sla:rule:update、sla:rule:delete、sla:rule:enable |
| 操作日志   | operation_log:view |
| 首页看板   | dashboard:view |
| 字典     | dict:view |

## 4.3 数据范围规则

工单数据范围和操作范围必须由后端控制：

```text
1. 拥有 ticket:view_all 的用户可以查看全部工单；
2. 只有 ticket:view_self 的用户只能查看 reporter_id = 当前用户ID 的工单；
3. 普通员工只能修改和取消自己创建且 status = pending 的工单；
4. IT 运维人员只能完成分配给自己的工单；
5. RBAC 角色码包含 admin 的用户可以操作全部数据。
```

## 4.4 默认角色示例

以下角色只是初始化数据示例，实际权限以 RBAC 分配结果为准。

### 普通员工 employee

允许：

```text
查看自己的信息
修改自己的密码
创建自己的报修工单
查看自己的工单列表
查看自己的工单详情
取消自己的 pending 状态工单
查看启用状态的 FAQ 列表和详情
```

不允许：

```text
查看全部用户
管理资产
派单
处理工单
查看操作日志
```

---

### IT 运维人员 it_staff

允许：

```text
查看工单列表
查看工单详情
接单
开始处理工单
完成工单
查看资产列表
查看资产详情
查看维修记录
查看 FAQ 列表和详情
```

不允许：

```text
删除用户
禁用用户
删除资产
查看系统操作日志
维护 FAQ
```

---

### 管理员 admin

允许：

```text
用户管理
资产分类管理
资产管理
工单管理
派单
查看所有工单
查看维修记录
查看操作日志
查看统计数据
FAQ 管理
```

---

# 5. 认证模块 Auth API

## 5.1 用户登录

```http
POST /api/v1/auth/login
```

权限：公开接口

请求参数：

```json
{
  "username": "admin",
  "password": "123456"
}
```

字段说明：

| 字段       | 类型     | 必填 | 说明    |
| -------- | ------ | -- | ----- |
| username | string | 是  | 登录用户名 |
| password | string | 是  | 登录密码  |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "jwt_token_string",
    "token_type": "Bearer",
    "expires_in": 7200,
    "user": {
      "id": 1,
      "username": "admin",
      "real_name": "系统管理员",
      "role": "admin",
      "department": "信息部",
      "phone": "13800000001",
      "email": "admin@example.com",
      "status": 1
    }
  }
}
```

业务规则：

```text
1. 根据 username 查询用户；
2. 用户不存在，返回用户名或密码错误；
3. 密码校验失败，返回用户名或密码错误；
4. 用户 status = 0，返回账号已禁用；
5. 登录成功后生成 JWT Token；
6. 记录登录操作日志。
```

---

## 5.2 获取当前登录用户

```http
GET /api/v1/auth/me
```

权限：登录用户

返回当前用户基础信息、RBAC 角色编码列表和权限编码列表。

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "admin",
    "real_name": "系统管理员",
    "role": "admin",
    "department": "信息部",
    "phone": "13800000001",
    "email": "admin@example.com",
    "status": 1,
    "created_at": "2026-06-21 08:00:00",
    "updated_at": "2026-06-21 08:00:00",
    "roles": [
      "admin"
    ],
    "permissions": [
      "user:view",
      "role:view",
      "ticket:view_all",
      "asset:view"
    ]
  }
}
```

---

## 5.3 修改当前用户密码

```http
PUT /api/v1/auth/password
```

权限：登录用户

请求参数：

```json
{
  "old_password": "123456",
  "new_password": "NewPassword123"
}
```

字段说明：

| 字段           | 类型     | 必填 | 说明           |
| ------------ | ------ | -- | ------------ |
| old_password | string | 是  | 原密码          |
| new_password | string | 是  | 新密码，长度至少 6 位 |

成功响应：

```json
{
  "code": 0,
  "message": "密码修改成功",
  "data": null
}
```

业务规则：

```text
1. 校验 old_password 是否正确；
2. new_password 需要加密后保存；
3. 修改成功后记录操作日志。
```

---

# 6. 用户管理 User API

## 6.1 查询用户列表

```http
GET /api/v1/users
```

权限：user:view

查询参数：

| 参数         | 类型     | 必填 | 说明                               |
| ---------- | ------ | -- | -------------------------------- |
| keyword    | string | 否  | 按用户名、姓名、手机号模糊查询                  |
| role       | string | 否  | 用户角色：admin / it_staff / employee |
| status     | int    | 否  | 用户状态：1启用，0禁用                     |
| department | string | 否  | 部门                               |
| page       | int    | 否  | 页码                               |
| page_size  | int    | 否  | 每页数量                             |

请求示例：

```http
GET /api/v1/users?keyword=张&role=it_staff&page=1&page_size=10
```

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 2,
        "username": "it_zhang",
        "real_name": "张工",
        "role": "it_staff",
        "department": "信息部",
        "phone": "13800000002",
        "email": "zhang@example.com",
        "status": 1,
        "created_at": "2026-06-21 08:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

---

## 6.2 创建用户

```http
POST /api/v1/users
```

权限：user:create

请求参数：

```json
{
  "username": "employee_chen",
  "password": "123456",
  "real_name": "陈强",
  "role": "employee",
  "department": "招商部",
  "phone": "13800000005",
  "email": "chenqiang@example.com",
  "status": 1
}
```

成功响应：

```json
{
  "code": 0,
  "message": "用户创建成功",
  "data": {
    "id": 5,
    "username": "employee_chen",
    "real_name": "陈强",
    "role": "employee",
    "department": "招商部",
    "phone": "13800000005",
    "email": "chenqiang@example.com",
    "status": 1
  }
}
```

业务规则：

```text
1. username 不允许重复；
2. password 必须加密后保存到 password_hash；
3. role 只能是 admin、it_staff、employee；
4. 创建成功后记录操作日志。
```

---

## 6.3 查询用户详情

```http
GET /api/v1/users/{user_id}
```

权限：user:view

路径参数：

| 参数      | 类型  | 必填 | 说明   |
| ------- | --- | -- | ---- |
| user_id | int | 是  | 用户ID |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 3,
    "username": "employee_li",
    "real_name": "李明",
    "role": "employee",
    "department": "财务部",
    "phone": "13800000003",
    "email": "liming@example.com",
    "status": 1,
    "created_at": "2026-06-21 08:00:00",
    "updated_at": "2026-06-21 08:00:00"
  }
}
```

---

## 6.4 修改用户

```http
PUT /api/v1/users/{user_id}
```

权限：user:update

请求参数：

```json
{
  "real_name": "李明",
  "role": "employee",
  "department": "财务部",
  "phone": "13800000003",
  "email": "liming@example.com",
  "status": 1
}
```

业务规则：

```text
1. 不允许通过该接口修改密码；
2. 不允许修改 username；
3. 修改用户信息后记录操作日志。
```

成功响应：

```json
{
  "code": 0,
  "message": "用户修改成功",
  "data": null
}
```

---

## 6.5 启用或禁用用户

```http
PATCH /api/v1/users/{user_id}/status
```

权限：user:status

请求参数：

```json
{
  "status": 0
}
```

成功响应：

```json
{
  "code": 0,
  "message": "用户状态修改成功",
  "data": null
}
```

业务规则：

```text
1. status 只能为 1 或 0；
2. 不允许禁用当前登录的管理员自己；
3. 修改后记录操作日志。
```

---

## 6.6 重置用户密码

```http
PATCH /api/v1/users/{user_id}/password
```

权限：user:reset_password

请求参数：

```json
{
  "new_password": "123456"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "密码重置成功",
  "data": null
}
```

---

## 6.7 删除用户

```http
DELETE /api/v1/users/{user_id}
```

权限：user:delete

成功响应：

```json
{
  "code": 0,
  "message": "用户删除成功",
  "data": null
}
```

业务规则：

```text
1. 如果用户已经关联工单、资产、维修记录，不允许物理删除；
2. 已有关联数据时，返回 409，并建议使用禁用用户；
3. 不允许删除当前登录用户自己。
```

---

# 7. 资产分类 Asset Category API

## 7.1 查询资产分类列表

```http
GET /api/v1/asset-categories
```

权限：asset_category:view

查询参数：

| 参数      | 类型     | 必填 | 说明      |
| ------- | ------ | -- | ------- |
| keyword | string | 否  | 分类名称或编码 |
| status  | int    | 否  | 1启用，0停用 |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "category_name": "办公电脑",
      "category_code": "PC",
      "description": "员工日常办公使用的台式机、笔记本电脑",
      "status": 1
    }
  ]
}
```

---

## 7.2 创建资产分类

```http
POST /api/v1/asset-categories
```

权限：asset_category:create

请求参数：

```json
{
  "category_name": "服务器设备",
  "category_code": "SERVER",
  "description": "服务器、存储等机房设备",
  "status": 1
}
```

成功响应：

```json
{
  "code": 0,
  "message": "资产分类创建成功",
  "data": {
    "id": 4
  }
}
```

业务规则：

```text
1. category_code 不允许重复；
2. category_name 不允许为空；
3. 创建成功后记录操作日志。
```

---

## 7.3 查询资产分类详情

```http
GET /api/v1/asset-categories/{category_id}
```

权限：asset_category:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "category_name": "办公电脑",
    "category_code": "PC",
    "description": "员工日常办公使用的台式机、笔记本电脑",
    "status": 1,
    "created_at": "2026-06-21 08:00:00",
    "updated_at": "2026-06-21 08:00:00"
  }
}
```

---

## 7.4 修改资产分类

```http
PUT /api/v1/asset-categories/{category_id}
```

权限：asset_category:update

请求参数：

```json
{
  "category_name": "办公终端",
  "category_code": "PC",
  "description": "台式机、笔记本、一体机等办公终端设备",
  "status": 1
}
```

成功响应：

```json
{
  "code": 0,
  "message": "资产分类修改成功",
  "data": null
}
```

---

## 7.5 删除资产分类

```http
DELETE /api/v1/asset-categories/{category_id}
```

权限：asset_category:delete

成功响应：

```json
{
  "code": 0,
  "message": "资产分类删除成功",
  "data": null
}
```

业务规则：

```text
1. 如果分类下已有资产，不允许删除；
2. 返回 409，提示该分类已被资产使用；
3. 建议使用停用状态代替删除。
```

---

# 8. 资产管理 Asset API

## 8.1 查询资产列表

```http
GET /api/v1/assets
```

权限：asset:view

查询参数：

| 参数          | 类型     | 必填 | 说明                                   |
| ----------- | ------ | -- | ------------------------------------ |
| keyword     | string | 否  | 资产编号、资产名称、品牌、型号、序列号                  |
| category_id | int    | 否  | 资产分类ID                               |
| status      | string | 否  | in_use / idle / repairing / scrapped |
| department  | string | 否  | 所属部门                                 |
| user_id     | int    | 否  | 使用人ID                                |
| page        | int    | 否  | 页码                                   |
| page_size   | int    | 否  | 每页数量                                 |

请求示例：

```http
GET /api/v1/assets?keyword=电脑&status=in_use&page=1&page_size=10
```

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "asset_no": "IT-PC-2026-0001",
        "asset_name": "财务部办公电脑",
        "category_id": 1,
        "category_name": "办公电脑",
        "brand": "Dell",
        "model": "OptiPlex 7090",
        "serial_no": "SN-PC-0001",
        "user_id": 3,
        "user_name": "李明",
        "department": "财务部",
        "location": "财务办公室A区",
        "status": "in_use",
        "purchase_date": "2024-05-10",
        "warranty_expire_date": "2027-05-10"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

---

## 8.2 创建资产

```http
POST /api/v1/assets
```

权限：asset:create

请求参数：

```json
{
  "asset_no": "IT-PC-2026-0004",
  "asset_name": "招商部办公电脑",
  "category_id": 1,
  "brand": "Lenovo",
  "model": "ThinkCentre M750",
  "serial_no": "SN-PC-0004",
  "user_id": 5,
  "department": "招商部",
  "location": "招商办公室C区",
  "status": "in_use",
  "purchase_date": "2025-01-10",
  "warranty_expire_date": "2028-01-10",
  "remark": "招商部员工办公电脑"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "资产创建成功",
  "data": {
    "id": 4,
    "asset_no": "IT-PC-2026-0004"
  }
}
```

业务规则：

```text
1. asset_no 不允许重复；
2. category_id 必须存在；
3. user_id 如果传入，必须存在；
4. status 必须为合法枚举值；
5. 创建成功后记录操作日志。
```

---

## 8.3 查询资产详情

```http
GET /api/v1/assets/{asset_id}
```

权限：asset:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "asset_no": "IT-PC-2026-0001",
    "asset_name": "财务部办公电脑",
    "category_id": 1,
    "category_name": "办公电脑",
    "brand": "Dell",
    "model": "OptiPlex 7090",
    "serial_no": "SN-PC-0001",
    "user_id": 3,
    "user_name": "李明",
    "department": "财务部",
    "location": "财务办公室A区",
    "status": "in_use",
    "purchase_date": "2024-05-10",
    "warranty_expire_date": "2027-05-10",
    "remark": "财务部日常办公电脑",
    "created_at": "2026-06-21 08:00:00",
    "updated_at": "2026-06-21 08:00:00"
  }
}
```

---

## 8.4 修改资产

```http
PUT /api/v1/assets/{asset_id}
```

权限：asset:update

请求参数：

```json
{
  "asset_name": "财务部办公电脑",
  "category_id": 1,
  "brand": "Dell",
  "model": "OptiPlex 7090",
  "serial_no": "SN-PC-0001",
  "user_id": 3,
  "department": "财务部",
  "location": "财务办公室A区",
  "status": "in_use",
  "purchase_date": "2024-05-10",
  "warranty_expire_date": "2027-05-10",
  "remark": "财务部日常办公电脑"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "资产修改成功",
  "data": null
}
```

业务规则：

```text
1. 不允许通过该接口修改 asset_no；
2. 如果资产存在 processing 状态的未完成工单，不建议直接改为 scrapped；
3. 修改成功后记录操作日志。
```

---

## 8.5 修改资产状态

```http
PATCH /api/v1/assets/{asset_id}/status
```

权限：asset:status

请求参数：

```json
{
  "status": "repairing",
  "remark": "该资产正在维修"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "资产状态修改成功",
  "data": null
}
```

业务规则：

```text
1. status 必须是 in_use、idle、repairing、scrapped 之一；
2. 工单开始处理时，可自动将资产状态改为 repairing；
3. 工单完成后，可根据维修结果改为 in_use 或 scrapped；
4. 修改后记录操作日志。
```

---

## 8.6 删除资产

```http
DELETE /api/v1/assets/{asset_id}
```

权限：asset:delete

成功响应：

```json
{
  "code": 0,
  "message": "资产删除成功",
  "data": null
}
```

业务规则：

```text
1. 如果资产已关联工单或维修记录，不允许物理删除；
2. 返回 409，提示该资产已有业务记录；
3. 建议将资产状态改为 scrapped。
```

---

## 8.7 查询资产维修历史

```http
GET /api/v1/assets/{asset_id}/repair-records
```

权限：asset:repair_records

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "ticket_id": 1,
      "ticket_no": "TK202606210001",
      "ticket_title": "财务电脑无法开机",
      "repair_user_id": 2,
      "repair_user_name": "张工",
      "fault_reason": "内存接触不良，主机内部灰尘较多",
      "repair_method": "重新插拔内存条并清理机箱灰尘",
      "repair_result": "fixed",
      "repair_cost": 0.0,
      "repaired_at": "2026-06-21 10:10:00"
    }
  ]
}
```

---

# 9. 报修工单 Ticket API

## 9.1 查询工单列表

```http
GET /api/v1/tickets
```

权限：ticket:view_all 或 ticket:view_self

查询参数：

| 参数          | 类型     | 必填 | 说明                                                        |
| ----------- | ------ | -- | --------------------------------------------------------- |
| keyword     | string | 否  | 工单编号、标题、描述                                                |
| status      | string | 否  | pending / assigned / processing / completed / cancelled   |
| priority    | string | 否  | low / normal / high / urgent                              |
| fault_type  | string | 否  | hardware / software / network / printer / account / other |
| reporter_id | int    | 否  | 报修人ID                                                     |
| handler_id  | int    | 否  | 处理人ID                                                     |
| asset_id    | int    | 否  | 资产ID                                                      |
| start_date  | string | 否  | 创建开始日期，格式 YYYY-MM-DD                                      |
| end_date    | string | 否  | 创建结束日期，格式 YYYY-MM-DD                                      |
| page        | int    | 否  | 页码                                                        |
| page_size   | int    | 否  | 每页数量                                                      |

权限过滤规则：

```text
1. 拥有 ticket:view_all 的用户可以查看全部工单；
2. 只有 ticket:view_self 的用户只能查看 reporter_id = 当前用户ID 的工单；
3. 同时拥有 ticket:view_all 与 ticket:view_self 时，以 ticket:view_all 为准。
```

请求示例：

```http
GET /api/v1/tickets?status=pending&page=1&page_size=10
```

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "ticket_no": "TK202606210001",
        "title": "财务电脑无法开机",
        "fault_type": "hardware",
        "priority": "high",
        "status": "completed",
        "reporter_id": 3,
        "reporter_name": "李明",
        "handler_id": 2,
        "handler_name": "张工",
        "asset_id": 1,
        "asset_no": "IT-PC-2026-0001",
        "asset_name": "财务部办公电脑",
        "created_at": "2026-06-21 09:10:00",
        "completed_at": "2026-06-21 10:10:00",
        "sla_response_deadline": "2026-06-21 09:40:00",
        "sla_resolve_deadline": "2026-06-21 13:10:00",
        "first_response_at": "2026-06-21 09:20:00",
        "resolved_at": "2026-06-21 10:10:00",
        "response_overdue": 0,
        "resolve_overdue": 0
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

---

## 9.2 创建报修工单

```http
POST /api/v1/tickets
```

权限：ticket:create

请求参数：

```json
{
  "title": "办公电脑无法开机",
  "description": "按下电源键后主机没有反应，显示器无信号。",
  "fault_type": "hardware",
  "priority": "high",
  "asset_id": 1
}
```

字段说明：

| 字段          | 类型     | 必填 | 说明            |
| ----------- | ------ | -- | ------------- |
| title       | string | 是  | 工单标题          |
| description | string | 是  | 故障描述          |
| fault_type  | string | 是  | 故障类型          |
| priority    | string | 否  | 优先级，默认 normal |
| asset_id    | int    | 否  | 关联资产ID        |

成功响应：

```json
{
  "code": 0,
  "message": "工单创建成功",
  "data": {
    "id": 5,
    "ticket_no": "TK202606230001",
    "status": "pending",
    "sla_response_deadline": "2026-06-23 01:29:35",
    "sla_resolve_deadline": "2026-06-23 08:29:35"
  }
}
```

业务规则：

```text
1. ticket_no 由后端自动生成，格式：TK + yyyyMMdd + 4位序号，例如 TK202606230001；
2. reporter_id 使用当前登录用户ID；
3. 创建后 status = pending；
4. 如果 asset_id 传入，必须校验资产是否存在；
5. 后端根据 fault_type、priority 和启用状态 SLA 规则自动计算 sla_response_deadline、sla_resolve_deadline；
6. SLA 第一版按自然时间计算，不排除工作日、节假日和上下班时间；
7. 创建成功后写入 it_ticket_record，action = create；
8. 创建成功后记录操作日志。
```

---

## 9.3 查询工单详情

```http
GET /api/v1/tickets/{ticket_id}
```

权限：ticket:view_all 或 ticket:view_self

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "ticket_no": "TK202606210001",
    "title": "财务电脑无法开机",
    "description": "按下电源键后电脑无反应，显示器无信号。",
    "fault_type": "hardware",
    "priority": "high",
    "status": "completed",
    "reporter": {
      "id": 3,
      "real_name": "李明",
      "department": "财务部",
      "phone": "13800000003"
    },
    "handler": {
      "id": 2,
      "real_name": "张工",
      "department": "信息部",
      "phone": "13800000002"
    },
    "asset": {
      "id": 1,
      "asset_no": "IT-PC-2026-0001",
      "asset_name": "财务部办公电脑",
      "brand": "Dell",
      "model": "OptiPlex 7090",
      "location": "财务办公室A区"
    },
    "result": "重新插拔内存并清理主板灰尘后恢复正常。",
    "created_at": "2026-06-21 09:10:00",
    "assigned_at": "2026-06-21 09:20:00",
    "started_at": "2026-06-21 09:30:00",
    "completed_at": "2026-06-21 10:10:00",
    "sla_response_deadline": "2026-06-21 09:40:00",
    "sla_resolve_deadline": "2026-06-21 13:10:00",
    "first_response_at": "2026-06-21 09:20:00",
    "resolved_at": "2026-06-21 10:10:00",
    "response_overdue": 0,
    "resolve_overdue": 0,
    "records": [
      {
        "id": 1,
        "operator_id": 3,
        "operator_name": "李明",
        "from_status": null,
        "to_status": "pending",
        "action": "create",
        "remark": "用户提交电脑无法开机工单",
        "created_at": "2026-06-21 09:10:00"
      }
    ]
  }
}
```

---

## 9.4 修改工单基础信息

```http
PUT /api/v1/tickets/{ticket_id}
```

权限：ticket:update

请求参数：

```json
{
  "title": "办公电脑无法开机",
  "description": "按下电源键后主机没有反应，显示器无信号。",
  "fault_type": "hardware",
  "priority": "high",
  "asset_id": 1
}
```

成功响应：

```json
{
  "code": 0,
  "message": "工单修改成功",
  "data": null
}
```

业务规则：

```text
1. 非 admin 用户只能修改自己创建且 status = pending 的工单；
2. RBAC 角色码包含 admin 的用户可以修改全部工单；
3. processing、completed、cancelled 状态下，非 admin 用户不允许修改基础信息；
4. 修改后记录操作日志。
```

---

## 9.5 派单

```http
PATCH /api/v1/tickets/{ticket_id}/assign
```

权限：ticket:assign

请求参数：

```json
{
  "handler_id": 2,
  "remark": "派给张工处理"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "派单成功",
  "data": {
    "id": 1,
    "status": "assigned",
    "handler_id": 2,
    "assigned_at": "2026-06-23 10:00:00",
    "first_response_at": "2026-06-23 10:00:00"
  }
}
```

业务规则：

```text
1. 只有 pending 状态允许派单；
2. handler_id 对应用户必须存在；
3. handler 用户 role 必须为 it_staff 或 admin；
4. 派单后 status = assigned；
5. 更新 handler_id、assigned_at；
6. 如果 first_response_at 为空，则写入当前时间；如果已有值，不覆盖；
7. 写入 it_ticket_record，action = assign；
8. 记录操作日志。
```

---

## 9.6 接单并开始处理

```http
PATCH /api/v1/tickets/{ticket_id}/start
```

权限：ticket:start

请求参数：

```json
{
  "remark": "开始排查故障"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "工单已开始处理",
  "data": {
    "id": 1,
    "status": "processing",
    "started_at": "2026-06-23 10:15:00",
    "first_response_at": "2026-06-23 10:00:00"
  }
}
```

业务规则：

```text
1. assigned 状态允许开始处理；
2. 非 admin 用户只能开始处理分配给自己的工单；
3. RBAC 角色码包含 admin 的用户可以开始处理任意 assigned 工单；
4. 如果工单 handler_id 为空，IT 人员开始处理时自动设置 handler_id = 当前用户ID；
5. 开始处理后 status = processing；
6. 更新 started_at；
7. 如果 first_response_at 为空，则写入当前时间；如果已有值，不覆盖；
8. 如果工单关联了 asset_id，则将资产状态改为 repairing；
9. 写入 it_ticket_record，action = start；
10. 记录操作日志。
```

---

## 9.7 完成工单

```http
PATCH /api/v1/tickets/{ticket_id}/complete
```

权限：ticket:complete

请求参数：

```json
{
  "result": "重新插拔内存并清理机箱灰尘后恢复正常。",
  "fault_reason": "内存接触不良，主机内部灰尘较多",
  "repair_method": "重新插拔内存条并清理机箱灰尘",
  "repair_result": "fixed",
  "repair_cost": 0.0,
  "asset_status_after_repair": "in_use",
  "remark": "工单处理完成"
}
```

字段说明：

| 字段                        | 类型     | 必填 | 说明                                             |
| ------------------------- | ------ | -- | ---------------------------------------------- |
| result                    | string | 是  | 工单处理结果                                         |
| fault_reason              | string | 否  | 故障原因                                           |
| repair_method             | string | 否  | 维修方法                                           |
| repair_result             | string | 是  | fixed / replace_repair / scrapped / unresolved |
| repair_cost               | number | 否  | 维修费用                                           |
| asset_status_after_repair | string | 否  | in_use / repairing / scrapped                  |
| remark                    | string | 否  | 流转备注                                           |

成功响应：

```json
{
  "code": 0,
  "message": "工单已完成",
  "data": {
    "id": 1,
    "status": "completed",
    "completed_at": "2026-06-23 11:00:00",
    "resolved_at": "2026-06-23 11:00:00"
  }
}
```

业务规则：

```text
1. 只有 processing 状态允许完成；
2. 非 admin 用户只能完成分配给自己的工单；
3. RBAC 角色码包含 admin 的用户可以完成任意 processing 工单；
4. 完成后 status = completed；
5. 更新 result、completed_at、resolved_at；
6. 如果工单关联 asset_id：
   - 创建 it_repair_record 维修记录；
   - 根据 asset_status_after_repair 更新资产状态；
   - 如果 repair_result = fixed 或 replace_repair，默认资产状态改为 in_use；
   - 如果 repair_result = scrapped，资产状态改为 scrapped；
   - 如果 repair_result = unresolved，资产状态保持 repairing；
7. 写入 it_ticket_record，action = finish；
8. 记录操作日志。
```

---

## 9.8 取消工单

```http
PATCH /api/v1/tickets/{ticket_id}/cancel
```

权限：ticket:cancel

请求参数：

```json
{
  "reason": "问题已自行解决，不需要处理"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "工单已取消",
  "data": {
    "id": 1,
    "status": "cancelled"
  }
}
```

业务规则：

```text
1. 非 admin 用户只能取消自己创建且 status = pending 的工单；
2. RBAC 角色码包含 admin 的用户可以取消 pending、assigned 状态工单；
3. processing、completed 状态不允许取消；
4. 取消后 status = cancelled；
5. 写入 it_ticket_record，action = cancel；
6. 记录操作日志。
```

---

## 9.9 删除工单

```http
DELETE /api/v1/tickets/{ticket_id}
```

权限：ticket:delete

成功响应：

```json
{
  "code": 0,
  "message": "工单删除成功",
  "data": null
}
```

业务规则：

```text
1. 第一版建议不做物理删除；
2. 如果必须实现，只允许删除 pending 或 cancelled 状态工单；
3. 如果已有维修记录，不允许删除；
4. 推荐通过 cancelled 状态代替删除。
```

---

# 10. 工单流转记录 Ticket Record API

## 10.1 查询指定工单流转记录

```http
GET /api/v1/tickets/{ticket_id}/records
```

权限：ticket:records，并且需要满足工单数据范围

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "ticket_id": 1,
      "operator_id": 3,
      "operator_name": "李明",
      "from_status": null,
      "to_status": "pending",
      "action": "create",
      "remark": "用户提交电脑无法开机工单",
      "created_at": "2026-06-21 09:10:00"
    },
    {
      "id": 2,
      "ticket_id": 1,
      "operator_id": 1,
      "operator_name": "系统管理员",
      "from_status": "pending",
      "to_status": "assigned",
      "action": "assign",
      "remark": "管理员将工单派给张工处理",
      "created_at": "2026-06-21 09:20:00"
    }
  ]
}
```

业务规则：

```text
1. 流转记录只允许查询，不提供手动新增、修改、删除接口；
2. 记录由工单业务接口自动写入。
```

---

# 11. 维修记录 Repair Record API

## 11.1 查询维修记录列表

```http
GET /api/v1/repair-records
```

权限：repair_record:view

查询参数：

| 参数             | 类型     | 必填 | 说明     |
| -------------- | ------ | -- | ------ |
| asset_id       | int    | 否  | 资产ID   |
| ticket_id      | int    | 否  | 工单ID   |
| repair_user_id | int    | 否  | 维修人员ID |
| repair_result  | string | 否  | 维修结果   |
| start_date     | string | 否  | 维修开始日期 |
| end_date       | string | 否  | 维修结束日期 |
| page           | int    | 否  | 页码     |
| page_size      | int    | 否  | 每页数量   |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "ticket_id": 1,
        "ticket_no": "TK202606210001",
        "ticket_title": "财务电脑无法开机",
        "asset_id": 1,
        "asset_no": "IT-PC-2026-0001",
        "asset_name": "财务部办公电脑",
        "repair_user_id": 2,
        "repair_user_name": "张工",
        "fault_reason": "内存接触不良，主机内部灰尘较多",
        "repair_method": "重新插拔内存条并清理机箱灰尘",
        "repair_result": "fixed",
        "repair_cost": 0.0,
        "repaired_at": "2026-06-21 10:10:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

业务规则：

```text
1. 维修记录主要由完成工单接口自动生成；
2. 第一版不提供手动创建维修记录接口；
3. 如需修改维修记录，只允许 admin 修改。
```

---

## 11.2 查询维修记录详情

```http
GET /api/v1/repair-records/{record_id}
```

权限：repair_record:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "ticket_id": 1,
    "ticket_no": "TK202606210001",
    "asset_id": 1,
    "asset_no": "IT-PC-2026-0001",
    "asset_name": "财务部办公电脑",
    "repair_user_id": 2,
    "repair_user_name": "张工",
    "fault_reason": "内存接触不良，主机内部灰尘较多",
    "repair_method": "重新插拔内存条并清理机箱灰尘",
    "repair_result": "fixed",
    "repair_cost": 0.0,
    "repaired_at": "2026-06-21 10:10:00",
    "created_at": "2026-06-21 10:10:00"
  }
}
```

---

## 11.3 修改维修记录

```http
PUT /api/v1/repair-records/{record_id}
```

权限：repair_record:update

请求参数：

```json
{
  "fault_reason": "内存接触不良",
  "repair_method": "重新插拔内存并清理灰尘",
  "repair_result": "fixed",
  "repair_cost": 0.0,
  "repaired_at": "2026-06-21 10:10:00"
}
```

成功响应：

```json
{
  "code": 0,
  "message": "维修记录修改成功",
  "data": null
}
```

---

# 12. 操作日志 Operation Log API

## 12.1 查询操作日志列表

```http
GET /api/v1/operation-logs
```

权限：operation_log:view

查询参数：

| 参数               | 类型     | 必填 | 说明             |
| ---------------- | ------ | -- | -------------- |
| user_id          | int    | 否  | 操作用户ID         |
| module_name      | string | 否  | 模块名称           |
| operation_type   | string | 否  | 操作类型           |
| operation_result | string | 否  | success / fail |
| start_date       | string | 否  | 开始日期           |
| end_date         | string | 否  | 结束日期           |
| page             | int    | 否  | 页码             |
| page_size        | int    | 否  | 每页数量           |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "real_name": "系统管理员",
        "module_name": "用户登录",
        "operation_type": "login",
        "business_id": null,
        "request_method": "POST",
        "request_url": "/api/v1/auth/login",
        "request_ip": "192.168.1.10",
        "operation_result": "success",
        "error_message": null,
        "created_at": "2026-06-21 08:50:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

业务规则：

```text
1. 操作日志由系统自动写入；
2. 第一版不提供新增、修改、删除日志接口；
3. 登录、创建工单、修改工单状态、创建资产、修改资产等关键操作都应记录日志。
```

---

# 13. 首页统计 Dashboard API

## 13.1 查询首页统计卡片

```http
GET /api/v1/dashboard/summary
```

权限：dashboard:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "ticket_total": 128,
    "ticket_pending": 12,
    "ticket_processing": 8,
    "ticket_completed": 100,
    "asset_total": 86,
    "asset_in_use": 70,
    "asset_repairing": 5,
    "asset_scrapped": 3
  }
}
```

统计规则：

```text
ticket_total：工单总数
ticket_pending：pending 状态工单数量
ticket_processing：processing 状态工单数量
ticket_completed：completed 状态工单数量
asset_total：资产总数
asset_in_use：in_use 状态资产数量
asset_repairing：repairing 状态资产数量
asset_scrapped：scrapped 状态资产数量
```

---

## 13.2 查询最近 7 天工单趋势

```http
GET /api/v1/dashboard/ticket-trend
```

权限：dashboard:view

查询参数：

| 参数   | 类型  | 必填 | 说明               |
| ---- | --- | -- | ---------------- |
| days | int | 否  | 最近多少天，默认 7，最大 30 |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "date": "2026-06-17",
      "count": 5
    },
    {
      "date": "2026-06-18",
      "count": 8
    },
    {
      "date": "2026-06-19",
      "count": 3
    }
  ]
}
```

统计规则：

```text
按照 it_ticket.created_at 的日期分组统计。
```

---

## 13.3 查询工单类型分布

```http
GET /api/v1/dashboard/ticket-fault-types
```

权限：dashboard:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "fault_type": "hardware",
      "fault_type_name": "硬件故障",
      "count": 20
    },
    {
      "fault_type": "network",
      "fault_type_name": "网络故障",
      "count": 15
    }
  ]
}
```

---

## 13.4 查询资产状态分布

```http
GET /api/v1/dashboard/asset-status
```

权限：dashboard:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "status": "in_use",
      "status_name": "在用",
      "count": 70
    },
    {
      "status": "repairing",
      "status_name": "维修中",
      "count": 5
    }
  ]
}
```

---

## 13.5 查询运维人员处理排行

```http
GET /api/v1/dashboard/handler-ranking
```

权限：dashboard:view

查询参数：

| 参数         | 类型     | 必填 | 说明         |
| ---------- | ------ | -- | ---------- |
| start_date | string | 否  | 开始日期       |
| end_date   | string | 否  | 结束日期       |
| limit      | int    | 否  | 返回数量，默认 10 |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "handler_id": 2,
      "handler_name": "张工",
      "completed_count": 36
    }
  ]
}
```

统计规则：

```text
统计 completed 状态工单，按照 handler_id 分组。
```

---

# 14. FAQ 常见问题 API

FAQ 用于维护企业内部 IT 常见问题，例如电脑无法联网、打印机卡纸、账号无法登录、ERP 系统异常等。普通员工可以查看启用状态 FAQ，减少重复报修；管理员可以在后台新增、修改、停用、删除 FAQ。

对应数据库表：

```text
it_faq
```

## 14.1 查询 FAQ 列表

```http
GET /api/v1/faqs
```

权限：faq:view

查询参数：

| 参数        | 类型     | 必填 | 说明                                             |
| --------- | ------ | -- | ---------------------------------------------- |
| keyword   | string | 否  | 按标题、摘要、内容模糊查询                                  |
| category  | string | 否  | computer / network / printer / account / other |
| status    | int    | 否  | 状态：1启用，0停用                                     |
| page      | int    | 否  | 当前页码，默认 1                                      |
| page_size | int    | 否  | 每页数量，默认 10，最大 100                              |

请求示例：

```http
GET /api/v1/faqs?keyword=打印机&category=printer&page=1&page_size=10
```

权限过滤规则：

```text
1. admin 可以查看全部 FAQ，包括启用和停用；
2. it_staff 可以查看全部 FAQ；
3. employee 只能查看 status = 1 的 FAQ；
4. 如果 employee 传入 status = 0，后端忽略该参数并只返回启用 FAQ。
```

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "打印机卡纸应该如何处理？",
        "category": "printer",
        "category_name": "打印机问题",
        "summary": "打印机卡纸时的基础处理步骤",
        "view_count": 28,
        "sort_order": 1,
        "status": 1,
        "created_at": "2026-06-21 08:00:00",
        "updated_at": "2026-06-21 08:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

业务规则：

```text
1. 按 sort_order ASC、created_at DESC 排序；
2. keyword 同时匹配 title、summary、content；
3. employee 只能看到启用状态 FAQ；
4. 列表接口不返回 content 全文，避免数据过大；
5. 查询列表不增加 view_count。
```

---

## 14.2 创建 FAQ

```http
POST /api/v1/faqs
```

权限：faq:create

请求参数：

```json
{
  "title": "打印机卡纸应该如何处理？",
  "category": "printer",
  "summary": "打印机卡纸时的基础处理步骤",
  "content": "1. 先停止打印任务；2. 打开打印机后盖；3. 按照纸张方向缓慢取出卡纸；4. 检查纸盒纸张是否受潮；5. 如果仍无法恢复，请提交 IT 报修工单。",
  "sort_order": 1,
  "status": 1
}
```

字段说明：

| 字段         | 类型     | 必填 | 说明              |
| ---------- | ------ | -- | --------------- |
| title      | string | 是  | 问题标题，最大 200 字符  |
| category   | string | 是  | FAQ 分类          |
| summary    | string | 否  | 问题摘要，最大 255 字符  |
| content    | string | 是  | 问题详细内容          |
| sort_order | int    | 否  | 排序值，越小越靠前，默认 0  |
| status     | int    | 否  | 状态：1启用，0停用，默认 1 |

成功响应：

```json
{
  "code": 0,
  "message": "FAQ 创建成功",
  "data": {
    "id": 1
  }
}
```

业务规则：

```text
1. title 不允许为空；
2. content 不允许为空；
3. category 必须是 computer、network、printer、account、other 之一；
4. status 只能是 1 或 0；
5. view_count 创建时默认为 0；
6. 创建成功后记录操作日志。
```

---

## 14.3 查询 FAQ 详情

```http
GET /api/v1/faqs/{faq_id}
```

权限：faq:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "打印机卡纸应该如何处理？",
    "category": "printer",
    "category_name": "打印机问题",
    "summary": "打印机卡纸时的基础处理步骤",
    "content": "1. 先停止打印任务；2. 打开打印机后盖；3. 按照纸张方向缓慢取出卡纸；4. 检查纸盒纸张是否受潮；5. 如果仍无法恢复，请提交 IT 报修工单。",
    "view_count": 29,
    "sort_order": 1,
    "status": 1,
    "created_at": "2026-06-21 08:00:00",
    "updated_at": "2026-06-21 08:00:00"
  }
}
```

业务规则：

```text
1. FAQ 不存在，返回 404；
2. employee 查询 status = 0 的 FAQ 时返回 404；
3. 查询详情成功后，view_count 自动加 1；
4. 第一版 admin、it_staff 查询详情也统一增加 view_count。
```

---

## 14.4 修改 FAQ

```http
PUT /api/v1/faqs/{faq_id}
```

权限：faq:update

请求参数：

```json
{
  "title": "打印机卡纸如何处理？",
  "category": "printer",
  "summary": "打印机卡纸的常见处理方法",
  "content": "1. 取消当前打印任务；2. 打开打印机后盖；3. 按纸张出纸方向取出卡纸；4. 检查纸盒纸张是否受潮或变形；5. 无法解决时提交 IT 报修。",
  "sort_order": 1,
  "status": 1
}
```

成功响应：

```json
{
  "code": 0,
  "message": "FAQ 修改成功",
  "data": null
}
```

业务规则：

```text
1. FAQ 不存在，返回 404；
2. category 必须合法；
3. status 只能是 1 或 0；
4. 不通过该接口修改 view_count；
5. 修改成功后记录操作日志。
```

---

## 14.5 修改 FAQ 状态

```http
PATCH /api/v1/faqs/{faq_id}/status
```

权限：faq:status

请求参数：

```json
{
  "status": 0
}
```

成功响应：

```json
{
  "code": 0,
  "message": "FAQ 状态修改成功",
  "data": null
}
```

业务规则：

```text
1. status 只能是 1 或 0；
2. status = 1 表示启用；
3. status = 0 表示停用；
4. 停用后的 FAQ 普通员工不可见；
5. 修改成功后记录操作日志。
```

---

## 14.6 删除 FAQ

```http
DELETE /api/v1/faqs/{faq_id}
```

权限：faq:delete

成功响应：

```json
{
  "code": 0,
  "message": "FAQ 删除成功",
  "data": null
}
```

业务规则：

```text
1. FAQ 不存在，返回 404；
2. 第一版可以物理删除；
3. 更推荐通过 status = 0 停用 FAQ；
4. 删除成功后记录操作日志。
```

---

## 14.7 查询 FAQ 分类数量

```http
GET /api/v1/faqs/category-stats
```

权限：faq:stats

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "category": "computer",
      "category_name": "电脑问题",
      "count": 6
    },
    {
      "category": "network",
      "category_name": "网络问题",
      "count": 3
    },
    {
      "category": "printer",
      "category_name": "打印机问题",
      "count": 5
    },
    {
      "category": "account",
      "category_name": "账号系统问题",
      "count": 4
    },
    {
      "category": "other",
      "category_name": "其他问题",
      "count": 2
    }
  ]
}
```

业务规则：

```text
1. employee 只统计 status = 1 的 FAQ；
2. admin、it_staff 可统计全部 FAQ；
3. 按固定分类顺序返回：computer、network、printer、account、other。
```

---

# 15. 通知中心 Notification API

通知中心用于保存系统消息、工单提醒、SLA 超时提醒、资产相关提醒等站内消息。

对应数据库表：

```text
it_notification
```

通用规则：

```text
1. 所有接口都需要登录；
2. 只能查询和操作当前登录用户自己的通知；
3. 列表接口自动排除 deleted = 1 的通知；
4. 删除接口均为逻辑删除，设置 deleted = 1；
5. 批量接口 ids 不能为空，一次最多 100 条；
6. 批量接口会忽略不存在、已删除或不属于当前用户的通知。
```

## 15.1 查询当前用户通知列表

```http
GET /api/v1/notifications
```

权限：登录用户

查询参数：

| 参数        | 类型     | 必填 | 默认值 | 说明                         |
| --------- | ------ | -- | --- | -------------------------- |
| page      | int    | 否  | 1   | 页码                         |
| page_size | int    | 否  | 10  | 每页数量，最大 100                |
| read_status | int | 否  | -   | 阅读状态：0未读，1已读              |
| biz_type  | string | 否  | -   | ticket / asset / sla / system |
| keyword   | string | 否  | -   | 按标题或内容模糊搜索                 |

请求示例：

```http
GET /api/v1/notifications?page=1&page_size=10&read_status=0&biz_type=ticket
```

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 2,
        "title": "新工单分派提醒",
        "content": "工单 TK202606210001 已分派给你，请及时处理。",
        "biz_type": "ticket",
        "biz_id": 1,
        "read_status": 0,
        "created_at": "2026-06-23 18:05:00",
        "read_at": null
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

---

## 15.2 查询未读通知数量

```http
GET /api/v1/notifications/unread-count
```

权限：登录用户

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "unread_count": 5
  }
}
```

---

## 15.3 标记单条通知为已读

```http
PUT /api/v1/notifications/{notification_id}/read
```

权限：登录用户

路径参数：

| 参数              | 类型  | 必填 | 说明   |
| --------------- | --- | -- | ---- |
| notification_id | int | 是  | 通知ID |

成功响应：

```json
{
  "code": 0,
  "message": "标记已读成功",
  "data": {
    "id": 2,
    "title": "新工单分派提醒",
    "content": "工单 TK202606210001 已分派给你，请及时处理。",
    "biz_type": "ticket",
    "biz_id": 1,
    "read_status": 1,
    "created_at": "2026-06-23 18:05:00",
    "read_at": "2026-06-24 10:00:00"
  }
}
```

业务规则：

```text
1. 只能操作当前登录用户自己的通知；
2. 通知不存在、已删除或不属于当前用户，返回 404；
3. 已读通知重复调用保持幂等，不报错；
4. 未读通知会设置 read_status = 1，并写入 read_at。
```

---

## 15.4 批量标记通知为已读

```http
PUT /api/v1/notifications/read-batch
```

权限：登录用户

请求参数：

```json
{
  "ids": [1, 2, 3]
}
```

成功响应：

```json
{
  "code": 0,
  "message": "批量标记已读成功",
  "data": {
    "processed_count": 2
  }
}
```

业务规则：

```text
1. ids 不能为空，最多 100 条；
2. 只处理当前登录用户自己的未删除通知；
3. 忽略不存在、已删除或不属于当前用户的通知；
4. 只统计本次从未读变为已读的通知数量。
```

---

## 15.5 全部标记为已读

```http
PUT /api/v1/notifications/read-all
```

权限：登录用户

成功响应：

```json
{
  "code": 0,
  "message": "全部标记已读成功",
  "data": {
    "processed_count": 5
  }
}
```

业务规则：

```text
将当前登录用户所有未读且未删除的通知设置为已读，并写入 read_at。
```

---

## 15.6 删除单条通知

```http
DELETE /api/v1/notifications/{notification_id}
```

权限：登录用户

成功响应：

```json
{
  "code": 0,
  "message": "通知删除成功",
  "data": null
}
```

业务规则：

```text
1. 逻辑删除，设置 deleted = 1；
2. 只能删除当前登录用户自己的通知；
3. 通知不存在、已删除或不属于当前用户，返回 404。
```

---

## 15.7 批量删除通知

```http
DELETE /api/v1/notifications/batch
```

权限：登录用户

请求参数：

```json
{
  "ids": [1, 2, 3]
}
```

成功响应：

```json
{
  "code": 0,
  "message": "批量删除成功",
  "data": {
    "processed_count": 2
  }
}
```

业务规则：

```text
1. ids 不能为空，最多 100 条；
2. 逻辑删除，设置 deleted = 1；
3. 只处理当前登录用户自己的未删除通知；
4. 忽略不存在、已删除或不属于当前用户的通知。
```

---

## 15.8 内部创建通知方法

通知创建方法不暴露前端接口，供工单分派、SLA 定时任务、资产审批等内部模块调用。

```python
from app.services.notification_service import create_notification

create_notification(
    db,
    user_id=2,
    title="新工单分派提醒",
    content="工单 TK202606210001 已分派给你，请及时处理。",
    biz_type="ticket",
    biz_id=1,
)
```

---

## 15.9 curl 测试示例

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/notifications?page=1&page_size=10"
```

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/notifications/unread-count"
```

```bash
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/notifications/1/read"
```

```bash
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"ids\":[1,2,3]}" \
  "http://127.0.0.1:8000/api/v1/notifications/read-batch"
```

```bash
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/notifications/read-all"
```

```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/notifications/1"
```

```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"ids\":[1,2,3]}" \
  "http://127.0.0.1:8000/api/v1/notifications/batch"
```

---

# 16. 字典接口 Dict API

为了方便前端渲染下拉框，提供统一字典接口。

## 16.1 查询所有字典

```http
GET /api/v1/dicts
```

权限：dict:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "roles": [
      {
        "label": "管理员",
        "value": "admin"
      },
      {
        "label": "IT运维人员",
        "value": "it_staff"
      },
      {
        "label": "普通员工",
        "value": "employee"
      }
    ],
    "ticket_status": [
      {
        "label": "待受理",
        "value": "pending"
      },
      {
        "label": "已派单",
        "value": "assigned"
      },
      {
        "label": "处理中",
        "value": "processing"
      },
      {
        "label": "已完成",
        "value": "completed"
      },
      {
        "label": "已取消",
        "value": "cancelled"
      }
    ],
    "ticket_priority": [
      {
        "label": "低",
        "value": "low"
      },
      {
        "label": "普通",
        "value": "normal"
      },
      {
        "label": "高",
        "value": "high"
      },
      {
        "label": "紧急",
        "value": "urgent"
      }
    ],
    "fault_type": [
      {
        "label": "硬件故障",
        "value": "hardware"
      },
      {
        "label": "软件故障",
        "value": "software"
      },
      {
        "label": "网络故障",
        "value": "network"
      },
      {
        "label": "打印机故障",
        "value": "printer"
      },
      {
        "label": "账号权限问题",
        "value": "account"
      },
      {
        "label": "其他",
        "value": "other"
      }
    ],
    "asset_status": [
      {
        "label": "在用",
        "value": "in_use"
      },
      {
        "label": "闲置",
        "value": "idle"
      },
      {
        "label": "维修中",
        "value": "repairing"
      },
      {
        "label": "已报废",
        "value": "scrapped"
      }
    ],
    "faq_category": [
      {
        "label": "电脑问题",
        "value": "computer"
      },
      {
        "label": "网络问题",
        "value": "network"
      },
      {
        "label": "打印机问题",
        "value": "printer"
      },
      {
        "label": "账号系统问题",
        "value": "account"
      },
      {
        "label": "其他问题",
        "value": "other"
      }
    ]
  }
}
```

---

# 17. RBAC 权限管理 API

RBAC 管理接口用于维护角色、查看权限、分配角色权限和分配用户角色。

所有角色、权限、用户角色、角色权限相关操作都会写入 `sys_operation_log`。

## 17.1 查询角色列表

```http
GET /api/v1/roles
```

权限：role:view

查询参数：

| 参数        | 类型     | 必填 | 说明          |
| --------- | ------ | -- | ----------- |
| keyword   | string | 否  | 角色编码或名称模糊查询 |
| status    | int    | 否  | 1启用，0停用     |
| page      | int    | 否  | 页码          |
| page_size | int    | 否  | 每页数量        |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "role_code": "admin",
        "role_name": "系统管理员",
        "description": "拥有系统全部权限",
        "sort_order": 1,
        "status": 1,
        "created_at": "2026-06-23 17:18:35",
        "updated_at": "2026-06-23 17:18:35"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 100,
    "pages": 1
  }
}
```

---

## 17.2 创建角色

```http
POST /api/v1/roles
```

权限：role:create

请求参数：

```json
{
  "role_code": "asset_manager",
  "role_name": "资产管理员",
  "description": "负责资产台账维护",
  "sort_order": 4,
  "status": 1
}
```

业务规则：

```text
1. role_code 不允许重复；
2. status 只能为 1 或 0；
3. 创建成功后记录操作日志。
```

---

## 17.3 查询角色详情

```http
GET /api/v1/roles/{role_id}
```

权限：role:view

---

## 17.4 修改角色

```http
PUT /api/v1/roles/{role_id}
```

权限：role:update

请求参数：

```json
{
  "role_name": "资产管理员",
  "description": "负责资产台账维护和状态变更",
  "sort_order": 4,
  "status": 1
}
```

---

## 17.5 修改角色状态

```http
PATCH /api/v1/roles/{role_id}/status
```

权限：role:update

请求参数：

```json
{
  "status": 0
}
```

---

## 17.6 删除角色

```http
DELETE /api/v1/roles/{role_id}
```

权限：role:delete

业务规则：

```text
1. 角色不存在，返回 404；
2. 角色已关联用户或权限时，不允许删除；
3. 删除成功后记录操作日志。
```

---

## 17.7 查询权限列表

```http
GET /api/v1/permissions
```

权限：permission:view

查询参数：

| 参数          | 类型     | 必填 | 说明           |
| ----------- | ------ | -- | ------------ |
| keyword     | string | 否  | 权限编码或名称模糊查询 |
| module_name | string | 否  | 模块名称         |
| status      | int    | 否  | 1启用，0停用      |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 40,
      "permission_code": "ticket:view_all",
      "permission_name": "查看全部工单",
      "module_name": "工单管理",
      "permission_type": "api",
      "api_method": "GET",
      "api_path": "/api/v1/tickets",
      "description": "查看全部工单",
      "sort_order": 40,
      "status": 1,
      "created_at": "2026-06-23 17:18:49",
      "updated_at": "2026-06-23 17:18:49"
    }
  ]
}
```

---

## 17.8 查询分组权限

```http
GET /api/v1/permissions/grouped
```

权限：permission:view

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "module_name": "工单管理",
      "permissions": [
        {
          "id": 40,
          "permission_code": "ticket:view_all",
          "permission_name": "查看全部工单",
          "module_name": "工单管理",
          "permission_type": "api",
          "api_method": "GET",
          "api_path": "/api/v1/tickets",
          "description": "查看全部工单",
          "sort_order": 40,
          "status": 1,
          "created_at": "2026-06-23 17:18:49",
          "updated_at": "2026-06-23 17:18:49"
        }
      ]
    }
  ]
}
```

---

## 17.9 查询角色权限

```http
GET /api/v1/roles/{role_id}/permissions
```

权限：role:view

成功响应：返回该角色已绑定的权限列表。

---

## 17.10 分配角色权限

```http
PUT /api/v1/roles/{role_id}/permissions
```

权限：role:assign_permission

请求参数：

```json
{
  "permission_ids": [40, 41, 42, 47]
}
```

业务规则：

```text
1. role_id 必须存在；
2. permission_ids 中的权限必须全部存在；
3. 后端先删除该角色旧权限，再插入新权限；
4. 分配成功后记录操作日志。
```

---

## 17.11 查询用户角色

```http
GET /api/v1/users/{user_id}/roles
```

权限：user:view 或 user:assign_role

成功响应：返回用户已绑定的角色列表。

---

## 17.12 分配用户角色

```http
PUT /api/v1/users/{user_id}/roles
```

权限：user:assign_role

请求参数：

```json
{
  "role_ids": [3]
}
```

业务规则：

```text
1. user_id 必须存在；
2. role_ids 中的角色必须全部存在；
3. 后端先删除该用户旧角色，再插入新角色；
4. 分配成功后记录操作日志。
```

---

# 18. SLA 规则管理 API

SLA 规则用于在创建工单时自动计算：

```text
sla_response_deadline  响应截止时间
sla_resolve_deadline   处理完成截止时间
```

当前版本只使用自然时间计算，不处理工作日、节假日和工作时间段。

## 18.1 查询 SLA 规则列表

```http
GET /api/v1/sla-rules
```

权限：sla:rule:list

查询参数：

| 参数            | 类型     | 必填 | 说明                              |
| ------------- | ------ | -- | ------------------------------- |
| priority      | string | 否  | urgent / high / medium / low    |
| ticket_category | string | 否 | hardware / software / network / printer / account / other |
| enabled       | int    | 否  | 1启用，0停用                       |
| page          | int    | 否  | 页码，默认 1                       |
| page_size     | int    | 否  | 每页数量，默认 10，最大 100           |

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "紧急工单通用SLA",
        "ticket_category": null,
        "priority": "urgent",
        "response_minutes": 10,
        "resolve_minutes": 120,
        "enabled": 1,
        "sort_order": 10,
        "created_at": "2026-06-24 00:00:00",
        "updated_at": "2026-06-24 00:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "pages": 1
  }
}
```

---

## 18.2 创建 SLA 规则

```http
POST /api/v1/sla-rules
```

权限：sla:rule:create

请求参数：

```json
{
  "name": "网络故障紧急SLA",
  "ticket_category": "network",
  "priority": "urgent",
  "response_minutes": 5,
  "resolve_minutes": 60,
  "enabled": 1,
  "sort_order": 1
}
```

字段说明：

| 字段               | 类型     | 必填 | 说明                                      |
| ---------------- | ------ | -- | --------------------------------------- |
| name             | string | 是  | 规则名称                                    |
| ticket_category  | string | 否  | 工单类型；为空表示通用规则                         |
| priority         | string | 是  | urgent / high / medium / low            |
| response_minutes | int    | 是  | 响应时限，单位分钟，必须大于 0                      |
| resolve_minutes  | int    | 是  | 处理完成时限，单位分钟，必须大于 0，且大于等于响应时限 |
| enabled          | int    | 否  | 1启用，0停用，默认 1                          |
| sort_order       | int    | 否  | 排序值，越小越优先，默认 0                       |

成功响应：

```json
{
  "code": 0,
  "message": "SLA规则创建成功",
  "data": {
    "id": 6,
    "name": "网络故障紧急SLA",
    "ticket_category": "network",
    "priority": "urgent",
    "response_minutes": 5,
    "resolve_minutes": 60,
    "enabled": 1,
    "sort_order": 1
  }
}
```

业务规则：

```text
1. priority 只能为 urgent、high、medium、low；
2. response_minutes 必须大于 0；
3. resolve_minutes 必须大于 0；
4. resolve_minutes 必须大于或等于 response_minutes；
5. enabled 只能为 1 或 0；
6. 创建成功后记录操作日志。
```

---

## 18.3 修改 SLA 规则

```http
PUT /api/v1/sla-rules/{id}
```

权限：sla:rule:update

请求参数：

```json
{
  "name": "高优先级通用SLA",
  "ticket_category": null,
  "priority": "high",
  "response_minutes": 30,
  "resolve_minutes": 240,
  "enabled": 1,
  "sort_order": 20
}
```

成功响应：

```json
{
  "code": 0,
  "message": "SLA规则修改成功",
  "data": {
    "id": 2,
    "name": "高优先级通用SLA",
    "ticket_category": null,
    "priority": "high",
    "response_minutes": 30,
    "resolve_minutes": 240,
    "enabled": 1,
    "sort_order": 20
  }
}
```

业务规则：

```text
1. 规则不存在返回 404；
2. 修改时执行与创建相同的数据校验；
3. 修改成功后记录操作日志。
```

---

## 18.4 启用或停用 SLA 规则

```http
PATCH /api/v1/sla-rules/{id}/enabled
```

权限：sla:rule:enable

请求参数：

```json
{
  "enabled": 0
}
```

成功响应：

```json
{
  "code": 0,
  "message": "SLA规则状态修改成功",
  "data": {
    "id": 2,
    "enabled": 0
  }
}
```

业务规则：

```text
1. enabled 只能为 1 或 0；
2. 规则不存在返回 404；
3. 修改成功后记录操作日志。
```

---

## 18.5 删除 SLA 规则

```http
DELETE /api/v1/sla-rules/{id}
```

权限：sla:rule:delete

成功响应：

```json
{
  "code": 0,
  "message": "SLA规则删除成功",
  "data": null
}
```

业务规则：

```text
1. 删除使用物理删除；
2. 规则不存在返回 404；
3. 删除成功后记录操作日志。
```

---

## 18.6 SLA 规则匹配与截止时间计算

规则匹配顺序：

```text
1. 优先匹配 ticket_category + priority 完全匹配且 enabled = 1 的规则；
2. 如果没有匹配到，则匹配 ticket_category IS NULL + priority 的通用规则；
3. 如果仍然没有匹配到，则使用兜底规则：response_minutes = 60，resolve_minutes = 480；
4. 多条规则同时匹配时，按 sort_order ASC、id ASC 排序。
```

截止时间计算：

```text
sla_response_deadline = created_at + response_minutes
sla_resolve_deadline = created_at + resolve_minutes
```

工单状态流转时间：

```text
首次进入 assigned 或 processing 状态时，如果 first_response_at 为空，则写入当前时间；
进入 completed 状态时，写入 resolved_at。
```

---

## 18.7 SLA 超时扫描定时任务

SLA 超时扫描是服务端后台任务，不对前端暴露 HTTP 接口。

调度方式：

```text
FastAPI 启动时根据配置启动 APScheduler；
FastAPI 停止时关闭 APScheduler；
默认每 5 分钟执行一次 check_ticket_sla_timeout。
```

配置项：

| 配置项                     | 默认值 | 说明                         |
| ------------------------ | --- | -------------------------- |
| SCHEDULER_ENABLED        | true | 是否启用 APScheduler 调度器       |
| SLA_CHECK_INTERVAL_MINUTES | 5 | SLA 超时扫描任务执行间隔，单位分钟 |

任务配置：

```text
job_id: check_ticket_sla_timeout
job_name: 检查工单SLA超时
max_instances: 1
coalesce: true
replace_existing: true
timezone: Asia/Shanghai
```

扫描范围：

```text
未完成、未取消的工单；
当前状态排除 completed、cancelled。
```

响应超时判断：

```text
当前时间 > sla_response_deadline
并且 first_response_at 为空
并且 response_overdue = 0
```

满足条件后：

```text
1. 更新 response_overdue = 1；
2. 写入站内信通知；
3. 通过 response_overdue 避免重复发送同类通知。
```

处理超时判断：

```text
当前时间 > sla_resolve_deadline
并且 resolved_at 为空
并且 resolve_overdue = 0
```

满足条件后：

```text
1. 更新 resolve_overdue = 1；
2. 写入站内信通知；
3. 通过 resolve_overdue 避免重复发送同类通知。
```

通知规则：

| 超时类型 | 标题       | 业务类型 | 接收人                         |
| ------ | -------- | ------ | ---------------------------- |
| 响应超时 | 工单响应已超时 | ticket | 优先 handler_id，否则 reporter_id |
| 处理超时 | 工单处理已超时 | ticket | 优先 handler_id，否则 reporter_id |

通知内容示例：

```text
工单 TK202606230001/办公电脑无法开机 已超过 SLA 响应时间，请尽快处理。
工单 TK202606230001/办公电脑无法开机 已超过 SLA 处理完成时间，请尽快处理。
```

日志要求：

```text
[Scheduler] APScheduler started
[Scheduler] APScheduler shutdown
[SLA Job] start checking ticket SLA timeout
[SLA Job] scanned=20 response_overdue=2 resolve_overdue=1
[SLA Job] finished
```

部署说明：

```text
当前 APScheduler 方案适合单 worker 部署；
如果生产环境使用多个 worker，需要只在一个进程开启 SCHEDULER_ENABLED，
或改为独立 scheduler 进程、Celery Beat、分布式锁、数据库锁等方案。
```

验证方式：

```text
1. 设置 SCHEDULER_ENABLED=true；
2. 将 SLA_CHECK_INTERVAL_MINUTES 临时设置为 1；
3. 启动 FastAPI，观察 APScheduler started 日志；
4. 构造一个超过 sla_response_deadline 且 first_response_at 为空的未完成工单；
5. 等待任务执行后确认 response_overdue = 1，并生成站内信；
6. 构造一个超过 sla_resolve_deadline 且 resolved_at 为空的未完成工单；
7. 等待任务执行后确认 resolve_overdue = 1，并生成站内信；
8. 再次执行任务，同一工单同一超时类型不应重复生成通知；
9. 停止 FastAPI，观察 APScheduler shutdown 日志。
```

---

# 19. 工单状态流转规则

工单状态只能按照以下规则流转：

```text
pending    -> assigned
pending    -> cancelled
assigned   -> processing
assigned   -> cancelled
processing -> completed
```

禁止：

```text
completed  -> 任意状态
cancelled  -> 任意状态
pending    -> completed
assigned   -> completed
processing -> cancelled
```

如果状态流转非法，返回：

```json
{
  "code": 40900,
  "message": "当前工单状态不允许执行该操作",
  "data": null
}
```

---

# 20. 后端实现要求

## 20.1 FastAPI 路由建议

建议拆分以下 router：

```text
app/api/v1/routers/auth.py
app/api/v1/routers/users.py
app/api/v1/routers/assets.py
app/api/v1/routers/asset_categories.py
app/api/v1/routers/tickets.py
app/api/v1/routers/repair_records.py
app/api/v1/routers/operation_logs.py
app/api/v1/routers/dashboard.py
app/api/v1/routers/dicts.py
app/api/v1/routers/faqs.py
app/api/v1/routers/notifications.py
app/api/v1/routers/sla_rules.py
app/routers/rbac.py
app/scheduler/scheduler.py
app/scheduler/jobs.py
```

---

## 20.2 定时任务目录建议

建议将 APScheduler 相关代码拆分到独立目录：

```text
app/scheduler/__init__.py
app/scheduler/scheduler.py   创建、启动、关闭调度器
app/scheduler/jobs.py        定时任务入口
```

不要把大量定时任务逻辑直接写在 `main.py` 中；`main.py` 只负责在 FastAPI
生命周期中调用 `start_scheduler()` 和 `shutdown_scheduler()`。

---

## 20.3 Service 层建议

建议拆分以下 service：

```text
app/services/auth_service.py
app/services/user_service.py
app/services/asset_service.py
app/services/ticket_service.py
app/services/repair_service.py
app/services/log_service.py
app/services/dashboard_service.py
app/services/faq_service.py
app/services/notification_service.py
app/services/rbac_service.py
app/services/sla_service.py
```

---

## 20.4 数据模型建议

建议拆分以下 model：

```text
app/models/user.py
app/models/asset_category.py
app/models/asset.py
app/models/ticket.py
app/models/ticket_record.py
app/models/repair_record.py
app/models/operation_log.py
app/models/faq.py
app/models/notification.py
app/models/rbac.py
app/models/sla_rule.py
```

---

## 20.5 Pydantic Schema 建议

建议拆分以下 schema：

```text
app/schemas/auth_schema.py
app/schemas/user_schema.py
app/schemas/asset_schema.py
app/schemas/ticket_schema.py
app/schemas/repair_schema.py
app/schemas/common_schema.py
app/schemas/faq_schema.py
app/schemas/notification_schema.py
app/schemas/rbac_schema.py
app/schemas/sla_rule_schema.py
```

---

## 20.6 统一响应工具

请封装统一响应方法：

```python
def success(data=None, message="success"):
    return {
        "code": 0,
        "message": message,
        "data": data
    }

def fail(code=40000, message="操作失败", data=None):
    return {
        "code": code,
        "message": message,
        "data": data
    }
```

---

## 20.7 权限校验要求

需要实现依赖函数：

```text
get_current_user
get_user_permission_codes
require_permissions
```

示例：

```text
require_permissions("user:view")
require_permissions("ticket:view_all", "ticket:view_self", require_all=False)
```

兼容说明：

```text
sys_user.role 可以继续作为用户基础信息字段返回；
业务接口授权必须基于 RBAC 表查询得到的 permission_code；
如需识别 admin 全量数据操作能力，应从 sys_user_role / sys_role 查询角色编码，不读取 sys_user.role。
```

---

## 20.8 定时任务配置要求

依赖要求：

```toml
apscheduler = "^3.10.4"
```

如果项目使用 PEP 621 格式，也可以写为：

```toml
"apscheduler>=3.10.4,<4.0.0"
```

环境变量：

```env
SCHEDULER_ENABLED=true
SLA_CHECK_INTERVAL_MINUTES=5
```

要求：

```text
1. SCHEDULER_ENABLED=false 时，FastAPI 启动但不启动 APScheduler；
2. SLA_CHECK_INTERVAL_MINUTES 必须大于 0；
3. 定时任务必须使用独立数据库 Session；
4. 不允许在 APScheduler job 中使用 Depends(get_db)；
5. job 异常必须捕获并记录日志，不能导致调度器停止。
```

---

## 20.9 操作日志要求

以下操作必须写入 sys_operation_log：

```text
用户登录
创建用户
修改用户
禁用用户
创建资产
修改资产
修改资产状态
创建工单
修改工单
派单
开始处理
完成工单
取消工单
修改维修记录
创建 FAQ
修改 FAQ
修改 FAQ 状态
删除 FAQ
创建角色
修改角色
修改角色状态
删除角色
查询角色
查询权限
分配角色权限
查询用户角色
分配用户角色
创建 SLA 规则
修改 SLA 规则
启用停用 SLA 规则
删除 SLA 规则
```

日志字段：

```text
user_id
module_name
operation_type
business_id
request_method
request_url
request_ip
operation_result
error_message
created_at
```

---

