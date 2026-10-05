export const ResultStatus = ["NORMAL", "ABNORMAL"] as const;
export type ResultStatus = (typeof ResultStatus)[number];

export const ResultStatusText: Record<ResultStatus, string> = {
  NORMAL: "正常",
  ABNORMAL: "异常"
};
