"""Synthetic governance trees for lifecycle integration and live browser checks."""
from pathlib import Path
import yaml

class IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def dump(value, **kwargs):
    return yaml.dump(value, Dumper=IndentedDumper, **kwargs)


IDS = {'requirement': 'REQ-9091-lifecycle', 'bug': 'BUG-9091-lifecycle'}

def populate(root):
    changes=[]
    for kind, oid in IDS.items():
        plural='requirements' if kind=='requirement' else 'bugs'
        folder=root/'issues'/plural/'review'/oid;folder.mkdir(parents=True,exist_ok=True)
        change='fix-'+kind+'-lifecycle';changes.append(change)
        meta={'status':'in_sprint','iteration':'sprint-999','openspec_changes':[{'change_id':change,'status':'proposed'}], 'title':kind+' 生命周期验收', 'created_at':'2026-09-12 00:00:00','updated_at':'2026-09-12 00:00:00', 'severity' if kind=='bug' else 'priority':'medium' if kind=='bug' else 'P2'}
        fm='---\n'+dump(meta,allow_unicode=True,sort_keys=False)+'---\n'
        (folder/'trace.md').write_text(fm+'\n## 变更记录\n\n| 时间 | 事件 | 说明 |\n|---|---|---|\n')
        (folder/('bug.md' if kind=='bug' else 'requirement.md')).write_text(fm+'\n# 合成生命周期验收\n')
        (folder/'acceptance.md').write_text('---\nacceptance_status: not_started\n---\n# 验收\n')
        if kind=='bug':(folder/'root-cause.md').write_text('## 根因状态\nstatus: confirmed\n\n## 证据链\n| id | type | source | 摘要 |\n|---|---|---|---|\n| E1 | reproduction | 合成生命周期夹具 | 隔离复现 |\n')
        entry={'id':oid,'title':kind+' 生命周期验收','status':'in_sprint','path':str(folder.relative_to(root)),'iteration':'sprint-999','related_change':change,'severity' if kind=='bug' else 'priority':'medium' if kind=='bug' else 'P2'}
        (root/'issues'/plural/'_registry.yaml').write_text(dump({'next_id':9092,'entries':[entry]},allow_unicode=True,sort_keys=False))
        c=root/'openspec/changes'/change;c.mkdir(parents=True,exist_ok=True)
        (c/'trace.md').write_text('---\nstatus: proposed\niteration: sprint-999\n'+('bug_id' if kind=='bug' else 'requirement_id')+': '+oid+'\n---\n')
        (c/'tasks.md').write_text('## 实施\n\n- [ ] 1.1 合成任务\n- [ ] 1.2 合成验收\n')
        specs=c/'specs/lifecycle';specs.mkdir(parents=True,exist_ok=True);(specs/'spec.md').write_text('# 合成验收规格\n')
        for name in ('proposal.md','design.md','spec.md'):(c/name).write_text('# 合成验收\n')
    sprint=root/'iterations/change/sprint-999';sprint.mkdir(parents=True,exist_ok=True)
    (sprint/'sprint.yaml').write_text(dump({'sprint_id':'sprint-999','status':'planning','requirements':[IDS['requirement']],'bugs':[IDS['bug']],'changes':changes,'start_date':'2026-09-12 00:00:00','end_date':'2026-09-26 00:00:00','capacity_person_days':20},sort_keys=False))
    for name in ('sprint.md','release-note.md','acceptance-report.md'):(sprint/name).write_text('# 隔离生命周期验收\n')
