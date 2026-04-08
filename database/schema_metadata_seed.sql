-- ============================================================
-- Schema 元数据种子数据
-- 将原 db_service.py 中硬编码的 Schema 文本迁移到元数据表集中管理
-- ============================================================
USE chatbi_oee_schema;

-- 清空旧数据（幂等执行）
TRUNCATE TABLE schema_metadata;

-- ============================================
-- 1. equipment（设备主数据表）  sort_order=10
-- ============================================
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sample_values, business_rule, is_important, sort_order) VALUES
('equipment', NULL,               NULL,                                                   '设备主数据表',        NULL, NULL, TRUE, 10),
('equipment', 'id',               'INT',                                                  '主键',               NULL, NULL, TRUE, 10),
('equipment', 'equipment_code',   'VARCHAR(50)',                                           '设备编号',           '如 EQ-A01', NULL, TRUE, 10),
('equipment', 'equipment_name',   'VARCHAR(100)',                                          '设备名称',           NULL, NULL, TRUE, 10),
('equipment', 'equipment_type',   'VARCHAR(50)',                                           '设备类型',           'CNC加工中心/数控车床/注塑机/冲压机/自动组装线/焊接机器人', NULL, TRUE, 10),
('equipment', 'workshop',         'VARCHAR(50)',                                           '车间',               '一车间/二车间/三车间', NULL, TRUE, 10),
('equipment', 'production_line',  'VARCHAR(50)',                                           '产线',               'A线/B线/C线/D线/E线/F线', NULL, TRUE, 10),
('equipment', 'ideal_cycle_time', 'DECIMAL(10,2)',                                         '理论节拍(秒/件)',     NULL, NULL, TRUE, 10),
('equipment', 'status',           'ENUM(''running'',''idle'',''maintenance'',''breakdown'')', '当前状态',         NULL, NULL, TRUE, 10);

-- ============================================
-- 2. product（产品主数据表）  sort_order=20
-- ============================================
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sample_values, business_rule, is_important, sort_order) VALUES
('product', NULL,               NULL,            '产品主数据表',  NULL, NULL, TRUE, 20),
('product', 'id',               'INT',           '主键',         NULL, NULL, TRUE, 20),
('product', 'product_code',     'VARCHAR(50)',   '产品编号',      NULL, NULL, TRUE, 20),
('product', 'product_name',     'VARCHAR(100)',  '产品名称',      NULL, NULL, TRUE, 20),
('product', 'product_category', 'VARCHAR(50)',   '产品类别',      NULL, NULL, TRUE, 20);

-- ============================================
-- 3. production_record（生产记录表）  sort_order=30
-- ============================================
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sample_values, business_rule, is_important, sort_order) VALUES
('production_record', NULL,                       NULL,            '生产记录表',          NULL, NULL, TRUE, 30),
('production_record', 'id',                       'INT',           '主键',               NULL, NULL, TRUE, 30),
('production_record', 'record_date',              'DATE',          '生产日期',            NULL, NULL, TRUE, 30),
('production_record', 'shift',                    'VARCHAR(20)',   '班次',                '早班/中班/晚班', NULL, TRUE, 30),
('production_record', 'equipment_id',             'INT',           '设备ID',              NULL, '关联 equipment.id', TRUE, 30),
('production_record', 'product_id',               'INT',           '产品ID',              NULL, '关联 product.id', TRUE, 30),
('production_record', 'planned_duration_minutes',  'INT',           '计划生产时长(分钟)',   NULL, NULL, TRUE, 30),
('production_record', 'actual_run_minutes',        'DECIMAL(10,2)', '实际运行时长(分钟)',   NULL, NULL, TRUE, 30),
('production_record', 'total_count',               'INT',           '总产出数量',          NULL, NULL, TRUE, 30),
('production_record', 'good_count',                'INT',           '合格数量',            NULL, NULL, TRUE, 30),
('production_record', 'defect_count',              'INT',           '不良数量',            NULL, NULL, TRUE, 30),
('production_record', 'ideal_cycle_time',          'DECIMAL(10,2)', '理论节拍(秒/件)',     NULL, NULL, TRUE, 30);

-- ============================================
-- 4. downtime_record（停机记录表）  sort_order=40
-- ============================================
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sample_values, business_rule, is_important, sort_order) VALUES
('downtime_record', NULL,                 NULL,                                  '停机记录表',  NULL, NULL, TRUE, 40),
('downtime_record', 'id',                 'INT',                                 '主键',       NULL, NULL, TRUE, 40),
('downtime_record', 'record_date',        'DATE',                                '日期',       NULL, NULL, TRUE, 40),
('downtime_record', 'shift',              'VARCHAR(20)',                         '班次',       NULL, NULL, TRUE, 40),
('downtime_record', 'equipment_id',       'INT',                                 '设备ID',     NULL, '关联 equipment.id', TRUE, 40),
('downtime_record', 'downtime_type',      'ENUM(''planned'',''unplanned'')',     '停机类型',    'planned=计划停机, unplanned=非计划停机', NULL, TRUE, 40),
('downtime_record', 'downtime_category',  'VARCHAR(50)',                         '停机分类',    '机械故障/电气故障/物料问题/质量问题/换型调整/计划保养', NULL, TRUE, 40),
('downtime_record', 'downtime_reason',    'VARCHAR(200)',                        '停机原因',    NULL, NULL, TRUE, 40),
('downtime_record', 'start_time',         'DATETIME',                            '开始时间',    NULL, NULL, TRUE, 40),
('downtime_record', 'end_time',           'DATETIME',                            '结束时间',    NULL, NULL, TRUE, 40),
('downtime_record', 'duration_minutes',   'DECIMAL(10,2)',                       '停机时长(分钟)', NULL, NULL, TRUE, 40);

-- ============================================
-- 5. oee_daily（OEE日汇总视图）  sort_order=50
-- ============================================
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sample_values, business_rule, is_important, sort_order) VALUES
('oee_daily', NULL,                       NULL,            'OEE日汇总视图, 已JOIN了 equipment 和 product 表, 直接查询即可, 无需再JOIN这两张表', NULL, NULL, TRUE, 50),
('oee_daily', 'record_date',              'DATE',          '生产日期',       NULL, NULL, TRUE, 50),
('oee_daily', 'shift',                    'VARCHAR(20)',   '班次',           NULL, NULL, TRUE, 50),
('oee_daily', 'equipment_id',             'INT',           '设备ID',         NULL, '可用于子查询关联 equipment 表获取 equipment_type', TRUE, 50),
('oee_daily', 'equipment_code',           'VARCHAR(50)',   '设备编号',       NULL, NULL, TRUE, 50),
('oee_daily', 'equipment_name',           'VARCHAR(100)',  '设备名称',       NULL, NULL, TRUE, 50),
('oee_daily', 'workshop',                 'VARCHAR(50)',   '车间',           NULL, NULL, TRUE, 50),
('oee_daily', 'production_line',          'VARCHAR(50)',   '产线',           NULL, NULL, TRUE, 50),
('oee_daily', 'product_name',             'VARCHAR(100)',  '产品名称',       NULL, NULL, TRUE, 50),
('oee_daily', 'planned_duration_minutes', 'INT',           '计划时长',       NULL, NULL, TRUE, 50),
('oee_daily', 'actual_run_minutes',       'DECIMAL',       '实际运行时长',    NULL, NULL, TRUE, 50),
('oee_daily', 'total_count',              'INT',           '总产出',         NULL, NULL, TRUE, 50),
('oee_daily', 'good_count',               'INT',           '合格数',         NULL, NULL, TRUE, 50),
('oee_daily', 'defect_count',             'INT',           '不良数',         NULL, NULL, TRUE, 50),
('oee_daily', 'availability',             'DECIMAL',       '可用率(%)',       NULL, NULL, TRUE, 50),
('oee_daily', 'performance',              'DECIMAL',       '性能率(%)',       NULL, NULL, TRUE, 50),
('oee_daily', 'quality',                  'DECIMAL',       '质量率(%)',       NULL, NULL, TRUE, 50),
('oee_daily', 'oee',                      'DECIMAL',       'OEE(%)',         NULL, NULL, TRUE, 50);

-- ============================================
-- 6. 全局业务规则  sort_order=900+
-- ============================================
INSERT INTO schema_metadata (table_name, column_name, column_type, description, sample_values, business_rule, is_important, sort_order) VALUES
('_global', 'oee_formula', NULL, 'OEE计算公式',  NULL,
 '- 可用率(Availability) = 实际运行时间 / 计划生产时间 × 100%\n- 性能率(Performance) = (理论节拍 × 总产出) / (实际运行时间 × 60) × 100%\n- 质量率(Quality) = 合格数量 / 总产出数量 × 100%\n- OEE = 可用率 × 性能率 × 质量率 / 10000 (因为三项都是百分比)',
 TRUE, 900),
('_global', 'data_range',  NULL, '数据时间范围: 2026-01-01 至 2026-03-31 (工作日)', NULL, NULL, TRUE, 901);
