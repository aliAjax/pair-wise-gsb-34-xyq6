import type { InspectionResult } from "../types/InspectionResult";

export const createDefaultInspectionResult = (
  overrides: Partial<InspectionResult> = {}
): InspectionResult => ({
  id: 0,
  task_id: 0,
  device_id: 0,
  item_name: "",
  item_code: "",
  result_status: "NORMAL",
  measured_value: "",
  photo_url: "",
  note: "",
  submitted_by: null,
  submitted_by_name: "",
  submitted_at: null,
  device_code: "",
  building_name: "",
  hazard_id: null,
  ...overrides
});

export const createInspectionResultForm = (overrides: Partial<InspectionResult> = {}) =>
  createDefaultInspectionResult(overrides);
export const createInspectionResultResponse = createDefaultInspectionResult;
