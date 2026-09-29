from pathlib import Path
import pytest
from app.governance.titles import project_title, read_title, validate_document


def doc(title):
    return f'---\ntitle: {title}\n---\n# {title}\n'


@pytest.mark.parametrize('stage', ['capture','planning','review-ready','approved','sprint-planning','ready-dev','development','acceptance','done'])
@pytest.mark.parametrize('kind', ['requirement.md','bug.md'])
def test_stage_source(tmp_path,stage,kind):
    main=tmp_path/kind;main.write_text(doc('主文档业务主题'))
    proposal=tmp_path/'proposal.md';proposal.write_text(doc('提案交付业务主题'))
    title,source,_=project_title(stage,'采集业务主题','REQ-0001',main,proposal)
    expected='采集业务主题' if stage=='capture' else '提案交付业务主题' if stage in {'ready-dev','development','acceptance','done'} else '主文档业务主题'
    assert title==expected


@pytest.mark.parametrize('value', ['','English','REQ-0016','BUG-0016修复追溯','Change 实施与验证记录','任务清单','<中文标题>'])
def test_bad_titles(tmp_path,value):
    p=tmp_path/'proposal.md';p.write_text(doc(value))
    assert read_title(p) is None
    assert validate_document(p.read_text())


def test_fallback_and_legacy(tmp_path):
    p=tmp_path/'bug.md';p.write_text('# 中文历史业务主题\n')
    assert project_title('acceptance','注册表主题','BUG-1',p)[0]=='中文历史业务主题'
    p.write_text('---\ntitle: English\n---\n# 中文历史业务主题\n')
    assert project_title('acceptance','注册表主题','BUG-1',p)[0]=='注册表主题'
    assert project_title('acceptance','English','BUG-1',p)[0]=='BUG-1'


@pytest.mark.parametrize('name', ['capture','trace','user-stories','review','requirement','bug','business-flow','acceptance','root-cause','workaround','proposal','design','tasks','spec'])
def test_all_documents(name):
    title='需求中心业务主题'+name
    assert not validate_document(doc(title))
    assert validate_document(doc(title).replace('# '+title,'# 其他业务主题'))
    assert validate_document('# '+title)


def test_fenced_heading_not_document_title():
    assert not validate_document(doc('业务主题说明')+'\n```md\n# 示例标题\n```\n')
