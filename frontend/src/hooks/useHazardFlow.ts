import { useMemo } from "react";
import {
  ASSIGNED,
  CLOSED,
  OPEN,
  RECTIFIED,
  REJECTED,
} from "../constants/RectifyStatus";
import { ROLE_MAINTAINER, ROLE_SUPERVISOR, type Role } from "../constants/Role";
import type { HazardTicket } from "../types/HazardTicket";

// 隐患流转可用动作：由角色 + 隐患当前状态共同决定，供按钮显隐与页面校验共用。
export function useHazardFlow(ticket: HazardTicket | null, role?: Role) {
  return useMemo(() => {
    const status = ticket?.rectify_status;
    const canAssign = !!ticket && role === ROLE_SUPERVISOR && (status === OPEN || status === REJECTED);
    const canRectify =
      !!ticket &&
      role === ROLE_MAINTAINER &&
      (status === ASSIGNED || status === REJECTED) &&
      ticket.owner_id !== null;
    const canReview = !!ticket && role === ROLE_SUPERVISOR && status === RECTIFIED;
    return {
      canAssign,
      canRectify,
      canReview,
      isClosed: status === CLOSED,
    };
  }, [ticket, role]);
}
