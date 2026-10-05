import { useMemo, useState } from "react";

export function usePagination<T>(rows: T[] = [], pageSize = 8) {
  const [page, setPage] = useState(1);
  const pageRows = useMemo(
    () => rows.slice((page - 1) * pageSize, page * pageSize),
    [rows, page, pageSize]
  );
  const pageCount = Math.max(1, Math.ceil(rows.length / pageSize));
  return { page, setPage, pageSize, pageRows, total: rows.length, pageCount };
}
