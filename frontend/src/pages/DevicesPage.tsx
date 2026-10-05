import { useEffect, useMemo, useState } from "react";
import { useBuildingStore } from "../stores/BuildingStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { useInspectionResultStore } from "../stores/InspectionResultStore";
import { DeviceLocationCell } from "../components/common/DeviceLocationCell";
import { EmptyState } from "../components/common/EmptyState";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceType } from "../constants/DeviceType";
import { formatDate, formatDeviceType } from "../utils/formatters";

export function DevicesPage() {
  const buildings = useBuildingStore((state) => state.rows);
  const loadBuildings = useBuildingStore((state) => state.load);
  const devices = useFireDeviceStore((state) => state.rows);
  const loadDevices = useFireDeviceStore((state) => state.load);
  const results = useInspectionResultStore((state) => state.rows);
  const loadResults = useInspectionResultStore((state) => state.load);

  const [buildingId, setBuildingId] = useState<number | undefined>(undefined);
  const [deviceType, setDeviceType] = useState<string>("");
  const [selectedDevice, setSelectedDevice] = useState<number | null>(null);

  useEffect(() => {
    void loadBuildings();
  }, [loadBuildings]);

  useEffect(() => {
    void loadDevices(buildingId);
  }, [buildingId, loadDevices]);

  useEffect(() => {
    if (selectedDevice) void loadResults({ deviceId: selectedDevice });
  }, [selectedDevice, loadResults]);

  const filtered = useMemo(
    () => devices.filter((d) => (deviceType ? d.device_type === deviceType : true)),
    [devices, deviceType]
  );

  const deviceResults = useMemo(
    () => results.filter((r) => r.device_id === selectedDevice).slice(0, 10),
    [results, selectedDevice]
  );

  return (
    <main className="page">
      <section className="page-head">
        <div>
          <p className="eyebrow">fire-inspect</p>
          <h1>消防设备台账</h1>
        </div>
      </section>

      <section className="filter-bar panel">
        <label>
          楼栋
          <select
            value={buildingId ?? ""}
            onChange={(e) => setBuildingId(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">全部楼栋</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>
        </label>
        <label>
          设备类型
          <select value={deviceType} onChange={(e) => setDeviceType(e.target.value)}>
            <option value="">全部类型</option>
            {DeviceType.map((t) => (
              <option key={t} value={t}>{formatDeviceType(t)}</option>
            ))}
          </select>
        </label>
      </section>

      <section className="workbench">
        <div className="panel wide">
          <h2>设备列表（{filtered.length}）</h2>
          {filtered.length === 0 ? <EmptyState title="该筛选下暂无设备" /> : (
            <div className="table">
              {filtered.map((device) => (
                <article
                  className={`row clickable ${selectedDevice === device.id ? "selected" : ""}`}
                  key={device.id}
                  onClick={() => setSelectedDevice(device.id)}
                >
                  <DeviceLocationCell device={device} />
                  <StatusBadge value={device.status} />
                  <span className={device.open_hazard_count > 0 ? "text-danger" : "muted"}>
                    未结隐患 {device.open_hazard_count}
                  </span>
                  <span className="muted">下次维保 {formatDate(device.next_maintenance_at)}</span>
                </article>
              ))}
            </div>
          )}
        </div>
        <div className="panel">
          <h2>历史巡检结果</h2>
          {selectedDevice === null ? (
            <EmptyState title="点击左侧设备查看历史结果" />
          ) : deviceResults.length === 0 ? (
            <EmptyState title="该设备暂无巡检记录" />
          ) : (
            <ul className="history-list">
              {deviceResults.map((r) => (
                <li key={r.id}>
                  <div>
                    <strong>{r.item_name}</strong>
                    <span className="muted">{formatDate(r.submitted_at)} · {r.submitted_by_name}</span>
                  </div>
                  <StatusBadge value={r.result_status} />
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </main>
  );
}
