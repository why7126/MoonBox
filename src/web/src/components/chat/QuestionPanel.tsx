import { useEffect, useRef, useState } from 'react';
import type { QuestionRead, QuestionListRead, QuestionAnswerValue } from '../../api/generated/chat';
import { chatRequest, normalizeChatError } from './chatApi';
import { readValidFrontendSession } from '../../pages/home/frontendSession';

const labels: Record<string, string> = {
  pending: '等待你的回答', answer_received: '答案已收到，等待回传', delivering: '答案回传中',
  delivered: '答案已发送至原任务', expired: '问题已过期，答案未发送',
  cancelled: '原任务已停止，无法继续回答', unrecoverable: '无法确认原请求，请先核对任务状态',
};

export function QuestionCard({ question, onSubmit }: { question: QuestionRead;
  onSubmit: (answers: Record<string, QuestionAnswerValue>, key: string) => Promise<void> }) {
  const [answers, setAnswers] = useState<Record<string, QuestionAnswerValue>>({});
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  const attempt = useRef<{ payload: string; key: string }>();
  const errorRef = useRef<HTMLParagraphElement>(null);
  const writable = question.status === 'pending';
  const valid = question.questions.every(q => !!answers[q.id]?.option_id || !!answers[q.id]?.text?.trim());
  const change = (id: string, value: QuestionAnswerValue) => {
    setAnswers(current => ({ ...current, [id]: { ...current[id], ...value } }));
    setError('');
  };
  const submit = async () => {
    if (!writable || busy || !valid) return;
    const payload = Object.fromEntries(question.questions.map(q => [q.id, answers[q.id] || {}]));
    const serialized = JSON.stringify(payload);
    if (!attempt.current || attempt.current.payload !== serialized)
      attempt.current = { payload: serialized, key: crypto.randomUUID() };
    setBusy(true); setError('');
    try { await onSubmit(payload, attempt.current.key); }
    catch (e) { setError((normalizeChatError(e) instanceof Error ? (normalizeChatError(e) as Error).message : '请求未完成，请重试')); requestAnimationFrame(() => errorRef.current?.focus()); }
    finally { setBusy(false); }
  };
  return <section className="chat-question-card" data-testid="question-card" aria-label="任务补充问题">
    <h3>需要你补充信息</h3>
    <p className="chat-question-status" role="status" data-testid="question-status">{busy ? '正在提交回答…' : labels[question.status]}</p>
    <p className="chat-question-help">回答会送回原任务。答案已发送不代表任务已经完成。</p>
    {question.questions.map(q => <fieldset key={q.id} disabled={!writable || busy}>
      <legend>{q.question}</legend>
      {q.options.map(option => <label className="chat-question-option" key={option.id} data-testid="question-option">
        <input type="radio" name={`${question.id}-${q.id}`} value={option.id} checked={answers[q.id]?.option_id === option.id}
          onChange={() => change(q.id, { option_id: option.id })}/>
        <span>{option.label}<small>{option.description}</small></span>
      </label>)}
      <label className="chat-question-text">补充说明（可填写其他选择，请勿填写密码或凭证）
        <textarea data-testid="question-text" maxLength={4000} value={answers[q.id]?.text || ''}
          onChange={e => change(q.id, { text: e.target.value })} rows={3}/>
      </label>
    </fieldset>)}
    {error && <p role="alert" tabIndex={-1} ref={errorRef} className="chat-error">{error}</p>}
    {writable && <button type="button" className="chat-question-submit" data-testid="question-submit"
      disabled={busy || !valid} onClick={() => void submit()}>{busy ? '正在提交…' : '提交回答'}</button>}
  </section>;
}

export function QuestionPanel({ turnId }: { turnId: string }) {
  const [items, setItems] = useState<QuestionRead[]>([]), [error, setError] = useState('');
  const [retry, setRetry] = useState(0);
  const identity = readValidFrontendSession()?.access_token;
  const generation = useRef(0);
  useEffect(() => {
    const current = ++generation.current;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout> | undefined;
    let inflight = false, terminal = false;
    setItems([]); setError('');
    const read = async () => {
      if (controller.signal.aborted || inflight || document.hidden || terminal) return;
      inflight = true;
      try {
        const data = await chatRequest<QuestionListRead>(`/turns/${encodeURIComponent(turnId)}/questions`, { signal: controller.signal });
        if (controller.signal.aborted || current !== generation.current || readValidFrontendSession()?.access_token !== identity) return;
        setItems(previous => data.items.map(item => {
          const prior = previous.find(row => row.id === item.id);
          return item.status === 'pending' && prior && prior.status !== 'pending' ? prior : item;
        })); setError('');
        terminal = !['queued', 'connecting', 'running', 'stopping'].includes(data.turn_status);
      } catch (e) {
        if (!controller.signal.aborted && current === generation.current) {
          setItems([]); setError((normalizeChatError(e) instanceof Error ? (normalizeChatError(e) as Error).message : '请求未完成，请重试')); terminal = true;
        }
      } finally {
        inflight = false;
        if (!controller.signal.aborted && !terminal) timer = setTimeout(read, 1500);
      }
    };
    const visible = () => { if (!document.hidden) { clearTimeout(timer); void read(); } };
    void read(); document.addEventListener('visibilitychange', visible);
    return () => { ++generation.current; controller.abort(); clearTimeout(timer); document.removeEventListener('visibilitychange', visible); };
  }, [turnId, identity, retry]);
  const submit = async (question: QuestionRead, answers: Record<string, QuestionAnswerValue>, key: string) => {
    const current = generation.current;
    const updated = await chatRequest<QuestionRead>(`/turns/${encodeURIComponent(turnId)}/questions/${encodeURIComponent(question.id)}/answers`,
      { method: 'POST', body: JSON.stringify({ version: question.version, idempotency_key: key, answers }) });
    if (current === generation.current && readValidFrontendSession()?.access_token === identity) setItems(rows => rows.map(row => row.id === updated.id ? updated : row));
  };
  return <div className="chat-question-list">
    {error && <p role="alert" className="chat-error">问题状态读取失败：{error} <button onClick={() => setRetry(v => v + 1)}>重试</button></p>}
    {items.map(question => <QuestionCard key={`${turnId}-${question.id}-${identity}`} question={question} onSubmit={(answers, key) => submit(question, answers, key)}/>)}
  </div>;
}
