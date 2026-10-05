import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (overrides: Partial<FireDevice> = {}): FireDevice => ({
  id: 0,
  building_id: 0,
  building_name: "",
  device_code: "",
  device_type: "HYDRANT",
  floor: "1",
  location_desc: "",
  install_date: null,
  status: "NORMAL",
  next_maintenance_at: null,
  open_hazard_count: 0,
  ...overrides
});

export const createFireDeviceForm = (overrides: Partial<FireDevice> = {}) =>
  createDefaultFireDevice(overrides);
export const createFireDeviceResponse = createDefaultFireDevice;
