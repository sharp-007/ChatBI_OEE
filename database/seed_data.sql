-- ChatBI OEE 演示数据填充脚本
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
USE chatbi_oee;

-- ============================================
-- 1. 设备数据 (3个车间, 10台设备)
-- ============================================
INSERT INTO equipment (equipment_code, equipment_name, equipment_type, workshop, production_line, ideal_cycle_time, status) VALUES
('EQ-A01', 'CNC加工中心-1', 'CNC加工中心', '一车间', 'A线', 30.00, 'running'),
('EQ-A02', 'CNC加工中心-2', 'CNC加工中心', '一车间', 'A线', 30.00, 'running'),
('EQ-A03', '数控车床-1', '数控车床', '一车间', 'B线', 25.00, 'running'),
('EQ-B01', '注塑机-1', '注塑机', '二车间', 'C线', 15.00, 'running'),
('EQ-B02', '注塑机-2', '注塑机', '二车间', 'C线', 15.00, 'idle'),
('EQ-B03', '冲压机-1', '冲压机', '二车间', 'D线', 8.00, 'running'),
('EQ-B04', '冲压机-2', '冲压机', '二车间', 'D线', 8.00, 'maintenance'),
('EQ-C01', '组装线-1', '自动组装线', '三车间', 'E线', 20.00, 'running'),
('EQ-C02', '组装线-2', '自动组装线', '三车间', 'E线', 20.00, 'running'),
('EQ-C03', '焊接机器人-1', '焊接机器人', '三车间', 'F线', 35.00, 'running');

-- ============================================
-- 2. 产品数据
-- ============================================
INSERT INTO product (product_code, product_name, product_category, unit) VALUES
('P001', '铝合金壳体A', '壳体', '件'),
('P002', '铝合金壳体B', '壳体', '件'),
('P003', '传动轴', '轴类', '件'),
('P004', '塑料外壳-标准', '注塑件', '件'),
('P005', '塑料外壳-加强', '注塑件', '件'),
('P006', '金属底板', '冲压件', '件'),
('P007', '控制器总成', '组件', '套'),
('P008', '传感器支架', '焊接件', '件');

-- ============================================
-- 3. 生产记录数据 (2026年1月-3月, 每台设备每天1-2个班次)
-- ============================================
-- 使用存储过程批量生成演示数据
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS generate_demo_data()
BEGIN
    DECLARE v_date DATE DEFAULT '2026-01-01';
    DECLARE v_end_date DATE DEFAULT '2026-03-31';
    DECLARE v_eq_id INT;
    DECLARE v_prod_id INT;
    DECLARE v_planned_min INT;
    DECLARE v_actual_min DECIMAL(10,2);
    DECLARE v_ideal_ct DECIMAL(10,2);
    DECLARE v_total_count INT;
    DECLARE v_good_count INT;
    DECLARE v_avail_factor DECIMAL(5,4);
    DECLARE v_perf_factor DECIMAL(5,4);
    DECLARE v_qual_factor DECIMAL(5,4);

    WHILE v_date <= v_end_date DO
        IF DAYOFWEEK(v_date) NOT IN (1, 7) THEN

            -- 设备1: CNC加工中心-1, 产品: 铝合金壳体A
            SET v_planned_min = 480;
            SET v_avail_factor = 0.85 + (RAND() * 0.12);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_ideal_ct = 30.00;
            SET v_perf_factor = 0.80 + (RAND() * 0.15);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.95 + (RAND() * 0.04);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 1, 1, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备2: CNC加工中心-2
            SET v_avail_factor = 0.82 + (RAND() * 0.15);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.78 + (RAND() * 0.18);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.93 + (RAND() * 0.06);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 2, 2, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备3: 数控车床-1
            SET v_ideal_ct = 25.00;
            SET v_avail_factor = 0.88 + (RAND() * 0.10);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.82 + (RAND() * 0.14);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.96 + (RAND() * 0.03);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 3, 3, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备4: 注塑机-1
            SET v_ideal_ct = 15.00;
            SET v_avail_factor = 0.86 + (RAND() * 0.12);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.83 + (RAND() * 0.14);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.94 + (RAND() * 0.05);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 4, 4, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备5: 注塑机-2
            SET v_avail_factor = 0.80 + (RAND() * 0.15);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.79 + (RAND() * 0.16);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.92 + (RAND() * 0.06);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 5, 5, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备6: 冲压机-1
            SET v_ideal_ct = 8.00;
            SET v_avail_factor = 0.87 + (RAND() * 0.11);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.85 + (RAND() * 0.12);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.97 + (RAND() * 0.025);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 6, 6, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备7: 冲压机-2
            SET v_avail_factor = 0.75 + (RAND() * 0.18);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.80 + (RAND() * 0.15);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.95 + (RAND() * 0.04);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 7, 6, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备8: 组装线-1
            SET v_ideal_ct = 20.00;
            SET v_avail_factor = 0.90 + (RAND() * 0.08);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.84 + (RAND() * 0.13);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.96 + (RAND() * 0.035);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 8, 7, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备9: 组装线-2
            SET v_avail_factor = 0.88 + (RAND() * 0.10);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.82 + (RAND() * 0.14);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.95 + (RAND() * 0.04);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 9, 7, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

            -- 设备10: 焊接机器人-1
            SET v_ideal_ct = 35.00;
            SET v_avail_factor = 0.84 + (RAND() * 0.13);
            SET v_actual_min = ROUND(v_planned_min * v_avail_factor, 2);
            SET v_perf_factor = 0.81 + (RAND() * 0.15);
            SET v_total_count = FLOOR((v_actual_min * 60 / v_ideal_ct) * v_perf_factor);
            SET v_qual_factor = 0.94 + (RAND() * 0.05);
            SET v_good_count = FLOOR(v_total_count * v_qual_factor);
            INSERT INTO production_record (record_date, shift, equipment_id, product_id, planned_duration_minutes, actual_run_minutes, total_count, good_count, defect_count, ideal_cycle_time)
            VALUES (v_date, '早班', 10, 8, v_planned_min, v_actual_min, v_total_count, v_good_count, v_total_count - v_good_count, v_ideal_ct);

        END IF;
        SET v_date = DATE_ADD(v_date, INTERVAL 1 DAY);
    END WHILE;
END //
DELIMITER ;

CALL generate_demo_data();
DROP PROCEDURE IF EXISTS generate_demo_data;

-- ============================================
-- 4. 停机记录数据
-- ============================================
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS generate_downtime_data()
BEGIN
    DECLARE v_date DATE DEFAULT '2026-01-01';
    DECLARE v_end_date DATE DEFAULT '2026-03-31';
    DECLARE v_rand DECIMAL(5,4);
    DECLARE v_duration INT;
    DECLARE v_eq_id INT;

    WHILE v_date <= v_end_date DO
        IF DAYOFWEEK(v_date) NOT IN (1, 7) THEN

            SET v_eq_id = 1;
            WHILE v_eq_id <= 10 DO
                SET v_rand = RAND();

                -- 约40%概率发生非计划停机
                IF v_rand < 0.40 THEN
                    SET v_duration = FLOOR(10 + RAND() * 60);

                    IF v_rand < 0.10 THEN
                        INSERT INTO downtime_record (record_date, shift, equipment_id, downtime_type, downtime_category, downtime_reason, start_time, end_time, duration_minutes)
                        VALUES (v_date, '早班', v_eq_id, 'unplanned', '机械故障', '主轴异常振动',
                            CONCAT(v_date, ' 08:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            CONCAT(v_date, ' 08:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            v_duration);
                    ELSEIF v_rand < 0.18 THEN
                        INSERT INTO downtime_record (record_date, shift, equipment_id, downtime_type, downtime_category, downtime_reason, start_time, end_time, duration_minutes)
                        VALUES (v_date, '早班', v_eq_id, 'unplanned', '电气故障', '传感器信号丢失',
                            CONCAT(v_date, ' 10:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            CONCAT(v_date, ' 10:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            v_duration);
                    ELSEIF v_rand < 0.26 THEN
                        INSERT INTO downtime_record (record_date, shift, equipment_id, downtime_type, downtime_category, downtime_reason, start_time, end_time, duration_minutes)
                        VALUES (v_date, '早班', v_eq_id, 'unplanned', '物料问题', '原材料供应不足',
                            CONCAT(v_date, ' 09:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            CONCAT(v_date, ' 09:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            v_duration);
                    ELSEIF v_rand < 0.33 THEN
                        INSERT INTO downtime_record (record_date, shift, equipment_id, downtime_type, downtime_category, downtime_reason, start_time, end_time, duration_minutes)
                        VALUES (v_date, '早班', v_eq_id, 'unplanned', '质量问题', '产品尺寸超差需调机',
                            CONCAT(v_date, ' 14:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            CONCAT(v_date, ' 14:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            v_duration);
                    ELSE
                        INSERT INTO downtime_record (record_date, shift, equipment_id, downtime_type, downtime_category, downtime_reason, start_time, end_time, duration_minutes)
                        VALUES (v_date, '早班', v_eq_id, 'unplanned', '换型调整', '产品换型准备',
                            CONCAT(v_date, ' 13:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            CONCAT(v_date, ' 13:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                            v_duration);
                    END IF;
                END IF;

                -- 约15%概率发生计划停机
                IF RAND() < 0.15 THEN
                    SET v_duration = FLOOR(30 + RAND() * 90);
                    INSERT INTO downtime_record (record_date, shift, equipment_id, downtime_type, downtime_category, downtime_reason, start_time, end_time, duration_minutes)
                    VALUES (v_date, '早班', v_eq_id, 'planned', '计划保养', '定期预防性维护',
                        CONCAT(v_date, ' 16:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                        CONCAT(v_date, ' 17:', LPAD(FLOOR(RAND()*59), 2, '0'), ':00'),
                        v_duration);
                END IF;

                SET v_eq_id = v_eq_id + 1;
            END WHILE;
        END IF;
        SET v_date = DATE_ADD(v_date, INTERVAL 1 DAY);
    END WHILE;
END //
DELIMITER ;

CALL generate_downtime_data();
DROP PROCEDURE IF EXISTS generate_downtime_data;
