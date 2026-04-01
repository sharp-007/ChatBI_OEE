-- ChatBI OEE 数据库建表脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS chatbi_oee
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE chatbi_oee;

-- ============================================
-- 1. 设备主数据表
-- ============================================
CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_code VARCHAR(50) NOT NULL UNIQUE COMMENT '设备编号',
    equipment_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    equipment_type VARCHAR(50) NOT NULL COMMENT '设备类型',
    workshop VARCHAR(50) NOT NULL COMMENT '车间',
    production_line VARCHAR(50) NOT NULL COMMENT '产线',
    ideal_cycle_time DECIMAL(10, 2) NOT NULL COMMENT '理论节拍(秒/件)',
    status ENUM('running', 'idle', 'maintenance', 'breakdown') DEFAULT 'idle' COMMENT '当前状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_workshop (workshop),
    INDEX idx_production_line (production_line)
) COMMENT '设备主数据表';

-- ============================================
-- 2. 产品主数据表
-- ============================================
CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE COMMENT '产品编号',
    product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
    product_category VARCHAR(50) COMMENT '产品类别',
    unit VARCHAR(20) DEFAULT '件' COMMENT '单位',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) COMMENT '产品主数据表';

-- ============================================
-- 3. 生产计划表
-- ============================================
CREATE TABLE IF NOT EXISTS production_plan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_date DATE NOT NULL COMMENT '计划日期',
    shift VARCHAR(20) NOT NULL COMMENT '班次(早班/中班/晚班)',
    equipment_id INT NOT NULL COMMENT '设备ID',
    product_id INT NOT NULL COMMENT '产品ID',
    planned_quantity INT NOT NULL COMMENT '计划产量',
    planned_duration_minutes INT NOT NULL COMMENT '计划生产时长(分钟)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    INDEX idx_plan_date (plan_date),
    INDEX idx_equipment (equipment_id)
) COMMENT '生产计划表';

-- ============================================
-- 4. 生产记录表
-- ============================================
CREATE TABLE IF NOT EXISTS production_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_date DATE NOT NULL COMMENT '生产日期',
    shift VARCHAR(20) NOT NULL COMMENT '班次',
    equipment_id INT NOT NULL COMMENT '设备ID',
    product_id INT NOT NULL COMMENT '产品ID',
    planned_duration_minutes INT NOT NULL COMMENT '计划生产时长(分钟)',
    actual_run_minutes DECIMAL(10, 2) NOT NULL COMMENT '实际运行时长(分钟)',
    total_count INT NOT NULL COMMENT '总产出数量',
    good_count INT NOT NULL COMMENT '合格数量',
    defect_count INT NOT NULL COMMENT '不良数量',
    ideal_cycle_time DECIMAL(10, 2) NOT NULL COMMENT '理论节拍(秒/件)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (product_id) REFERENCES product(id),
    INDEX idx_record_date (record_date),
    INDEX idx_equipment_date (equipment_id, record_date)
) COMMENT '生产记录表';

-- ============================================
-- 5. 停机记录表
-- ============================================
CREATE TABLE IF NOT EXISTS downtime_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_date DATE NOT NULL COMMENT '日期',
    shift VARCHAR(20) NOT NULL COMMENT '班次',
    equipment_id INT NOT NULL COMMENT '设备ID',
    downtime_type ENUM('planned', 'unplanned') NOT NULL COMMENT '停机类型(计划/非计划)',
    downtime_category VARCHAR(50) NOT NULL COMMENT '停机分类',
    downtime_reason VARCHAR(200) NOT NULL COMMENT '停机原因',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME NOT NULL COMMENT '结束时间',
    duration_minutes DECIMAL(10, 2) NOT NULL COMMENT '停机时长(分钟)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    INDEX idx_record_date (record_date),
    INDEX idx_equipment (equipment_id),
    INDEX idx_downtime_type (downtime_type)
) COMMENT '停机记录表';

-- ============================================
-- 6. OEE 日汇总视图
-- ============================================
CREATE OR REPLACE VIEW oee_daily AS
SELECT
    pr.record_date,
    pr.shift,
    pr.equipment_id,
    e.equipment_code,
    e.equipment_name,
    e.workshop,
    e.production_line,
    p.product_name,
    pr.planned_duration_minutes,
    pr.actual_run_minutes,
    pr.total_count,
    pr.good_count,
    pr.defect_count,
    pr.ideal_cycle_time,
    -- 可用率 = 实际运行时间 / 计划生产时间
    ROUND(pr.actual_run_minutes / pr.planned_duration_minutes * 100, 2) AS availability,
    -- 性能率 = (理论节拍 × 总产出) / (实际运行时间 × 60)
    ROUND((pr.ideal_cycle_time * pr.total_count) / (pr.actual_run_minutes * 60) * 100, 2) AS performance,
    -- 质量率 = 合格数量 / 总产出数量
    ROUND(pr.good_count / pr.total_count * 100, 2) AS quality,
    -- OEE = 可用率 × 性能率 × 质量率
    ROUND(
        (pr.actual_run_minutes / pr.planned_duration_minutes)
        * ((pr.ideal_cycle_time * pr.total_count) / (pr.actual_run_minutes * 60))
        * (pr.good_count / pr.total_count)
        * 100, 2
    ) AS oee
FROM production_record pr
JOIN equipment e ON pr.equipment_id = e.id
JOIN product p ON pr.product_id = p.id;
