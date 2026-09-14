import { AlertCircle, LoaderCircle, Unplug } from "lucide-react";

export type ChatAvailability = "loading" | "unavailable" | "error" | "unknown";

const copy: Record<ChatAvailability, { title: string; detail: string }> = {
  loading: { title: "正在连接工作台", detail: "正在检查空间、仓库与执行服务。" },
  unavailable: { title: "执行服务尚未就绪", detail: "平台完成仓库与执行服务配置后，即可开始个人会话。" },
  error: { title: "暂时无法读取工作台", detail: "请稍后重新连接。已有会话不会因此被删除。" },
  unknown: { title: "运行状态待确认", detail: "确认原运行状态前无法再次发送，请保留当前会话。" },
};

export function ChatStatus({ availability }: { availability: ChatAvailability }) {
  const Icon = availability === "loading" ? LoaderCircle : availability === "unavailable" ? Unplug : AlertCircle;
  return (
    <div className="chat-status" data-testid="chat-status" data-state={availability} role={availability === "error" ? "alert" : "status"}>
      <span className="chat-status-icon"><Icon size={24} strokeWidth={1.5} aria-hidden="true" /></span>
      <h2>{copy[availability].title}</h2>
      <p>{copy[availability].detail}</p>
    </div>
  );
}
