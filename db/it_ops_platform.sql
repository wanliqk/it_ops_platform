/*
 Navicat Premium Data Transfer

 Source Server         : local57
 Source Server Type    : MySQL
 Source Server Version : 50744 (5.7.44)
 Source Host           : 127.0.0.1:3306
 Source Schema         : it_ops_platform

 Target Server Type    : MySQL
 Target Server Version : 50744 (5.7.44)
 File Encoding         : 65001

 Date: 23/06/2026 17:25:28
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for it_asset
-- ----------------------------
DROP TABLE IF EXISTS `it_asset`;
CREATE TABLE `it_asset`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '资产ID，主键',
  `asset_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '资产编号，唯一标识一台资产',
  `asset_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '资产名称',
  `category_id` bigint(20) NOT NULL COMMENT '资产分类ID，关联it_asset_category表',
  `brand` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '品牌',
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '型号',
  `serial_no` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '设备序列号',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '当前使用人ID，关联sys_user表',
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属部门',
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '存放位置',
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'in_use' COMMENT '资产状态：in_use在用，idle闲置，repairing维修中，scrapped已报废',
  `purchase_date` date NULL DEFAULT NULL COMMENT '采购日期',
  `warranty_expire_date` date NULL DEFAULT NULL COMMENT '保修到期日期',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注信息',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `asset_no`(`asset_no`) USING BTREE,
  INDEX `fk_asset_category`(`category_id`) USING BTREE,
  INDEX `fk_asset_user`(`user_id`) USING BTREE,
  CONSTRAINT `fk_asset_category` FOREIGN KEY (`category_id`) REFERENCES `it_asset_category` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_asset_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'IT资产台账表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_asset
-- ----------------------------
INSERT INTO `it_asset` VALUES (1, 'IT-PC-2026-0001', '财务部办公电脑', 1, 'Dell', 'OptiPlex 7090', 'SN-PC-0001', 3, '财务部', '财务办公室A区', 'in_use', '2024-05-10', '2027-05-10', '财务部日常办公电脑', '2026-06-22 19:39:11', '2026-06-22 19:39:11');
INSERT INTO `it_asset` VALUES (2, 'IT-PRINTER-2026-0001', '运营部打印机', 2, 'HP', 'LaserJet Pro MFP', 'SN-PR-0001', 4, '运营部', '运营办公室B区', 'repairing', '2023-09-15', '2026-09-15', '近期出现卡纸问题', '2026-06-22 19:39:11', '2026-06-22 19:39:11');
INSERT INTO `it_asset` VALUES (3, 'IT-NET-2026-0001', '核心交换机', 3, 'H3C', 'S5120V3', 'SN-NET-0001', 2, '信息部', '机房机柜01', 'in_use', '2022-03-20', '2027-03-20', '核心网络设备', '2026-06-22 19:39:11', '2026-06-22 19:39:11');

-- ----------------------------
-- Table structure for it_asset_category
-- ----------------------------
DROP TABLE IF EXISTS `it_asset_category`;
CREATE TABLE `it_asset_category`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '资产分类ID，主键',
  `category_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '资产分类名称',
  `category_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '资产分类编码',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '分类说明',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `category_code`(`category_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'IT资产分类表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_asset_category
-- ----------------------------
INSERT INTO `it_asset_category` VALUES (1, '办公电脑', 'PC', '员工日常办公使用的台式机、笔记本电脑', 1, '2026-06-22 19:39:11', '2026-06-22 19:39:11');
INSERT INTO `it_asset_category` VALUES (2, '打印设备', 'PRINTER', '企业内部使用的打印机、复印机、一体机', 1, '2026-06-22 19:39:11', '2026-06-22 19:39:11');
INSERT INTO `it_asset_category` VALUES (3, '网络设备', 'NETWORK', '交换机、路由器、防火墙、无线AP等网络设备', 1, '2026-06-22 19:39:11', '2026-06-22 19:39:11');

-- ----------------------------
-- Table structure for it_faq
-- ----------------------------
DROP TABLE IF EXISTS `it_faq`;
CREATE TABLE `it_faq`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '常见问题ID，主键',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '问题标题',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '问题分类：computer电脑，network网络，printer打印机，account账号系统，other其他',
  `summary` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '问题摘要',
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '问题详细内容',
  `view_count` int(11) NOT NULL DEFAULT 0 COMMENT '浏览次数',
  `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序值，越小越靠前',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '常见问题表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_faq
-- ----------------------------
INSERT INTO `it_faq` VALUES (1, '电脑无法开机应该如何处理？', 'computer', '电脑无法开机时的基础排查步骤', '1. 检查电源线是否插紧；2. 检查插座是否有电；3. 长按电源键 10 秒后重新开机；4. 检查显示器是否正常；5. 如果仍无法解决，请提交 IT 报修工单。', 15, 1, 1, '2026-06-23 10:29:16', '2026-06-23 10:29:16');
INSERT INTO `it_faq` VALUES (2, '打印机卡纸应该如何处理？', 'printer', '打印机卡纸时的基础处理步骤', '1. 先取消当前打印任务；2. 打开打印机后盖；3. 按照纸张出纸方向缓慢取出卡纸；4. 检查纸盒纸张是否受潮或变形；5. 如果仍无法恢复，请提交 IT 报修工单。', 28, 2, 1, '2026-06-23 10:29:16', '2026-06-23 10:29:16');
INSERT INTO `it_faq` VALUES (3, '无法访问内网系统怎么办？', 'network', '无法访问 ERP、OA 等内网系统时的处理方法', '1. 检查网线或 Wi-Fi 是否连接；2. 尝试访问其他网站判断是否为整体网络问题；3. 使用 ipconfig 查看是否获取到正确 IP；4. 重启浏览器后再次访问；5. 如果多个系统均无法访问，请联系 IT 运维人员。', 21, 3, 1, '2026-06-23 10:29:16', '2026-06-23 10:29:16');

-- ----------------------------
-- Table structure for it_notification
-- ----------------------------
DROP TABLE IF EXISTS `it_notification`;
CREATE TABLE `it_notification`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '通知ID',
  `user_id` bigint(20) NOT NULL COMMENT '接收用户ID',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '通知标题',
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '通知内容',
  `biz_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '业务类型：ticket工单，asset资产，sla SLA提醒，system系统',
  `biz_id` bigint(20) NULL DEFAULT NULL COMMENT '关联业务ID，例如工单ID、资产ID',
  `read_status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '阅读状态：0未读，1已读',
  `read_at` datetime NULL DEFAULT NULL COMMENT '阅读时间',
  `deleted` tinyint(4) NOT NULL DEFAULT 0 COMMENT '逻辑删除标识：0正常，1已删除',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_notification_user_status`(`user_id`, `read_status`, `deleted`) USING BTREE,
  INDEX `idx_notification_biz`(`biz_type`, `biz_id`) USING BTREE,
  CONSTRAINT `fk_notification_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '站内通知表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_notification
-- ----------------------------
INSERT INTO `it_notification` VALUES (1, 1, '系统欢迎通知', '欢迎使用企业内部 IT 报修与资产管理平台。', 'system', NULL, 0, NULL, 0, '2026-06-23 18:00:00', '2026-06-23 18:00:00');
INSERT INTO `it_notification` VALUES (2, 2, '新工单分派提醒', '工单 TK202606210001 已分派给你，请及时处理。', 'ticket', 1, 0, NULL, 0, '2026-06-23 18:05:00', '2026-06-23 18:05:00');
INSERT INTO `it_notification` VALUES (3, 3, '资产保修提醒', '你名下资产 IT-PC-2026-0001 即将到达保修截止日期。', 'asset', 1, 1, '2026-06-23 18:15:00', 0, '2026-06-23 18:10:00', '2026-06-23 18:15:00');
-- ----------------------------
-- Table structure for it_repair_record
-- ----------------------------
DROP TABLE IF EXISTS `it_repair_record`;
CREATE TABLE `it_repair_record`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '维修记录ID，主键',
  `ticket_id` bigint(20) NOT NULL COMMENT '关联工单ID，关联it_ticket表',
  `asset_id` bigint(20) NOT NULL COMMENT '关联资产ID，关联it_asset表',
  `repair_user_id` bigint(20) NOT NULL COMMENT '维修人员ID，关联sys_user表',
  `fault_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '故障原因',
  `repair_method` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '维修处理方法',
  `repair_result` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '维修结果：fixed已修复，replace_repair更换配件，scrapped建议报废，unresolved未解决',
  `repair_cost` decimal(10, 2) NOT NULL DEFAULT 0.00 COMMENT '维修费用',
  `repaired_at` datetime NOT NULL COMMENT '维修完成时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_repair_ticket`(`ticket_id`) USING BTREE,
  INDEX `fk_repair_asset`(`asset_id`) USING BTREE,
  INDEX `fk_repair_user`(`repair_user_id`) USING BTREE,
  CONSTRAINT `fk_repair_asset` FOREIGN KEY (`asset_id`) REFERENCES `it_asset` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_repair_ticket` FOREIGN KEY (`ticket_id`) REFERENCES `it_ticket` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_repair_user` FOREIGN KEY (`repair_user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '资产维修记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_repair_record
-- ----------------------------
INSERT INTO `it_repair_record` VALUES (1, 1, 1, 2, '内存接触不良，主机内部灰尘较多', '重新插拔内存条并清理机箱灰尘', 'fixed', 0.00, '2026-06-21 10:10:00', '2026-06-22 19:39:12');
INSERT INTO `it_repair_record` VALUES (2, 2, 2, 2, '打印机搓纸轮老化，导致进纸异常', '清理纸道并更换搓纸轮', 'replace_repair', 80.00, '2026-06-21 11:00:00', '2026-06-22 19:39:12');
INSERT INTO `it_repair_record` VALUES (3, 3, 3, 2, '交换机部分端口异常，导致内网访问不稳定', '调整交换机端口并重启网络设备', 'fixed', 0.00, '2026-06-21 12:10:00', '2026-06-22 19:39:12');

-- ----------------------------
-- Table structure for it_sla_rule
-- ----------------------------
DROP TABLE IF EXISTS `it_sla_rule`;
CREATE TABLE `it_sla_rule`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'SLA规则ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '规则名称',
  `ticket_category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '工单类型：hardware硬件，software软件，network网络，printer打印机，account账号系统，other其他；NULL表示通用规则',
  `priority` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '优先级：urgent紧急，high高，medium普通，low低',
  `response_minutes` int(11) NOT NULL COMMENT '响应时限，单位分钟',
  `resolve_minutes` int(11) NOT NULL COMMENT '处理完成时限，单位分钟',
  `enabled` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否启用：1启用，0停用',
  `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序值，越小越优先',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sla_rule_match`(`ticket_category`, `priority`, `enabled`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'SLA规则表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_sla_rule
-- ----------------------------
INSERT INTO `it_sla_rule` VALUES (1, '紧急工单通用SLA', NULL, 'urgent', 10, 120, 1, 10, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `it_sla_rule` VALUES (2, '高优先级通用SLA', NULL, 'high', 30, 240, 1, 20, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `it_sla_rule` VALUES (3, '普通优先级通用SLA', NULL, 'medium', 60, 480, 1, 30, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `it_sla_rule` VALUES (4, '低优先级通用SLA', NULL, 'low', 240, 2880, 1, 40, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `it_sla_rule` VALUES (5, '网络故障紧急SLA', 'network', 'urgent', 5, 60, 1, 1, '2026-06-24 00:00:00', '2026-06-24 00:00:00');

-- ----------------------------
-- Table structure for it_ticket
-- ----------------------------
DROP TABLE IF EXISTS `it_ticket`;
CREATE TABLE `it_ticket`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '工单ID，主键',
  `ticket_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '工单编号，系统自动生成',
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '工单标题',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '故障描述',
  `fault_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '故障类型：hardware硬件，software软件，network网络，printer打印机，other其他',
  `category_id` bigint(20) NULL DEFAULT NULL COMMENT '工单分类ID，用于自动分配规则匹配',
  `priority` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'normal' COMMENT '优先级：low低，normal普通，high高，urgent紧急',
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'pending_accept' COMMENT '工单状态：pending_accept待受理，assigned已分配，processing处理中，pending_confirm待确认，completed已完成，closed已关闭，cancelled已取消',
  `reporter_id` bigint(20) NOT NULL COMMENT '报修人ID，关联sys_user表',
  `handler_id` bigint(20) NULL DEFAULT NULL COMMENT '处理人ID，关联sys_user表',
  `asset_id` bigint(20) NULL DEFAULT NULL COMMENT '关联资产ID，关联it_asset表',
  `result` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '处理结果说明',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `assigner_id` bigint(20) NULL DEFAULT NULL COMMENT '分派人ID，自动分配时为空',
  `assign_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '分配来源：manual手动，auto自动，claim主动受理',
  `assigned_at` datetime NULL DEFAULT NULL COMMENT '分配时间',
  `accepted_at` datetime NULL DEFAULT NULL COMMENT '受理时间',
  `started_at` datetime NULL DEFAULT NULL COMMENT '开始处理时间',
  `completed_at` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `sla_response_deadline` datetime NULL DEFAULT NULL COMMENT 'SLA响应截止时间',
  `sla_resolve_deadline` datetime NULL DEFAULT NULL COMMENT 'SLA处理完成截止时间',
  `first_response_at` datetime NULL DEFAULT NULL COMMENT '首次响应时间',
  `resolved_at` datetime NULL DEFAULT NULL COMMENT '解决完成时间',
  `response_overdue` tinyint(4) NOT NULL DEFAULT 0 COMMENT '是否响应超时：0否，1是',
  `resolve_overdue` tinyint(4) NOT NULL DEFAULT 0 COMMENT '是否处理超时：0否，1是',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ticket_no`(`ticket_no`) USING BTREE,
  INDEX `fk_ticket_reporter`(`reporter_id`) USING BTREE,
  INDEX `fk_ticket_handler`(`handler_id`) USING BTREE,
  INDEX `idx_ticket_status`(`status`) USING BTREE,
  INDEX `idx_ticket_category`(`category_id`) USING BTREE,
  INDEX `idx_ticket_priority`(`priority`) USING BTREE,
  INDEX `idx_ticket_assigned_at`(`assigned_at`) USING BTREE,
  INDEX `fk_ticket_assigner`(`assigner_id`) USING BTREE,
  INDEX `fk_ticket_asset`(`asset_id`) USING BTREE,
  CONSTRAINT `fk_ticket_asset` FOREIGN KEY (`asset_id`) REFERENCES `it_asset` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_ticket_assigner` FOREIGN KEY (`assigner_id`) REFERENCES `sys_user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_ticket_handler` FOREIGN KEY (`handler_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_ticket_reporter` FOREIGN KEY (`reporter_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'IT报修工单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_ticket
-- ----------------------------
INSERT INTO `it_ticket` VALUES (1, 'TK202606210001', '财务电脑无法开机', '按下电源键后电脑无反应，显示器无信号。', 'hardware', 1, 'high', 'completed', 3, 2, 1, '重新插拔内存并清理主板灰尘后恢复正常。', '2026-06-21 09:10:00', 1, 'manual', '2026-06-21 09:20:00', '2026-06-21 09:20:00', '2026-06-21 09:30:00', '2026-06-21 10:10:00', '2026-06-21 09:40:00', '2026-06-21 13:10:00', '2026-06-21 09:20:00', '2026-06-21 10:10:00', 0, 0, '2026-06-22 19:39:11');
INSERT INTO `it_ticket` VALUES (2, 'TK202606210002', '运营部打印机卡纸', '打印合同时频繁卡纸，影响正常办公。', 'printer', 3, 'normal', 'completed', 4, 2, 2, '清理纸道并更换搓纸轮后恢复正常。', '2026-06-21 10:00:00', 1, 'manual', '2026-06-21 10:15:00', '2026-06-21 10:15:00', '2026-06-21 10:30:00', '2026-06-21 11:00:00', '2026-06-21 11:00:00', '2026-06-21 18:00:00', '2026-06-21 10:15:00', '2026-06-21 11:00:00', 0, 0, '2026-06-22 19:39:11');
INSERT INTO `it_ticket` VALUES (3, 'TK202606210003', '部分电脑访问内网系统较慢', '多个用户反馈访问ERP系统时页面加载缓慢。', 'network', 2, 'urgent', 'completed', 3, 2, 3, '排查发现交换机端口异常，调整端口并重启相关网络设备后恢复。', '2026-06-21 11:20:00', 1, 'manual', '2026-06-21 11:25:00', '2026-06-21 11:25:00', '2026-06-21 11:30:00', '2026-06-21 12:10:00', '2026-06-21 11:25:00', '2026-06-21 12:20:00', '2026-06-21 11:25:00', '2026-06-21 12:10:00', 0, 0, '2026-06-22 19:39:11');
INSERT INTO `it_ticket` VALUES (4, 'TK202606210004', '办公软件无法正常启动', '打开Excel后提示组件加载失败。', 'software', NULL, 'normal', 'pending_accept', 4, NULL, 1, NULL, '2026-06-21 14:00:00', NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-21 15:00:00', '2026-06-21 22:00:00', NULL, NULL, 0, 0, '2026-06-22 19:39:11');
INSERT INTO `it_ticket` VALUES (5, 'TK202606230001', '电脑无法开机', '就是电脑无法开机', 'hardware', 1, 'normal', 'cancelled', 1, NULL, NULL, NULL, '2026-06-23 00:29:35', NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-23 01:29:35', '2026-06-23 08:29:35', NULL, NULL, 0, 0, '2026-06-23 00:52:15');
INSERT INTO `it_ticket` VALUES (6, 'TK202606230002', '打印机无法打印', '打印机无法打印', 'hardware', 1, 'normal', 'pending_accept', 2, NULL, NULL, NULL, '2026-06-23 01:42:31', NULL, NULL, NULL, NULL, NULL, NULL, '2026-06-23 02:42:31', '2026-06-23 09:42:31', NULL, NULL, 0, 0, '2026-06-23 01:42:31');

-- ----------------------------
-- Table structure for it_ticket_record
-- ----------------------------
DROP TABLE IF EXISTS `it_ticket_record`;
CREATE TABLE `it_ticket_record`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '工单流转记录ID，主键',
  `ticket_id` bigint(20) NOT NULL COMMENT '工单ID，关联it_ticket表',
  `operator_id` bigint(20) NOT NULL COMMENT '操作人ID，关联sys_user表',
  `from_status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '变更前状态',
  `to_status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '变更后状态',
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作动作：create创建，assign派单，start开始处理，finish完成，cancel取消',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '操作备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_record_ticket`(`ticket_id`) USING BTREE,
  INDEX `fk_record_operator`(`operator_id`) USING BTREE,
  CONSTRAINT `fk_record_operator` FOREIGN KEY (`operator_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_record_ticket` FOREIGN KEY (`ticket_id`) REFERENCES `it_ticket` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '工单状态流转记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_ticket_record
-- ----------------------------
INSERT INTO `it_ticket_record` VALUES (1, 1, 3, NULL, 'pending', 'create', '用户提交电脑无法开机工单', '2026-06-21 09:10:00');
INSERT INTO `it_ticket_record` VALUES (2, 1, 1, 'pending', 'assigned', 'assign', '管理员将工单派给张工处理', '2026-06-21 09:20:00');
INSERT INTO `it_ticket_record` VALUES (3, 1, 2, 'assigned', 'processing', 'start', '张工开始处理该工单', '2026-06-21 09:30:00');
INSERT INTO `it_ticket_record` VALUES (4, 1, 2, 'processing', 'completed', 'finish', '电脑已恢复正常', '2026-06-21 10:10:00');
INSERT INTO `it_ticket_record` VALUES (5, 2, 4, NULL, 'pending', 'create', '用户提交打印机卡纸工单', '2026-06-21 10:00:00');
INSERT INTO `it_ticket_record` VALUES (6, 2, 2, 'processing', 'completed', 'finish', '打印机维修完成', '2026-06-21 11:00:00');
INSERT INTO `it_ticket_record` VALUES (7, 3, 3, NULL, 'pending', 'create', '用户提交网络访问慢工单', '2026-06-21 11:20:00');
INSERT INTO `it_ticket_record` VALUES (8, 3, 2, 'processing', 'completed', 'finish', '网络故障处理完成', '2026-06-21 12:10:00');
INSERT INTO `it_ticket_record` VALUES (9, 5, 1, NULL, 'pending', 'create', '用户提交报修工单', '2026-06-23 00:29:35');
INSERT INTO `it_ticket_record` VALUES (10, 5, 1, 'pending', 'cancelled', 'cancel', '自己解决了', '2026-06-23 00:52:15');
INSERT INTO `it_ticket_record` VALUES (11, 6, 2, NULL, 'pending', 'create', '用户提交报修工单', '2026-06-23 01:42:31');

-- ----------------------------
-- Table structure for sys_operation_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_operation_log`;
CREATE TABLE `sys_operation_log`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '操作日志ID，主键',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '操作用户ID，关联sys_user表',
  `module_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作模块名称',
  `operation_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '操作类型：create新增，update修改，delete删除，query查询，login登录',
  `business_id` bigint(20) NULL DEFAULT NULL COMMENT '业务数据ID，例如工单ID或资产ID',
  `request_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'HTTP请求方法，例如GET、POST、PUT、DELETE',
  `request_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '请求地址',
  `request_ip` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '客户端IP地址',
  `operation_result` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'success' COMMENT '操作结果：success成功，fail失败',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '错误信息',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_log_user`(`user_id`) USING BTREE,
  CONSTRAINT `fk_log_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统操作日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_operation_log
-- ----------------------------
INSERT INTO `sys_operation_log` VALUES (1, 1, '用户登录', 'login', NULL, 'POST', '/api/auth/login', '192.168.1.10', 'success', NULL, '2026-06-21 08:50:00');
INSERT INTO `sys_operation_log` VALUES (2, 3, '报修工单', 'create', 1, 'POST', '/api/tickets', '192.168.1.21', 'success', NULL, '2026-06-21 09:10:00');
INSERT INTO `sys_operation_log` VALUES (3, 2, '报修工单', 'update', 1, 'PUT', '/api/tickets/1/finish', '192.168.1.30', 'success', NULL, '2026-06-21 10:10:00');
INSERT INTO `sys_operation_log` VALUES (4, 4, '报修工单', 'create', 2, 'POST', '/api/tickets', '192.168.1.22', 'success', NULL, '2026-06-21 10:00:00');
INSERT INTO `sys_operation_log` VALUES (5, 1, '用户登录', 'login', NULL, 'POST', '/api/v1/auth/login', '127.0.0.1', 'success', NULL, '2026-06-23 11:06:36');
INSERT INTO `sys_operation_log` VALUES (6, 1, '用户登录', 'login', NULL, 'POST', '/api/v1/auth/login', '127.0.0.1', 'success', NULL, '2026-06-23 12:43:40');
INSERT INTO `sys_operation_log` VALUES (7, 1, '用户登录', 'login', NULL, 'POST', '/api/v1/auth/login', '127.0.0.1', 'success', NULL, '2026-06-23 13:10:32');
INSERT INTO `sys_operation_log` VALUES (8, 1, '用户登录', 'login', NULL, 'POST', '/api/v1/auth/login', '127.0.0.1', 'success', NULL, '2026-06-23 13:13:38');
INSERT INTO `sys_operation_log` VALUES (9, 1, '用户登录', 'login', NULL, 'POST', '/api/v1/auth/login', '127.0.0.1', 'success', NULL, '2026-06-23 14:44:55');

-- ----------------------------
-- Table structure for sys_permission
-- ----------------------------
DROP TABLE IF EXISTS `sys_permission`;
CREATE TABLE `sys_permission`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '权限ID，主键',
  `permission_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限编码，例如：ticket:create、asset:update',
  `permission_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限名称，例如：创建工单、修改资产',
  `module_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '所属模块，例如：用户管理、工单管理、资产管理',
  `permission_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'api' COMMENT '权限类型：api接口权限，menu菜单权限，button按钮权限',
  `api_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接口请求方法，例如GET、POST、PUT、PATCH、DELETE',
  `api_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接口路径，例如 /api/v1/tickets',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '权限说明',
  `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序值，越小越靠前',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `permission_code`(`permission_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 146 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_permission
-- ----------------------------
INSERT INTO `sys_permission` VALUES (1, 'user:view', '查看用户', '用户管理', 'api', 'GET', '/api/v1/users', '查看用户列表和用户详情', 1, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (2, 'user:create', '创建用户', '用户管理', 'api', 'POST', '/api/v1/users', '创建系统用户', 2, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (3, 'user:update', '修改用户', '用户管理', 'api', 'PUT', '/api/v1/users/{user_id}', '修改用户基础信息', 3, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (4, 'user:status', '启用禁用用户', '用户管理', 'api', 'PATCH', '/api/v1/users/{user_id}/status', '启用或禁用用户账号', 4, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (5, 'user:reset_password', '重置用户密码', '用户管理', 'api', 'PATCH', '/api/v1/users/{user_id}/password', '管理员重置用户密码', 5, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (6, 'user:delete', '删除用户', '用户管理', 'api', 'DELETE', '/api/v1/users/{user_id}', '删除用户', 6, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (7, 'role:view', '查看角色', '角色权限管理', 'api', 'GET', '/api/v1/roles', '查看角色列表和详情', 7, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (8, 'role:create', '创建角色', '角色权限管理', 'api', 'POST', '/api/v1/roles', '创建角色', 8, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (9, 'role:update', '修改角色', '角色权限管理', 'api', 'PUT', '/api/v1/roles/{role_id}', '修改角色信息', 9, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (10, 'role:delete', '删除角色', '角色权限管理', 'api', 'DELETE', '/api/v1/roles/{role_id}', '删除角色', 10, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (11, 'role:assign_permission', '分配角色权限', '角色权限管理', 'api', 'PUT', '/api/v1/roles/{role_id}/permissions', '为角色分配权限', 11, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (12, 'permission:view', '查看权限', '角色权限管理', 'api', 'GET', '/api/v1/permissions', '查看权限列表', 12, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (13, 'user:assign_role', '分配用户角色', '角色权限管理', 'api', 'PUT', '/api/v1/users/{user_id}/roles', '为用户分配角色', 13, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (20, 'asset_category:view', '查看资产分类', '资产分类管理', 'api', 'GET', '/api/v1/asset-categories', '查看资产分类', 20, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (21, 'asset_category:create', '创建资产分类', '资产分类管理', 'api', 'POST', '/api/v1/asset-categories', '创建资产分类', 21, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (22, 'asset_category:update', '修改资产分类', '资产分类管理', 'api', 'PUT', '/api/v1/asset-categories/{category_id}', '修改资产分类', 22, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (23, 'asset_category:delete', '删除资产分类', '资产分类管理', 'api', 'DELETE', '/api/v1/asset-categories/{category_id}', '删除资产分类', 23, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (30, 'asset:view', '查看资产', '资产管理', 'api', 'GET', '/api/v1/assets', '查看资产列表和详情', 30, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (31, 'asset:create', '创建资产', '资产管理', 'api', 'POST', '/api/v1/assets', '创建资产', 31, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (32, 'asset:update', '修改资产', '资产管理', 'api', 'PUT', '/api/v1/assets/{asset_id}', '修改资产信息', 32, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (33, 'asset:status', '修改资产状态', '资产管理', 'api', 'PATCH', '/api/v1/assets/{asset_id}/status', '修改资产状态', 33, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (34, 'asset:delete', '删除资产', '资产管理', 'api', 'DELETE', '/api/v1/assets/{asset_id}', '删除资产', 34, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (35, 'asset:repair_records', '查看资产维修历史', '资产管理', 'api', 'GET', '/api/v1/assets/{asset_id}/repair-records', '查看指定资产维修历史', 35, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (40, 'ticket:view_all', '查看全部工单', '工单管理', 'api', 'GET', '/api/v1/tickets', '查看全部工单', 40, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (41, 'ticket:view_self', '查看自己的工单', '工单管理', 'api', 'GET', '/api/v1/tickets', '普通员工查看自己的工单', 41, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (42, 'ticket:create', '创建工单', '工单管理', 'api', 'POST', '/api/v1/tickets', '创建报修工单', 42, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (43, 'ticket:update', '修改工单', '工单管理', 'api', 'PUT', '/api/v1/tickets/{ticket_id}', '修改工单基础信息', 43, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (44, 'ticket:assign', '派单', '工单管理', 'api', 'PATCH', '/api/v1/tickets/{ticket_id}/assign', '管理员派单', 44, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (45, 'ticket:start', '开始处理工单', '工单管理', 'api', 'PATCH', '/api/v1/tickets/{ticket_id}/start', 'IT人员开始处理工单', 45, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (46, 'ticket:complete', '完成工单', '工单管理', 'api', 'PATCH', '/api/v1/tickets/{ticket_id}/complete', '完成工单并生成维修记录', 46, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (47, 'ticket:cancel', '取消工单', '工单管理', 'api', 'PATCH', '/api/v1/tickets/{ticket_id}/cancel', '取消工单', 47, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (48, 'ticket:delete', '删除工单', '工单管理', 'api', 'DELETE', '/api/v1/tickets/{ticket_id}', '删除工单', 48, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (49, 'ticket:records', '查看工单流转记录', '工单管理', 'api', 'GET', '/api/v1/tickets/{ticket_id}/records', '查看工单状态流转记录', 49, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (60, 'repair_record:view', '查看维修记录', '维修记录管理', 'api', 'GET', '/api/v1/repair-records', '查看维修记录列表和详情', 60, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (61, 'repair_record:update', '修改维修记录', '维修记录管理', 'api', 'PUT', '/api/v1/repair-records/{record_id}', '修改维修记录', 61, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (70, 'faq:view', '查看FAQ', 'FAQ管理', 'api', 'GET', '/api/v1/faqs', '查看常见问题列表和详情', 70, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (71, 'faq:create', '创建FAQ', 'FAQ管理', 'api', 'POST', '/api/v1/faqs', '创建常见问题', 71, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (72, 'faq:update', '修改FAQ', 'FAQ管理', 'api', 'PUT', '/api/v1/faqs/{faq_id}', '修改常见问题', 72, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (73, 'faq:status', '修改FAQ状态', 'FAQ管理', 'api', 'PATCH', '/api/v1/faqs/{faq_id}/status', '启用或停用FAQ', 73, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (74, 'faq:delete', '删除FAQ', 'FAQ管理', 'api', 'DELETE', '/api/v1/faqs/{faq_id}', '删除FAQ', 74, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (75, 'faq:stats', 'FAQ分类统计', 'FAQ管理', 'api', 'GET', '/api/v1/faqs/category-stats', '查看FAQ分类统计', 75, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (80, 'operation_log:view', '查看操作日志', '操作日志', 'api', 'GET', '/api/v1/operation-logs', '查看系统操作日志', 80, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (90, 'dashboard:view', '查看首页统计', '首页看板', 'api', 'GET', '/api/v1/dashboard/summary', '查看首页统计数据', 90, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (100, 'dict:view', '查看字典', '系统字典', 'api', 'GET', '/api/v1/dicts', '查看系统字典数据', 100, 1, '2026-06-23 17:18:49', '2026-06-23 17:18:49');
INSERT INTO `sys_permission` VALUES (110, 'sla:rule:list', '查看SLA规则', 'SLA规则管理', 'api', 'GET', '/api/v1/sla-rules', '查看SLA规则列表', 110, 1, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `sys_permission` VALUES (111, 'sla:rule:create', '创建SLA规则', 'SLA规则管理', 'api', 'POST', '/api/v1/sla-rules', '创建SLA规则', 111, 1, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `sys_permission` VALUES (112, 'sla:rule:update', '修改SLA规则', 'SLA规则管理', 'api', 'PUT', '/api/v1/sla-rules/{id}', '修改SLA规则', 112, 1, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `sys_permission` VALUES (113, 'sla:rule:delete', '删除SLA规则', 'SLA规则管理', 'api', 'DELETE', '/api/v1/sla-rules/{id}', '删除SLA规则', 113, 1, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `sys_permission` VALUES (114, 'sla:rule:enable', '启用停用SLA规则', 'SLA规则管理', 'api', 'PATCH', '/api/v1/sla-rules/{id}/enabled', '启用或停用SLA规则', 114, 1, '2026-06-24 00:00:00', '2026-06-24 00:00:00');
INSERT INTO `sys_permission` VALUES (120, 'todo:view_self', '查看我的待办', '待办事项', 'api', 'GET', '/api/v1/todos/my', '查看当前登录用户自己的待办事项', 120, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (121, 'todo:view_all', '查看全部待办', '待办事项', 'api', 'GET', '/api/v1/todos', '管理员查看全部待办事项', 121, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (122, 'todo:create', '创建待办', '待办事项', 'api', 'POST', '/api/v1/todos', '创建待办事项', 122, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (123, 'todo:update', '处理待办', '待办事项', 'api', 'PUT', '/api/v1/todos/{todo_id}/start', '开始或完成待办事项', 123, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (124, 'todo:cancel', '取消待办', '待办事项', 'api', 'PUT', '/api/v1/todos/{todo_id}/cancel', '取消待办事项', 124, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (130, 'work_group:list', '查看运维组', '运维组管理', 'api', 'GET', '/api/v1/work-groups', '查看运维组列表和详情', 130, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (131, 'work_group:create', '创建运维组', '运维组管理', 'api', 'POST', '/api/v1/work-groups', '创建运维组', 131, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (132, 'work_group:update', '修改运维组', '运维组管理', 'api', 'PUT', '/api/v1/work-groups/{id}', '修改运维组', 132, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (133, 'work_group:delete', '删除运维组', '运维组管理', 'api', 'DELETE', '/api/v1/work-groups/{id}', '删除运维组', 133, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (134, 'work_group:member:list', '查看运维组成员', '运维组管理', 'api', 'GET', '/api/v1/work-groups/{group_id}/members', '查看运维组成员列表', 134, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (135, 'work_group:member:add', '添加运维组成员', '运维组管理', 'api', 'POST', '/api/v1/work-groups/{group_id}/members', '添加运维组成员', 135, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (136, 'work_group:member:update', '修改运维组成员', '运维组管理', 'api', 'PUT', '/api/v1/work-groups/{group_id}/members/{user_id}', '修改运维组成员信息', 136, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (137, 'work_group:member:delete', '移除运维组成员', '运维组管理', 'api', 'DELETE', '/api/v1/work-groups/{group_id}/members/{user_id}', '移除运维组成员', 137, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (140, 'ticket:assignment-rule:list', '查看自动分配规则', '工单自动分配', 'api', 'GET', '/api/v1/ticket-assignment-rules', '查看工单自动分配规则', 140, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (141, 'ticket:assignment-rule:create', '创建自动分配规则', '工单自动分配', 'api', 'POST', '/api/v1/ticket-assignment-rules', '创建工单自动分配规则', 141, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (142, 'ticket:assignment-rule:update', '修改自动分配规则', '工单自动分配', 'api', 'PUT', '/api/v1/ticket-assignment-rules/{id}', '修改工单自动分配规则', 142, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (143, 'ticket:assignment-rule:delete', '删除自动分配规则', '工单自动分配', 'api', 'DELETE', '/api/v1/ticket-assignment-rules/{id}', '删除工单自动分配规则', 143, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (144, 'ticket:assignment-rule:status', '启用停用自动分配规则', '工单自动分配', 'api', 'PATCH', '/api/v1/ticket-assignment-rules/{id}/status', '启用或停用工单自动分配规则', 144, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `sys_permission` VALUES (145, 'ticket:auto-assign', '手动触发自动分配', '工单自动分配', 'api', 'POST', '/api/v1/tickets/{id}/auto-assign', '管理员手动触发工单自动分配', 145, 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00');

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '角色ID，主键',
  `role_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色编码，例如：admin、it_staff、employee',
  `role_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色名称，例如：管理员、IT运维人员、普通员工',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '角色说明',
  `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序值，越小越靠前',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `role_code`(`role_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统角色表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role
-- ----------------------------
INSERT INTO `sys_role` VALUES (1, 'admin', '系统管理员', '拥有系统全部权限，可以管理用户、角色、权限、资产、工单和日志', 1, 1, '2026-06-23 17:18:35', '2026-06-23 17:18:35');
INSERT INTO `sys_role` VALUES (2, 'it_staff', 'IT运维人员', '负责查看、接单、处理工单，并查看资产和维修记录', 2, 1, '2026-06-23 17:18:35', '2026-06-23 17:18:35');
INSERT INTO `sys_role` VALUES (3, 'employee', '普通员工', '企业内部普通员工，可以提交报修、查看自己的工单和FAQ', 3, 1, '2026-06-23 17:18:35', '2026-06-23 17:18:35');

-- ----------------------------
-- Table structure for sys_role_permission
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_permission`;
CREATE TABLE `sys_role_permission`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '角色权限关联ID，主键',
  `role_id` bigint(20) NOT NULL COMMENT '角色ID，关联sys_role表',
  `permission_id` bigint(20) NOT NULL COMMENT '权限ID，关联sys_permission表',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_role_permission`(`role_id`, `permission_id`) USING BTREE,
  INDEX `fk_role_permission_permission`(`permission_id`) USING BTREE,
  CONSTRAINT `fk_role_permission_permission` FOREIGN KEY (`permission_id`) REFERENCES `sys_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_role_permission_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 122 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '角色权限关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_role_permission
-- ----------------------------
INSERT INTO `sys_role_permission` VALUES (1, 1, 1, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (2, 1, 2, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (3, 1, 3, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (4, 1, 4, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (5, 1, 5, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (6, 1, 6, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (7, 1, 7, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (8, 1, 8, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (9, 1, 9, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (10, 1, 10, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (11, 1, 11, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (12, 1, 12, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (13, 1, 13, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (14, 1, 20, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (15, 1, 21, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (16, 1, 22, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (17, 1, 23, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (18, 1, 30, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (19, 1, 31, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (20, 1, 32, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (21, 1, 33, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (22, 1, 34, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (23, 1, 35, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (24, 1, 40, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (25, 1, 41, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (26, 1, 42, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (27, 1, 43, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (28, 1, 44, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (29, 1, 45, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (30, 1, 46, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (31, 1, 47, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (32, 1, 48, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (33, 1, 49, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (34, 1, 60, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (35, 1, 61, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (36, 1, 70, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (37, 1, 71, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (38, 1, 72, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (39, 1, 73, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (40, 1, 74, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (41, 1, 75, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (42, 1, 80, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (43, 1, 90, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (44, 1, 100, '2026-06-23 17:19:18');
INSERT INTO `sys_role_permission` VALUES (94, 1, 110, '2026-06-24 00:00:00');
INSERT INTO `sys_role_permission` VALUES (95, 1, 111, '2026-06-24 00:00:00');
INSERT INTO `sys_role_permission` VALUES (96, 1, 112, '2026-06-24 00:00:00');
INSERT INTO `sys_role_permission` VALUES (97, 1, 113, '2026-06-24 00:00:00');
INSERT INTO `sys_role_permission` VALUES (98, 1, 114, '2026-06-24 00:00:00');
INSERT INTO `sys_role_permission` VALUES (99, 1, 120, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (100, 1, 121, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (101, 1, 122, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (102, 1, 123, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (103, 1, 124, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (104, 2, 120, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (105, 2, 123, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (106, 3, 120, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (107, 3, 123, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (108, 1, 130, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (109, 1, 131, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (110, 1, 132, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (111, 1, 133, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (112, 1, 134, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (113, 1, 135, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (114, 1, 136, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (115, 1, 137, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (116, 1, 140, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (117, 1, 141, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (118, 1, 142, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (119, 1, 143, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (120, 1, 144, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (121, 1, 145, '2026-06-25 00:00:00');
INSERT INTO `sys_role_permission` VALUES (64, 2, 35, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (65, 2, 33, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (66, 2, 30, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (67, 2, 20, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (68, 2, 90, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (69, 2, 100, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (70, 2, 75, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (71, 2, 70, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (72, 2, 60, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (73, 2, 46, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (74, 2, 49, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (75, 2, 45, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (76, 2, 40, '2026-06-23 17:19:26');
INSERT INTO `sys_role_permission` VALUES (79, 3, 100, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (80, 3, 75, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (81, 3, 70, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (82, 3, 47, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (83, 3, 42, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (84, 3, 49, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (85, 3, 43, '2026-06-23 17:19:36');
INSERT INTO `sys_role_permission` VALUES (86, 3, 41, '2026-06-23 17:19:36');

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户ID，主键',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '登录用户名',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '加密后的登录密码',
  `real_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户真实姓名',
  `role` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户角色：admin管理员，it_staff运维人员，employee普通员工',
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属部门',
  `phone` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '联系电话',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '邮箱地址',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '账号状态：1启用，0禁用',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user
-- ----------------------------
INSERT INTO `sys_user` VALUES (1, 'admin', 'pbkdf2_sha256$260000$abc123$26f0fb8c10bb28dc85118fe973c28b0521d6c98d766db114a04e358e74c447f0', '系统管理员', 'admin', '信息部', '13800000001', 'admin@example.com', 1, '2026-06-22 19:39:10', '2026-06-22 20:44:50');
INSERT INTO `sys_user` VALUES (2, 'it_zhang', 'pbkdf2_sha256$260000$abc123$26f0fb8c10bb28dc85118fe973c28b0521d6c98d766db114a04e358e74c447f0', '张工', 'it_staff', '信息部', '13800000002', 'zhang@example.com', 1, '2026-06-22 19:39:10', '2026-06-22 20:46:06');
INSERT INTO `sys_user` VALUES (3, 'employee_li', 'pbkdf2_sha256$260000$abc123$26f0fb8c10bb28dc85118fe973c28b0521d6c98d766db114a04e358e74c447f0', '李明', 'employee', '财务部', '13800000003', 'liming@example.com', 1, '2026-06-22 19:39:10', '2026-06-22 20:46:07');
INSERT INTO `sys_user` VALUES (4, 'employee_wang', 'pbkdf2_sha256$260000$abc123$26f0fb8c10bb28dc85118fe973c28b0521d6c98d766db114a04e358e74c447f0', '王芳', 'employee', '运营部', '13800000004', 'wangfang@example.com', 1, '2026-06-22 19:39:10', '2026-06-22 20:46:10');

-- ----------------------------
-- Table structure for it_work_group
-- ----------------------------
DROP TABLE IF EXISTS `it_work_group`;
CREATE TABLE `it_work_group`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '运维组ID',
  `group_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '运维组名称',
  `group_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '运维组编码',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '运维组说明',
  `leader_id` bigint(20) NULL DEFAULT NULL COMMENT '组长用户ID，关联sys_user表',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
  `sort_order` int(11) NOT NULL DEFAULT 0 COMMENT '排序值，越小越靠前',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_group_code`(`group_code`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  INDEX `idx_sort_order`(`sort_order`) USING BTREE,
  INDEX `fk_work_group_leader`(`leader_id`) USING BTREE,
  CONSTRAINT `fk_work_group_leader` FOREIGN KEY (`leader_id`) REFERENCES `sys_user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '运维组表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_work_group
-- ----------------------------
INSERT INTO `it_work_group` VALUES (1, '桌面运维组', 'desktop', '负责办公电脑、桌面软件等日常运维支持', NULL, 1, 10, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `it_work_group` VALUES (2, '网络运维组', 'network', '负责网络链路、交换机、无线网络等运维支持', NULL, 1, 20, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `it_work_group` VALUES (3, '打印机维护组', 'printer', '负责打印机、复印机及耗材相关维护', NULL, 1, 30, '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `it_work_group` VALUES (4, '系统账号组', 'account', '负责账号开通、权限申请和系统登录问题', NULL, 1, 40, '2026-06-25 00:00:00', '2026-06-25 00:00:00');

-- ----------------------------
-- Table structure for it_work_group_member
-- ----------------------------
DROP TABLE IF EXISTS `it_work_group_member`;
CREATE TABLE `it_work_group_member`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '成员关系ID',
  `group_id` bigint(20) NOT NULL COMMENT '运维组ID，关联it_work_group表',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID，关联sys_user表',
  `member_role` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'member' COMMENT '组内角色：leader组长，member成员',
  `status` tinyint(4) NOT NULL DEFAULT 1 COMMENT '状态：1启用，0停用',
  `joined_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_group_user`(`group_id`, `user_id`) USING BTREE,
  INDEX `idx_group_id`(`group_id`) USING BTREE,
  INDEX `idx_user_id`(`user_id`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  CONSTRAINT `fk_work_group_member_group` FOREIGN KEY (`group_id`) REFERENCES `it_work_group` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_work_group_member_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '运维组成员表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of it_work_group_member
-- ----------------------------
INSERT INTO `it_work_group_member` VALUES (1, 1, 2, 'leader', 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `it_work_group_member` VALUES (2, 2, 2, 'member', 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `it_work_group_member` VALUES (3, 3, 2, 'member', 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `it_work_group_member` VALUES (4, 4, 2, 'member', 1, '2026-06-25 00:00:00', '2026-06-25 00:00:00', '2026-06-25 00:00:00');

-- ----------------------------
-- Table structure for ticket_assignment_rule
-- ----------------------------
DROP TABLE IF EXISTS `ticket_assignment_rule`;
CREATE TABLE `ticket_assignment_rule`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自动分配规则ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '规则名称',
  `category_id` bigint(20) NULL DEFAULT NULL COMMENT '工单分类ID，可为空表示不限制分类',
  `priority` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '优先级，可为空表示不限制优先级',
  `ops_group_id` bigint(20) NULL DEFAULT NULL COMMENT '运维组ID，least_workload策略必填',
  `assign_strategy` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '分配策略：least_workload最少工单，fixed_user固定人员',
  `target_user_id` bigint(20) NULL DEFAULT NULL COMMENT '固定处理人ID，仅fixed_user策略使用',
  `enabled` tinyint(4) NOT NULL DEFAULT 1 COMMENT '是否启用：1启用，0停用',
  `sort_order` int(11) NOT NULL DEFAULT 100 COMMENT '排序值，越小越优先',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_assignment_rule_enabled`(`enabled`) USING BTREE,
  INDEX `idx_assignment_rule_category`(`category_id`) USING BTREE,
  INDEX `idx_assignment_rule_priority`(`priority`) USING BTREE,
  INDEX `idx_assignment_rule_ops_group`(`ops_group_id`) USING BTREE,
  INDEX `idx_assignment_rule_target_user`(`target_user_id`) USING BTREE,
  INDEX `idx_assignment_rule_sort`(`sort_order`) USING BTREE,
  INDEX `idx_assignment_rule_match`(`enabled`, `category_id`, `priority`, `sort_order`) USING BTREE,
  CONSTRAINT `fk_assignment_rule_ops_group` FOREIGN KEY (`ops_group_id`) REFERENCES `it_work_group` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_assignment_rule_target_user` FOREIGN KEY (`target_user_id`) REFERENCES `sys_user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '工单自动分配规则表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of ticket_assignment_rule
-- ----------------------------
INSERT INTO `ticket_assignment_rule` VALUES (1, '电脑故障自动分配规则', 1, NULL, 1, 'least_workload', NULL, 1, 10, '电脑故障分配给桌面运维组中当前工单最少的人', '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `ticket_assignment_rule` VALUES (2, '网络故障自动分配规则', 2, NULL, 2, 'least_workload', NULL, 1, 20, '网络故障分配给网络运维组中当前工单最少的人', '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `ticket_assignment_rule` VALUES (3, '打印机故障自动分配规则', 3, NULL, 3, 'least_workload', NULL, 1, 30, '打印机故障分配给打印机维护组中当前工单最少的人', '2026-06-25 00:00:00', '2026-06-25 00:00:00');
INSERT INTO `ticket_assignment_rule` VALUES (4, '账号系统固定分配规则', NULL, 'urgent', 4, 'fixed_user', 2, 1, 40, '紧急账号系统故障固定分配给张工', '2026-06-25 00:00:00', '2026-06-25 00:00:00');

-- ----------------------------
-- Table structure for ticket_assignment_log
-- ----------------------------
DROP TABLE IF EXISTS `ticket_assignment_log`;
CREATE TABLE `ticket_assignment_log`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自动分配日志ID',
  `ticket_id` bigint(20) NOT NULL COMMENT '工单ID',
  `rule_id` bigint(20) NULL DEFAULT NULL COMMENT '命中的规则ID',
  `ops_group_id` bigint(20) NULL DEFAULT NULL COMMENT '运维组ID',
  `assignee_id` bigint(20) NULL DEFAULT NULL COMMENT '最终处理人ID',
  `assign_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '分配来源，自动分配时为auto',
  `assign_strategy` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '分配策略',
  `success` tinyint(4) NOT NULL DEFAULT 0 COMMENT '是否成功：1成功，0失败',
  `fail_stage` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '失败阶段',
  `fail_reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '失败原因',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_assignment_log_ticket`(`ticket_id`) USING BTREE,
  INDEX `idx_assignment_log_rule`(`rule_id`) USING BTREE,
  INDEX `idx_assignment_log_assignee`(`assignee_id`) USING BTREE,
  INDEX `idx_assignment_log_success`(`success`) USING BTREE,
  INDEX `idx_assignment_log_created_at`(`created_at`) USING BTREE,
  CONSTRAINT `fk_assignment_log_ticket` FOREIGN KEY (`ticket_id`) REFERENCES `it_ticket` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_assignment_log_rule` FOREIGN KEY (`rule_id`) REFERENCES `ticket_assignment_rule` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_assignment_log_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `sys_user` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '工单自动分配日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_todo
-- ----------------------------
DROP TABLE IF EXISTS `sys_todo`;
CREATE TABLE `sys_todo`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '待办ID，主键',
  `todo_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '待办编号',
  `title` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '待办标题',
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '待办内容',
  `todo_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '待办类型',
  `business_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '业务类型',
  `business_id` bigint(20) NOT NULL COMMENT '关联业务ID',
  `assignee_id` bigint(20) NULL DEFAULT NULL COMMENT '待办处理人ID',
  `assignee_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '待办处理人名称',
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'pending' COMMENT '待办状态：pending待处理，processing处理中，completed已完成，cancelled已取消，expired已超时',
  `priority` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'normal' COMMENT '优先级：low低，normal普通，high高，urgent紧急',
  `deadline_at` datetime NULL DEFAULT NULL COMMENT '截止时间',
  `completed_at` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `cancelled_at` datetime NULL DEFAULT NULL COMMENT '取消时间',
  `reminded_at` datetime NULL DEFAULT NULL COMMENT '超时提醒时间',
  `expire_notice_sent` tinyint(4) NOT NULL DEFAULT 0 COMMENT '超时提醒是否已发送：0否，1是',
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '备注',
  `created_by` bigint(20) NULL DEFAULT NULL COMMENT '创建人ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(4) NOT NULL DEFAULT 0 COMMENT '逻辑删除标识：0正常，1已删除',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `todo_no`(`todo_no`) USING BTREE,
  INDEX `idx_todo_assignee`(`assignee_id`) USING BTREE,
  INDEX `idx_todo_business`(`business_type`, `business_id`) USING BTREE,
  INDEX `idx_todo_status_deadline`(`status`, `deadline_at`) USING BTREE,
  CONSTRAINT `fk_todo_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '待办事项表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_todo
-- ----------------------------
INSERT INTO `sys_todo` VALUES (1, 'TODO202606250001', '待处理工单：打印机无法打印', '工单 TK202606230002/打印机无法打印 已分配给你，请及时处理。', 'ticket_process', 'ticket', 6, 2, '张工', 'pending', 'normal', '2026-06-25 10:00:00', NULL, NULL, NULL, 0, NULL, 1, '2026-06-25 09:00:00', '2026-06-25 09:00:00', 0);
INSERT INTO `sys_todo` VALUES (2, 'TODO202606250002', '已超时工单待办：部分电脑访问内网系统较慢', '工单 TK202606210003/部分电脑访问内网系统较慢 已超过待办截止时间。', 'ticket_process', 'ticket', 3, 2, '张工', 'expired', 'urgent', '2026-06-21 12:20:00', NULL, NULL, '2026-06-25 09:05:00', 1, NULL, 1, '2026-06-25 09:00:00', '2026-06-25 09:05:00', 0);
INSERT INTO `sys_todo` VALUES (3, 'TODO202606250003', '待确认工单：财务电脑无法开机', '工单 TK202606210001/财务电脑无法开机 已处理完成，请确认结果。', 'ticket_confirm', 'ticket', 1, 3, '李明', 'pending', 'high', NULL, NULL, NULL, NULL, 0, NULL, 2, '2026-06-25 09:00:00', '2026-06-25 09:00:00', 0);

-- ----------------------------
-- Table structure for sys_user_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_user_role`;
CREATE TABLE `sys_user_role`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '用户角色关联ID，主键',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID，关联sys_user表',
  `role_id` bigint(20) NOT NULL COMMENT '角色ID，关联sys_role表',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_user_role`(`user_id`, `role_id`) USING BTREE,
  INDEX `fk_user_role_role`(`role_id`) USING BTREE,
  CONSTRAINT `fk_user_role_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_role_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户角色关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sys_user_role
-- ----------------------------
INSERT INTO `sys_user_role` VALUES (1, 1, 1, '2026-06-23 17:19:08');
INSERT INTO `sys_user_role` VALUES (2, 2, 2, '2026-06-23 17:19:08');
INSERT INTO `sys_user_role` VALUES (3, 3, 3, '2026-06-23 17:19:08');
INSERT INTO `sys_user_role` VALUES (4, 4, 3, '2026-06-23 17:19:08');

SET FOREIGN_KEY_CHECKS = 1;
