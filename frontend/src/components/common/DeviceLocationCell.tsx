import type { ReactNode } from "react";
import type { FireDevice } from "../../types/FireDevice";
import { formatDeviceType } from "../../utils/formatters";

export function DeviceLocationCell({ device, buildingName }: { device?: FireDevice; buildingName?: string }) {
  if (!device) return <span className="muted">—</span>;
  return (
    <div className="loc-cell">
      <strong>{device.device_code}</strong>
      <span>
        {buildingName ? `${buildingName} · ` : ""}
        {formatDeviceType(device.device_type)} · {device.floor} 层 · {device.location_desc}
      </span>
    </div>
  );
}

export function DeviceText({ children }: { children: ReactNode }) {
  return <span className="loc-inline">{children}</span>;
}
