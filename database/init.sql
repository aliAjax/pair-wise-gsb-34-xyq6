-- 初始库占位脚本：应用启动时 SQLAlchemy create_all 会自动创建/对齐下列业务表。
-- 保留建表语句便于 DBA 预审表结构；字段与 backend/src/models/entities.py 对应。

CREATE TABLE IF NOT EXISTS app_user (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  password VARCHAR(128) NOT NULL,
  name VARCHAR(64) NOT NULL,
  role VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS building (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  campus VARCHAR(128) NOT NULL,
  floor_count INTEGER DEFAULT 1,
  fire_grade VARCHAR(32) DEFAULT '二级',
  manager_id INTEGER REFERENCES app_user(id),
  address_code VARCHAR(64) DEFAULT ''
);

CREATE TABLE IF NOT EXISTS fire_device (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL REFERENCES building(id),
  device_code VARCHAR(64) UNIQUE NOT NULL,
  device_type VARCHAR(32) NOT NULL,
  floor VARCHAR(16) DEFAULT '1',
  location_desc VARCHAR(255) DEFAULT '',
  install_date TIMESTAMP,
  status VARCHAR(32) DEFAULT 'NORMAL',
  next_maintenance_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inspection_task (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL REFERENCES building(id),
  inspector_id INTEGER REFERENCES app_user(id),
  plan_date TIMESTAMP,
  task_type VARCHAR(32) NOT NULL,
  status VARCHAR(32) DEFAULT 'PLANNED',
  checklist_version INTEGER DEFAULT 1,
  finished_at TIMESTAMP,
  reviewed_at TIMESTAMP,
  created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_checklist_item (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL REFERENCES inspection_task(id),
  device_id INTEGER NOT NULL REFERENCES fire_device(id),
  item_code VARCHAR(64) NOT NULL,
  item_name VARCHAR(255) NOT NULL,
  checklist_version INTEGER DEFAULT 1,
  UNIQUE (task_id, item_code)
);

CREATE TABLE IF NOT EXISTS inspection_result (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL REFERENCES inspection_task(id),
  device_id INTEGER NOT NULL REFERENCES fire_device(id),
  item_code VARCHAR(64) NOT NULL,
  result_status VARCHAR(16) NOT NULL,
  measured_value VARCHAR(255) DEFAULT '',
  photo_url VARCHAR(255) DEFAULT '',
  note TEXT DEFAULT '',
  submitted_by INTEGER REFERENCES app_user(id),
  submitted_at TIMESTAMP,
  UNIQUE (task_id, item_code)
);

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id SERIAL PRIMARY KEY,
  result_id INTEGER NOT NULL UNIQUE REFERENCES inspection_result(id),
  severity VARCHAR(16) DEFAULT 'MEDIUM',
  owner_id INTEGER REFERENCES app_user(id),
  deadline TIMESTAMP,
  rectify_status VARCHAR(16) DEFAULT 'OPEN',
  rectify_note TEXT DEFAULT '',
  created_at TIMESTAMP,
  rectified_at TIMESTAMP,
  closed_at TIMESTAMP,
  closed_by INTEGER REFERENCES app_user(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  actor_id INTEGER,
  actor_name VARCHAR(64) DEFAULT '',
  actor_role VARCHAR(32) DEFAULT '',
  action VARCHAR(64) NOT NULL,
  target_type VARCHAR(64) DEFAULT '',
  target_id VARCHAR(64) DEFAULT '',
  detail TEXT DEFAULT '',
  created_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inspection_task_building ON inspection_task(building_id);
CREATE INDEX IF NOT EXISTS idx_inspection_result_task ON inspection_result(task_id);
CREATE INDEX IF NOT EXISTS idx_hazard_ticket_status ON hazard_ticket(rectify_status);
