import type { RecoveryOperationResponse } from '../../api/generated/governance';
export type RunFacts = {status?:string; operation?:RecoveryOperationResponse|null; business?:boolean; rejected?:boolean; loading?:boolean; error?:boolean; hasBody?:boolean; truncated?:boolean; truncationReason?:string|null; partial?:boolean};
export function projectRunStatus(f:RunFacts) {
 const op=f.operation; const terminal=['completed','failed','stopped'].includes(f.status||'');
 let label=({queued:'排队中',connecting:'准备中',running:'执行中',stopping:'停止中',completed:'已完成',failed:'执行失败',stopped:'已停止',unknown:'结果待确认'} as Record<string,string>)[f.status||'']||'正在读取状态';
 let detail='';
 if(op?.state==='completed'||op?.historical_result==='verified') {
  label='已完成'; detail=(['failed','stopped'].includes(op.execution_terminal||'')||op.auto_retry_count>0||op.manual_count>0)?'经恢复完成 · 原执行终态保留':'成果已应用并核验';
  if(op.admission_state==='blocked' && op.admission_reason!=='stale_operation') detail+=' · 下一步暂不可执行';
  if(['running','stopping'].includes(f.status||'')) {label='结果待确认';detail='完成证明与当前占用矛盾，请重新核验';}
 } else if(f.status==='unknown') {label='结果待确认';detail='请查看本轮轨迹核实，不要重复发送命令';}
 else if(f.status==='stopping') label='停止中';
 else if(op && ['active','validating','applying','recovering'].includes(op.state) && ['validation','apply','readback'].includes(op.stage)) {label=({validation:'校验中',apply:'应用中',readback:'确认中'} as Record<string,string>)[op.stage]||'待处理';detail=['failed','stopped'].includes(op.execution_terminal||'')?'恢复中 · 原执行终态保留':'';}
 else if(!['failed','stopped'].includes(f.status||'') && terminal && f.business) {label=f.rejected?'待处理':op?.reason_code?'待处理':'结果待确认';detail=f.rejected?'结果未通过校验':op?.reason_code?'业务结果待核对':'结果待校验';}
 if(f.rejected&&!detail) detail='结果未通过校验';
 const notes:string[]=[];
 if(f.error) notes.push(f.status||op?'上次确认，更新失败；写操作暂不可用':'状态暂不可用');
 if(!f.status&&!op&&f.error) label='状态暂不可用';
 if(f.truncated) notes.push(['preview_limit','read_window'].includes(f.truncationReason||'')?'仅展示部分输出':['history_gap','invalid_payload'].includes(f.truncationReason||'')?'部分历史输出不可用':'输出内容不完整');
 else if(terminal&&f.partial) notes.push(f.hasBody?'未收到最终答复，以下为已保留的过程输出':'未收到最终答复');
 else if(['failed','stopped'].includes(f.status||'')) notes.push(f.hasBody?'已保留过程输出':'未收到可展示的输出');
 return {label,detail,notes};
}
