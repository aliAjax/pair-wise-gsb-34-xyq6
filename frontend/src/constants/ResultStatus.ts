export const RESULT_NORMAL = "NORMAL";
export const RESULT_ABNORMAL = "ABNORMAL";

export const ResultStatus = [RESULT_NORMAL, RESULT_ABNORMAL] as const;
export type ResultStatus = (typeof ResultStatus)[number];

export const ResultStatusLabels: Record<ResultStatus, string> = {
  NORMAL: "合格",
  ABNORMAL: "异常",
};
