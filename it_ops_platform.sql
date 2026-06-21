-- =========================================================
-- 企业内部 IT 报修与资产运维管理平台 - MySQL 初始化脚本
-- 适用版本：MySQL 8.0+
-- =========================================================

DROP DATABASE IF EXISTS it_ops_platform;
CREATE DATABASE it_ops_platform
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_general_ci;

USE it_ops_platform;

-- =========================================================
-- 1. 用户表
-- =========================================================

CREATE TABLE sys_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID，主键',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的登录密码',
    real_name VARCHAR(50) NOT NULL COMMENT '用户真实姓名',
    role VARCHAR(30) NOT NULL COMMENT '用户角色：admin管理员，it_staff运维人员，employee普通员工',
    department VARCHAR(100) DEFAULT NULL COMMENT '所属部门',
    phone VARCHAR(30) DEFAULT NULL COMMENT '联系电话',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱地址',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '账号状态：1启用，0禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

INSERT INTO sys_user
(id, username, password_hash, real_name, role, department, phone, email, status)
VALUES
(1, 'admin', 'pbkdf2_sha256$test_admin_password', '系统管理员', 'admin', '信息部', '13800000001', 'admin@example.com', 1),
(2, 'it_zhang', 'pbkdf2_sha256$test_it_password', '张工', 'it_staff', '信息部', '13800000002', 'zhang@example.com', 1),
(3, 'employee_li', 'pbkdf2_sha256$test_employee_password', '李明', 'employee', '财务部', '13800000003', 'liming@example.com', 1),
(4, 'employee_wang', 'pbkdf2_sha256$test_employee_password', '王芳', 'employee', '运营部', '13800000004', 'wangfang@example.com', 1);


-- =========================================================
-- 2. 资产分类表
-- =========================================================

CREATE TABLE it_asset_category (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '资产分类ID，主键',
    category_name VARCHAR(100) NOT NULL COMMENT '资产分类名称',
    category_code VARCHAR(50) NOT NULL UNIQUE COMMENT '资产分类编码',
    description VARCHAR(255) DEFAULT NULL COMMENT '分类说明',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='IT资产分类表';

INSERT INTO it_asset_category
(id, category_name, category_code, description, status)
VALUES
(1, '办公电脑', 'PC', '员工日常办公使用的台式机、笔记本电脑', 1),
(2, '打印设备', 'PRINTER', '企业内部使用的打印机、复印机、一体机', 1),
(3, '网络设备', 'NETWORK', '交换机、路由器、防火墙、无线AP等网络设备', 1);


-- =========================================================
-- 3. 资产表
-- =========================================================

CREATE TABLE it_asset (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '资产ID，主键',
    asset_no VARCHAR(50) NOT NULL UNIQUE COMMENT '资产编号，唯一标识一台资产',
    asset_name VARCHAR(100) NOT NULL COMMENT '资产名称',
    category_id BIGINT NOT NULL COMMENT '资产分类ID，关联it_asset_category表',
    brand VARCHAR(50) DEFAULT NULL COMMENT '品牌',
    model VARCHAR(100) DEFAULT NULL COMMENT '型号',
    serial_no VARCHAR(100) DEFAULT NULL COMMENT '设备序列号',
    user_id BIGINT DEFAULT NULL COMMENT '当前使用人ID，关联sys_user表',
    department VARCHAR(100) DEFAULT NULL COMMENT '所属部门',
    location VARCHAR(100) DEFAULT NULL COMMENT '存放位置',
    status VARCHAR(30) NOT NULL DEFAULT 'in_use' COMMENT '资产状态：in_use在用，idle闲置，repairing维修中，scrapped已报废',
    purchase_date DATE DEFAULT NULL COMMENT '采购日期',
    warranty_expire_date DATE DEFAULT NULL COMMENT '保修到期日期',
    remark TEXT DEFAULT NULL COMMENT '备注信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_asset_category FOREIGN KEY (category_id) REFERENCES it_asset_category(id),
    CONSTRAINT fk_asset_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='IT资产台账表';

INSERT INTO it_asset
(id, asset_no, asset_name, category_id, brand, model, serial_no, user_id, department, location, status, purchase_date, warranty_expire_date, remark)
VALUES
(1, 'IT-PC-2026-0001', '财务部办公电脑', 1, 'Dell', 'OptiPlex 7090', 'SN-PC-0001', 3, '财务部', '财务办公室A区', 'in_use', '2024-05-10', '2027-05-10', '财务部日常办公电脑'),
(2, 'IT-PRINTER-2026-0001', '运营部打印机', 2, 'HP', 'LaserJet Pro MFP', 'SN-PR-0001', 4, '运营部', '运营办公室B区', 'repairing', '2023-09-15', '2026-09-15', '近期出现卡纸问题'),
(3, 'IT-NET-2026-0001', '核心交换机', 3, 'H3C', 'S5120V3', 'SN-NET-0001', 2, '信息部', '机房机柜01', 'in_use', '2022-03-20', '2027-03-20', '核心网络设备');


-- =========================================================
-- 4. 报修工单表
-- =========================================================

CREATE TABLE it_ticket (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '工单ID，主键',
    ticket_no VARCHAR(50) NOT NULL UNIQUE COMMENT '工单编号，系统自动生成',
    title VARCHAR(100) NOT NULL COMMENT '工单标题',
    description TEXT NOT NULL COMMENT '故障描述',
    fault_type VARCHAR(50) DEFAULT NULL COMMENT '故障类型：hardware硬件，software软件，network网络，printer打印机，other其他',
    priority VARCHAR(20) NOT NULL DEFAULT 'normal' COMMENT '优先级：low低，normal普通，high高，urgent紧急',
    status VARCHAR(30) NOT NULL DEFAULT 'pending' COMMENT '工单状态：pending待受理，assigned已派单，processing处理中，completed已完成，cancelled已取消',
    reporter_id BIGINT NOT NULL COMMENT '报修人ID，关联sys_user表',
    handler_id BIGINT DEFAULT NULL COMMENT '处理人ID，关联sys_user表',
    asset_id BIGINT DEFAULT NULL COMMENT '关联资产ID，关联it_asset表',
    result TEXT DEFAULT NULL COMMENT '处理结果说明',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    assigned_at DATETIME DEFAULT NULL COMMENT '派单时间',
    started_at DATETIME DEFAULT NULL COMMENT '开始处理时间',
    completed_at DATETIME DEFAULT NULL COMMENT '完成时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_ticket_reporter FOREIGN KEY (reporter_id) REFERENCES sys_user(id),
    CONSTRAINT fk_ticket_handler FOREIGN KEY (handler_id) REFERENCES sys_user(id),
    CONSTRAINT fk_ticket_asset FOREIGN KEY (asset_id) REFERENCES it_asset(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='IT报修工单表';

INSERT INTO it_ticket
(id, ticket_no, title, description, fault_type, priority, status, reporter_id, handler_id, asset_id, result, created_at, assigned_at, started_at, completed_at)
VALUES
(1, 'TK202606210001', '财务电脑无法开机', '按下电源键后电脑无反应，显示器无信号。', 'hardware', 'high', 'completed', 3, 2, 1, '重新插拔内存并清理主板灰尘后恢复正常。', '2026-06-21 09:10:00', '2026-06-21 09:20:00', '2026-06-21 09:30:00', '2026-06-21 10:10:00'),
(2, 'TK202606210002', '运营部打印机卡纸', '打印合同时频繁卡纸，影响正常办公。', 'printer', 'normal', 'completed', 4, 2, 2, '清理纸道并更换搓纸轮后恢复正常。', '2026-06-21 10:00:00', '2026-06-21 10:15:00', '2026-06-21 10:30:00', '2026-06-21 11:00:00'),
(3, 'TK202606210003', '部分电脑访问内网系统较慢', '多个用户反馈访问ERP系统时页面加载缓慢。', 'network', 'urgent', 'completed', 3, 2, 3, '排查发现交换机端口异常，调整端口并重启相关网络设备后恢复。', '2026-06-21 11:20:00', '2026-06-21 11:25:00', '2026-06-21 11:30:00', '2026-06-21 12:10:00'),
(4, 'TK202606210004', '办公软件无法正常启动', '打开Excel后提示组件加载失败。', 'software', 'normal', 'pending', 4, NULL, 1, NULL, '2026-06-21 14:00:00', NULL, NULL, NULL);


-- =========================================================
-- 5. 工单流转记录表
-- =========================================================

CREATE TABLE it_ticket_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '工单流转记录ID，主键',
    ticket_id BIGINT NOT NULL COMMENT '工单ID，关联it_ticket表',
    operator_id BIGINT NOT NULL COMMENT '操作人ID，关联sys_user表',
    from_status VARCHAR(30) DEFAULT NULL COMMENT '变更前状态',
    to_status VARCHAR(30) NOT NULL COMMENT '变更后状态',
    action VARCHAR(50) NOT NULL COMMENT '操作动作：create创建，assign派单，start开始处理，finish完成，cancel取消',
    remark TEXT DEFAULT NULL COMMENT '操作备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    CONSTRAINT fk_record_ticket FOREIGN KEY (ticket_id) REFERENCES it_ticket(id),
    CONSTRAINT fk_record_operator FOREIGN KEY (operator_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单状态流转记录表';

INSERT INTO it_ticket_record
(id, ticket_id, operator_id, from_status, to_status, action, remark, created_at)
VALUES
(1, 1, 3, NULL, 'pending', 'create', '用户提交电脑无法开机工单', '2026-06-21 09:10:00'),
(2, 1, 1, 'pending', 'assigned', 'assign', '管理员将工单派给张工处理', '2026-06-21 09:20:00'),
(3, 1, 2, 'assigned', 'processing', 'start', '张工开始处理该工单', '2026-06-21 09:30:00'),
(4, 1, 2, 'processing', 'completed', 'finish', '电脑已恢复正常', '2026-06-21 10:10:00'),
(5, 2, 4, NULL, 'pending', 'create', '用户提交打印机卡纸工单', '2026-06-21 10:00:00'),
(6, 2, 2, 'processing', 'completed', 'finish', '打印机维修完成', '2026-06-21 11:00:00'),
(7, 3, 3, NULL, 'pending', 'create', '用户提交网络访问慢工单', '2026-06-21 11:20:00'),
(8, 3, 2, 'processing', 'completed', 'finish', '网络故障处理完成', '2026-06-21 12:10:00');


-- =========================================================
-- 6. 维修记录表
-- =========================================================

CREATE TABLE it_repair_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '维修记录ID，主键',
    ticket_id BIGINT NOT NULL COMMENT '关联工单ID，关联it_ticket表',
    asset_id BIGINT NOT NULL COMMENT '关联资产ID，关联it_asset表',
    repair_user_id BIGINT NOT NULL COMMENT '维修人员ID，关联sys_user表',
    fault_reason TEXT DEFAULT NULL COMMENT '故障原因',
    repair_method TEXT DEFAULT NULL COMMENT '维修处理方法',
    repair_result VARCHAR(50) NOT NULL COMMENT '维修结果：fixed已修复，replace_repair更换配件，scrapped建议报废，unresolved未解决',
    repair_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '维修费用',
    repaired_at DATETIME NOT NULL COMMENT '维修完成时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    CONSTRAINT fk_repair_ticket FOREIGN KEY (ticket_id) REFERENCES it_ticket(id),
    CONSTRAINT fk_repair_asset FOREIGN KEY (asset_id) REFERENCES it_asset(id),
    CONSTRAINT fk_repair_user FOREIGN KEY (repair_user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产维修记录表';

INSERT INTO it_repair_record
(id, ticket_id, asset_id, repair_user_id, fault_reason, repair_method, repair_result, repair_cost, repaired_at)
VALUES
(1, 1, 1, 2, '内存接触不良，主机内部灰尘较多', '重新插拔内存条并清理机箱灰尘', 'fixed', 0.00, '2026-06-21 10:10:00'),
(2, 2, 2, 2, '打印机搓纸轮老化，导致进纸异常', '清理纸道并更换搓纸轮', 'replace_repair', 80.00, '2026-06-21 11:00:00'),
(3, 3, 3, 2, '交换机部分端口异常，导致内网访问不稳定', '调整交换机端口并重启网络设备', 'fixed', 0.00, '2026-06-21 12:10:00');


-- =========================================================
-- 7. 操作日志表
-- =========================================================

CREATE TABLE sys_operation_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '操作日志ID，主键',
    user_id BIGINT DEFAULT NULL COMMENT '操作用户ID，关联sys_user表',
    module_name VARCHAR(100) NOT NULL COMMENT '操作模块名称',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型：create新增，update修改，delete删除，query查询，login登录',
    business_id BIGINT DEFAULT NULL COMMENT '业务数据ID，例如工单ID或资产ID',
    request_method VARCHAR(10) DEFAULT NULL COMMENT 'HTTP请求方法，例如GET、POST、PUT、DELETE',
    request_url VARCHAR(255) DEFAULT NULL COMMENT '请求地址',
    request_ip VARCHAR(50) DEFAULT NULL COMMENT '客户端IP地址',
    operation_result VARCHAR(20) NOT NULL DEFAULT 'success' COMMENT '操作结果：success成功，fail失败',
    error_message TEXT DEFAULT NULL COMMENT '错误信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    CONSTRAINT fk_log_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表';

INSERT INTO sys_operation_log
(id, user_id, module_name, operation_type, business_id, request_method, request_url, request_ip, operation_result, error_message, created_at)
VALUES
(1, 1, '用户登录', 'login', NULL, 'POST', '/api/auth/login', '192.168.1.10', 'success', NULL, '2026-06-21 08:50:00'),
(2, 3, '报修工单', 'create', 1, 'POST', '/api/tickets', '192.168.1.21', 'success', NULL, '2026-06-21 09:10:00'),
(3, 2, '报修工单', 'update', 1, 'PUT', '/api/tickets/1/finish', '192.168.1.30', 'success', NULL, '2026-06-21 10:10:00'),
(4, 4, '报修工单', 'create', 2, 'POST', '/api/tickets', '192.168.1.22', 'success', NULL, '2026-06-21 10:00:00');


-- =========================================================
-- 8. 常用查询测试
-- =========================================================

-- 查询工单列表
SELECT
    t.id,
    t.ticket_no,
    t.title,
    t.priority,
    t.status,
    reporter.real_name AS reporter_name,
    handler.real_name AS handler_name,
    a.asset_name,
    t.created_at
FROM it_ticket t
LEFT JOIN sys_user reporter ON t.reporter_id = reporter.id
LEFT JOIN sys_user handler ON t.handler_id = handler.id
LEFT JOIN it_asset a ON t.asset_id = a.id
ORDER BY t.created_at DESC;

-- 查询资产列表
SELECT
    a.id,
    a.asset_no,
    a.asset_name,
    c.category_name,
    a.brand,
    a.model,
    u.real_name AS user_name,
    a.department,
    a.status
FROM it_asset a
LEFT JOIN it_asset_category c ON a.category_id = c.id
LEFT JOIN sys_user u ON a.user_id = u.id
ORDER BY a.id ASC;

-- 查询某个资产的维修历史
SELECT
    r.id,
    a.asset_name,
    t.ticket_no,
    t.title,
    u.real_name AS repair_user,
    r.fault_reason,
    r.repair_method,
    r.repair_result,
    r.repair_cost,
    r.repaired_at
FROM it_repair_record r
LEFT JOIN it_asset a ON r.asset_id = a.id
LEFT JOIN it_ticket t ON r.ticket_id = t.id
LEFT JOIN sys_user u ON r.repair_user_id = u.id
WHERE r.asset_id = 1
ORDER BY r.repaired_at DESC;