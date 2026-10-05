import type { FireDevice } from "../../types/FireDevice";
import { formatDeviceType } from "../../utils/formatters";

export function DeviceLocationCell({ device }: { device: FireDevice }) {
  return (
    <div className="device-cell">
      <strong>{device.device_code}</strong>
      <span>
        {device.building_name} · {device.floor} · {device.location_desc}
      </span>
      <em>{formatDeviceType(device.device_type)}</em>
    </div>
  );
}
