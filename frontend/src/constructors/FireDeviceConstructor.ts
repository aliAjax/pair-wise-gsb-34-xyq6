import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (overrides: Partial<FireDevice> = {}): FireDevice => ({
  id: 0,
  building_id: 0,
  device_code: "",
  device_type: "HYDRANT",
  floor: "1",
  location_desc: "",
  install_date: null,
  status: "NORMAL",
  next_maintenance_at: null,
  ...overrides,
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
