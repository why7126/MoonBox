import type {RequirementCenterIssue} from '../../api/generated/governance';

export type CardTimeFacts = Pick<RequirementCenterIssue, 'card_time' | 'card_time_source'>;
const labels = {updated:'更新于',created:'创建于',execution_completed:'执行完成于',execution_started:'执行开始于'};
export function CardTime({card_time,card_time_source,updatedAt}: CardTimeFacts & {updatedAt?: string}) {
  let text = /^\d{2}\/\d{2}\/\d{2} \d{2}:\d{2}$/.test(updatedAt || '') ? `更新 ${updatedAt}` : '更新时间未知';
  if (card_time_source != null) {
    text = '时间未记录';
    if (card_time_source !== 'missing' && card_time && Number.isFinite(Date.parse(card_time))) {
      const parts = new Intl.DateTimeFormat('en-GB', {timeZone:'Asia/Shanghai',year:'2-digit',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date(card_time));
      const value = (key: string) => parts.find(part => part.type === key)?.value;
      text = `${labels[card_time_source]} ${value('year')}/${value('month')}/${value('day')} ${value('hour')}:${value('minute')}`;
    }
  }
  return <span className="rc-updated" data-time-source={card_time_source ?? 'legacy'}>{text}</span>;
}
