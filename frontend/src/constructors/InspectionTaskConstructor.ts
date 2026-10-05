import type { ChecklistItem, InspectionTask } from "../types/InspectionTask";

export const createDefaultChecklistItem = (
  overrides: Partial<ChecklistItem> = {}
): ChecklistItem => ({
  id: 0,
  device_id: 0,
  item_code: "",
  item_name: "",
  checklist_version: 1,
  result_status: null,
  measured_value: "",
  photo_url: "",
  note: "",
  submitted_by: null,
  submitted_by_name: "",
  submitted_at: null,
  hazard_id: null,
  hazard_status: null,
  ...overrides
});

export const createDefaultInspectionTask = (
  overrides: Partial<InspectionTask> = {}
): InspectionTask => ({
  id: 0,
  building_id: 0,
  building_name: "",
  inspector_id: null,
  inspector_name: "",
  plan_date: "",
  task_type: "HYDRANT",
  status: "PLANNED",
  checklist_version: 1,
  finished_at: null,
  reviewed_at: null,
  created_at: "",
  total_items: 0,
  submitted_items: 0,
  abnormal_items: 0,
  open_hazard_count: 0,
  items: [],
  ...overrides
});

export const createInspectionTaskForm = (overrides: Partial<InspectionTask> = {}) =>
  createDefaultInspectionTask(overrides);
export const createInspectionTaskResponse = createDefaultInspectionTask;
