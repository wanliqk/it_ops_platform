# 移动端 API 接口文档

## 基础信息

- Base URL: `/api/mobile`
- Content-Type: `application/json`
- 认证方式: JWT Bearer Token
- 除登录接口外，其他接口都需要请求头：

```http
Authorization: Bearer <access_token>
```

## 统一响应格式

成功：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 400,
  "message": "错误原因",
  "data": null
}
```

常见 HTTP 状态：

- `400`: 业务参数错误，例如工单状态不允许取消
- `401`: 未登录、Token 缺失、Token 无效或已过期
- `403`: 无权访问当前资源
- `404`: 资源不存在
- `422`: FastAPI 参数校验失败

## 枚举值

工单状态 `status`:

| 值 | 说明 |
| --- | --- |
| `pending` | 待处理 |
| `assigned` | 已分派 |
| `processing` | 处理中 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |

工单分类 `category_id`:

工单分类由后端动态维护，移动端通过 `GET /api/mobile/tickets/form-options` 获取可选分类。

优先级 `priority`:

| 值 | 说明 |
| --- | --- |
| `low` | 低 |
| `normal` | 普通 |
| `high` | 高 |
| `urgent` | 紧急 |

FAQ 分类 `category`:

| 值 | 说明 |
| --- | --- |
| `computer` | 电脑问题 |
| `network` | 网络问题 |
| `printer` | 打印机问题 |
| `account` | 账号系统 |
| `other` | 其他问题 |

## 1. 员工登录

### POST `/api/mobile/auth/login`

说明：员工登录，成功后返回 JWT Token。此接口不需要 Token。

请求体：

```json
{
  "username": "employee_li",
  "password": "123456"
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "jwt token",
    "token_type": "bearer",
    "user": {
      "id": 3,
      "username": "employee_li",
      "real_name": "李明",
      "role": "employee",
      "department": "财务部",
      "phone": "13800000003"
    }
  }
}
```

可能错误：

- `用户名或密码错误`
- `账号已禁用`

### GET `/api/mobile/auth/me`

说明：获取当前登录用户信息。

请求头：

```http
Authorization: Bearer <access_token>
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 3,
    "username": "employee_li",
    "real_name": "李明",
    "role": "employee",
    "department": "财务部",
    "phone": "13800000003"
  }
}
```

## 2. 报修首页

### GET `/api/mobile/home/summary`

说明：获取当前登录用户自己的报修统计。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_count": 12,
    "pending_count": 2,
    "assigned_count": 1,
    "processing_count": 3,
    "completed_count": 6,
    "cancelled_count": 0
  }
}
```

### GET `/api/mobile/tickets/recent`

说明：获取当前用户最近报修记录，按创建时间倒序。

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `limit` | number | 否 | `5` | 返回条数，范围 `1-100` |

示例：

```http
GET /api/mobile/tickets/recent?limit=5
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "ticket_no": "TK202606220001",
      "title": "电脑无法开机",
      "status": "pending",
      "created_at": "2026-06-22T10:30:00",
      "category_id": 1,
      "priority": "high",
      "asset_id": 1
    }
  ]
}
```

## 3. 发起报修

### GET `/api/mobile/tickets/form-options`

说明：获取工单分类和优先级选项。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "categories": [
      { "value": "1", "label": "电脑故障" },
      { "value": "2", "label": "网络故障" },
      { "value": "3", "label": "打印机故障" }
    ],
    "priorities": [
      { "value": "low", "label": "低" },
      { "value": "normal", "label": "普通" },
      { "value": "high", "label": "高" },
      { "value": "urgent", "label": "紧急" }
    ]
  }
}
```

### GET `/api/mobile/assets/options`

说明：获取当前用户可选择的资产列表。只返回当前用户资产，并排除已报废资产。

Query 参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `keyword` | string | 否 | 根据资产编号、资产名称、品牌、型号模糊搜索 |

示例：

```http
GET /api/mobile/assets/options?keyword=电脑
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "asset_no": "PC20260001",
      "asset_name": "办公电脑",
      "brand": "Lenovo",
      "model": "ThinkCentre",
      "status": "in_use",
      "location": "财务部办公室"
    }
  ]
}
```

### POST `/api/mobile/tickets`

说明：创建报修工单。`reporter_id` 由后端根据当前登录用户确定，前端不要传。

请求体：

```json
{
  "title": "电脑无法开机",
  "description": "按下电源键后主机没有反应，显示器无信号。",
  "category_id": 1,
  "priority": "high",
  "asset_id": 1
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `title` | string | 是 | 工单标题，最大 100 字符 |
| `description` | string | 是 | 故障描述 |
| `category_id` | number | 是 | 工单分类 ID |
| `priority` | string | 否 | 优先级，默认 `normal` |
| `asset_id` | number/null | 否 | 关联资产 ID，可为空 |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "ticket_no": "TK202606220001",
    "title": "电脑无法开机",
    "status": "pending",
    "created_at": "2026-06-22T10:30:00"
  }
}
```

可能错误：

- `资产不存在或已报废`

## 4. 我的报修

### GET `/api/mobile/tickets`

说明：分页查询当前用户自己的报修列表，按创建时间倒序。

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `page` | number | 否 | `1` | 页码，最小 `1` |
| `page_size` | number | 否 | `10` | 每页条数，范围 `1-100` |
| `status` | string | 否 | - | 工单状态 |
| `keyword` | string | 否 | - | 根据工单编号、标题模糊搜索 |

示例：

```http
GET /api/mobile/tickets?page=1&page_size=10&status=pending&keyword=电脑
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "ticket_no": "TK202606220001",
        "title": "电脑无法开机",
        "status": "pending",
        "created_at": "2026-06-22T10:30:00",
        "category_id": 1,
        "priority": "high",
        "asset_id": 1
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

## 5. 报修详情

### GET `/api/mobile/tickets/{ticket_id}`

说明：查询报修详情。普通员工只能查看自己提交的工单。

Path 参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `ticket_id` | number | 工单 ID |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "ticket_no": "TK202606220001",
    "title": "电脑无法开机",
    "description": "按下电源键后主机没有反应，显示器无信号。",
    "category_id": 1,
    "priority": "high",
    "status": "pending",
    "result": null,
    "reporter": {
      "id": 3,
      "username": "employee_li",
      "real_name": "李明",
      "department": "财务部",
      "phone": "13800000003"
    },
    "handler": null,
    "asset": {
      "id": 1,
      "asset_no": "PC20260001",
      "asset_name": "办公电脑",
      "brand": "Lenovo",
      "model": "ThinkCentre",
      "serial_no": "SN001",
      "location": "财务部办公室",
      "status": "in_use"
    },
    "repair_records": [],
    "records": [
      {
        "id": 1,
        "action": "create",
        "from_status": null,
        "to_status": "pending",
        "remark": "用户提交报修工单",
        "operator": {
          "id": 3,
          "username": "employee_li",
          "real_name": "李明",
          "department": "财务部",
          "phone": "13800000003"
        },
        "created_at": "2026-06-22T10:30:00"
      }
    ],
    "created_at": "2026-06-22T10:30:00",
    "assigned_at": null,
    "started_at": null,
    "completed_at": null,
    "updated_at": "2026-06-22T10:30:00"
  }
}
```

可能错误：

- `工单不存在`
- `无权查看该工单`

### POST `/api/mobile/tickets/{ticket_id}/cancel`

说明：取消报修。只有报修人本人可以取消，且只有 `pending` 状态可以取消。

请求体：

```json
{
  "reason": "问题已经自行解决"
}
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "ticket_no": "TK202606220001",
    "status": "cancelled"
  }
}
```

可能错误：

- `工单不存在`
- `无权取消该工单`
- `只有待处理状态的工单可以取消`

## 6. 常见问题

### GET `/api/mobile/faqs/categories`

说明：获取 FAQ 分类。

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    { "value": "computer", "label": "电脑问题" },
    { "value": "network", "label": "网络问题" },
    { "value": "printer", "label": "打印机问题" },
    { "value": "account", "label": "账号系统" },
    { "value": "other", "label": "其他问题" }
  ]
}
```

### GET `/api/mobile/faqs`

说明：分页查询启用状态的 FAQ。排序规则：`sort_order ASC, created_at DESC`。

Query 参数：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `category` | string | 否 | - | FAQ 分类 |
| `keyword` | string | 否 | - | 根据标题、摘要模糊搜索 |
| `page` | number | 否 | `1` | 页码，最小 `1` |
| `page_size` | number | 否 | `10` | 每页条数，范围 `1-100` |

示例：

```http
GET /api/mobile/faqs?category=network&keyword=无法上网&page=1&page_size=10
```

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "无法上网怎么办？",
        "category": "network",
        "summary": "网络无法连接时的基础排查步骤",
        "view_count": 10,
        "created_at": "2026-06-22T10:30:00",
        "updated_at": "2026-06-22T10:30:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

### GET `/api/mobile/faqs/{faq_id}`

说明：查看 FAQ 详情。只允许查看 `status = 1` 的 FAQ，每次查看详情会让 `view_count + 1`。

Path 参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `faq_id` | number | FAQ ID |

响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "无法上网怎么办？",
    "category": "network",
    "summary": "网络无法连接时的基础排查步骤",
    "content": "请先检查网线、Wi-Fi、IP 配置和公司网络通知。",
    "view_count": 11,
    "created_at": "2026-06-22T10:30:00",
    "updated_at": "2026-06-22T10:30:00"
  }
}
```

可能错误：

- `FAQ不存在或已停用`

## 前端调用建议

登录成功后保存 `data.access_token`，后续请求统一带上：

```ts
headers: {
  Authorization: `Bearer ${token}`
}
```

前端可统一判断：

```ts
if (response.code !== 200) {
  throw new Error(response.message)
}
```

遇到 HTTP `401` 时建议清理本地 Token 并跳转登录页。
