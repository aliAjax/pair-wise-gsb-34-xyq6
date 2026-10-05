-- fire-inspect 初始结构。应用启动时 SQLAlchemy 也会 create_all 补全，
-- 这里保持与 backend/src/models 完全一致，便于 DBA 审阅。

CREATE TABLE IF NOT EXISTS app_user (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  display_name VARCHAR(64) NOT NULL,
  role VARCHAR(32) NOT NULL,
  password_hash VARCHAR(128) NOT NULL
);

CREATE TABLE IF NOT EXISTS building (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  campus VARCHAR(128) NOT NULL,
  floor_count INTEGER NOT NULL DEFAULT 1,
  fire_grade VARCHAR(32) NOT NULL DEFAULT '二级',
  manager_id INTEGER,
  address_code VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS fire_device (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL,
  device_code VARCHAR(64) NOT NULL UNIQUE,
  device_type VARCHAR(32) NOT NULL,
  floor VARCHAR(16) NOT NULL,
  location_desc VARCHAR(128) NOT NULL,
  install_date DATE,
  status VARCHAR(32) NOT NULL DEFAULT 'NORMAL',
  next_maintenance_at DATE
);
CREATE INDEX IF NOT EXISTS ix_fire_device_building_id ON fire_device (building_id);
CREATE INDEX IF NOT EXISTS ix_fire_device_status ON fire_device (status);

CREATE TABLE IF NOT EXISTS inspection_task (
  id SERIAL PRIMARY KEY,
  building_id INTEGER NOT NULL,
  inspector_id INTEGER,
  plan_date VARCHAR(32) NOT NULL,
  task_type VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'PLANNED',
  checklist_version VARCHAR(16) NOT NULL DEFAULT 'v1',
  finished_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_inspection_task_building_id ON inspection_task (building_id);
CREATE INDEX IF NOT EXISTS ix_inspection_task_inspector_id ON inspection_task (inspector_id);
CREATE INDEX IF NOT EXISTS ix_inspection_task_status ON inspection_task (status);

CREATE TABLE IF NOT EXISTS checklist_template (
  id SERIAL PRIMARY KEY,
  task_type VARCHAR(32) NOT NULL,
  version VARCHAR(16) NOT NULL,
  item_code VARCHAR(64) NOT NULL,
  item_name VARCHAR(128) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_checklist_template_task_type ON checklist_template (task_type);

CREATE TABLE IF NOT EXISTS checklist_item (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  item_code VARCHAR(64) NOT NULL,
  item_name VARCHAR(128) NOT NULL,
  checklist_version VARCHAR(16) NOT NULL,
  deprecated BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS ix_checklist_item_task_id ON checklist_item (task_id);

CREATE TABLE IF NOT EXISTS inspection_result (
  id SERIAL PRIMARY KEY,
  task_id INTEGER NOT NULL,
  device_id INTEGER NOT NULL,
  item_code VARCHAR(64) NOT NULL,
  result_status VARCHAR(16) NOT NULL,
  measured_value VARCHAR(128),
  photo_url VARCHAR(256),
  note TEXT,
  checklist_version VARCHAR(16) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT now(),
  CONSTRAINT uq_result_task_item UNIQUE (task_id, item_code)
);
CREATE INDEX IF NOT EXISTS ix_inspection_result_task_id ON inspection_result (task_id);
CREATE INDEX IF NOT EXISTS ix_inspection_result_device_id ON inspection_result (device_id);

CREATE TABLE IF NOT EXISTS hazard_ticket (
  id SERIAL PRIMARY KEY,
  result_id INTEGER NOT NULL UNIQUE,
  device_id INTEGER NOT NULL,
  severity VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
  owner_id INTEGER,
  deadline DATE,
  rectify_status VARCHAR(16) NOT NULL DEFAULT 'OPEN',
  rectify_note TEXT,
  closed_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_result_id ON hazard_ticket (result_id);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_device_id ON hazard_ticket (device_id);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_owner_id ON hazard_ticket (owner_id);
CREATE INDEX IF NOT EXISTS ix_hazard_ticket_rectify_status ON hazard_ticket (rectify_status);

CREATE TABLE IF NOT EXISTS audit_log (
  id SERIAL PRIMARY KEY,
  actor VARCHAR(64) NOT NULL,
  action VARCHAR(128) NOT NULL,
  target_type VARCHAR(32) NOT NULL,
  target_id VARCHAR(32) NOT NULL,
  detail TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT now()
);
