import { useEffect, useMemo, useState } from "react";
import { AlertBanner } from "../components/common/AlertBanner";
import { DeviceLocationCell } from "../components/common/DeviceLocationCell";
import { EmptyState } from "../components/common/EmptyState";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceType } from "../constants/DeviceType";
import { DeviceStatus, DeviceStatusLabels } from "../constants/DeviceStatus";
import { useBuildingStore } from "../stores/BuildingStore";
import { useFireDeviceStore } from "../stores/FireDeviceStore";
import { useInspectionResultStore } from "../stores/InspectionResultStore";
import { formatDate, formatDeviceStatus, formatDeviceType } from "../utils/formatters";
import { usePagination } from "../hooks/usePagination";

export function DevicesPage() {
  const buildings = useBuildingStore((state) => state.rows);
  const loadBuildings = useBuildingStore((state) => state.load);
  const devices = useFireDeviceStore((state) => state.rows);
  const loadDevices = useFireDeviceStore((state) => state.load);
  const results = useInspectionResultStore((state) => state.rows);
  const loadResults = useInspectionResultStore((state) => state.load);

  const [buildingId, setBuildingId] = useState<number | undefined>(undefined);
  const [deviceType, setDeviceType] = useState<string>("");
  const [floor, setFloor] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBuildings();
    loadDevices();
    loadResults();
  }, [loadBuildings, loadDevices, loadResults]);

  const buildingMap = useMemo(() => new Map(buildings.map((row) => [row.id, row.name])), [buildings]);
  const lastResultByDevice = useMemo(() => {
    const map = new Map<number, (typeof results)[number]>();
    for (const row of results) {
      const prev = map.get(row.device_id);
      if (!prev || row.id > prev.id) map.set(row.device_id, row);
    }
    return map;
  }, [results]);

  const filtered = useMemo(
    () =>
      devices.filter(
        (device) =>
          (buildingId === undefined || device.building_id === buildingId) &&
          (!deviceType || device.device_type === deviceType) &&
          (!floor || device.floor === floor) &&
          (!status || device.status === status),
      ),
    [devices, buildingId, deviceType, floor, status],
  );
  const { pageRows, page, pageCount, setPage } = usePagination(filtered, 10);

  return (
    <main className="page">
      <PageHeader title="消防设备台账" eyebrow="设备状态随巡检/隐患闭环自动重算" />
      {error && <AlertBanner tone="danger" onClose={() => setError(null)}>{error}</AlertBanner>}

      <section className="panel filter-bar">
        <label>
          楼栋
          <select value={buildingId ?? ""} onChange={(e) => setBuildingId(e.target.value ? Number(e.target.value) : undefined)}>
            <option value="">全部楼栋</option>
            {buildings.map((row) => (
              <option key={row.id} value={row.id}>{row.name}</option>
            ))}
          </select>
        </label>
        <label>
          设备类型
          <select value={deviceType} onChange={(e) => setDeviceType(e.target.value)}>
            <option value="">全部类型</option>
            {DeviceType.map((value) => (
              <option key={value} value={value}>{formatDeviceType(value)}</option>
            ))}
          </select>
        </label>
        <label>
          楼层
          <input placeholder="如 5" value={floor} onChange={(e) => setFloor(e.target.value)} />
        </label>
        <label>
          状态
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">全部状态</option>
            {DeviceStatus.map((value) => (
              <option key={value} value={value}>{DeviceStatusLabels[value]}</option>
            ))}
          </select>
        </label>
      </section>

      <section className="panel">
        {pageRows.length === 0 ? (
          <EmptyState title="没有符合筛选条件的设备" hint="调整楼栋、类型或状态筛选后重试" />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>设备 / 位置</th>
                <th>类型</th>
                <th>安装日期</th>
                <th>下次维保</th>
                <th>最近巡检</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {pageRows.map((device) => {
                const last = lastResultByDevice.get(device.id);
                return (
                  <tr key={device.id}>
                    <td>
                      <DeviceLocationCell device={device} buildingName={buildingMap.get(device.building_id)} />
                    </td>
                    <td>{formatDeviceType(device.device_type)}</td>
                    <td>{formatDate(device.install_date)}</td>
                    <td>{formatDate(device.next_maintenance_at)}</td>
                    <td>
                      {last ? (
                        <span className={last.result_status === "ABNORMAL" ? "danger-text" : "ok-text"}>
                          {last.result_status === "ABNORMAL" ? "异常" : "合格"} · {last.item_code}
                        </span>
                      ) : (
                        <span className="muted">暂无记录</span>
                      )}
                    </td>
                    <td><StatusBadge value={device.status} label={formatDeviceStatus(device.status)} /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
        <div className="pager">
          <button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>上一页</button>
          <span>第 {page} / {pageCount} 页 · 共 {filtered.length} 台</span>
          <button className="btn" disabled={page >= pageCount} onClick={() => setPage(page + 1)}>下一页</button>
        </div>
      </section>
    </main>
  );
}
