import type { InspectionTask } from "../types/InspectionTask";

export const createDefaultInspectionTask = (overrides: Partial<InspectionTask> = {}): InspectionTask => ({
  id: 0,
  building_id: 0,
  inspector_id: null,
  plan_date: "",
  task_type: "HYDRANT",
  status: "PLANNED",
  checklist_version: "v1",
  finished_at: null,
  ...overrides,
});

export const createInspectionTaskForm = createDefaultInspectionTask;
export const createInspectionTaskResponse = createDefaultInspectionTask;
