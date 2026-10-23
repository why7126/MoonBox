/** Navigation decisions are independent from card rendering and modal layout. */
export type GovernanceSessionResult = {
  object_id?: string;
  object_type?: string;
  conversation_id: string | null;
  view_conversation_id?: string | null;
  can_send?: boolean;
  execution_state?: string;
  reason_code?: string | null;
  prompt?: string;
};

export type GovernanceSessionDecision = {
  conversationId: string | null;
  replaceDraft: boolean;
  message: string;
};

export function governanceSessionDecision(result: GovernanceSessionResult): GovernanceSessionDecision {
  if (result.can_send === false) {
    return {
      conversationId: result.view_conversation_id || null,
      replaceDraft: false,
      message: result.execution_state === "needs_review"
        ? "结果待核对，已产生的文档会保留"
        : "对象正在执行，请查看当前执行",
    };
  }
  return {
    conversationId: result.conversation_id || null,
    replaceDraft: Boolean(result.conversation_id),
    message: result.conversation_id ? "" : "对象会话暂不可用，请刷新后重试",
  };
}
