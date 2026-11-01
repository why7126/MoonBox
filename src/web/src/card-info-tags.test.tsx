import React from 'react';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import {CardInfoTags} from './pages/catalog/CardInfoTags';
afterEach(cleanup);
it('renders ordered root and explicit zero without triggering the card',()=>{
 const open=vi.fn(),card=vi.fn();render(<div onClick={card}><CardInfoTags facts={{type:'bug',root_cause_state:'confirmed',estimate_status:'available',estimated_person_days:0}} onRootCause={open}/></div>);
 const root=screen.getByRole('button',{name:'根因已确认'});expect(root.nextElementSibling?.textContent).toContain('0');fireEvent.click(root);expect(open).toHaveBeenCalledOnce();expect(card).not.toHaveBeenCalled();
});
it('hides unknown fields and never shows roots for requirements',()=>{
 render(<CardInfoTags facts={{type:'requirement',root_cause_state:'confirmed',estimated_person_days:3}} onRootCause={()=>{}}/>);expect(screen.queryByTestId('root-cause-tag')).toBeNull();expect(screen.queryByTestId('person-days-tag')).toBeNull();
});
it('shows conflicts as pending and preserves decimals',()=>{
 render(<CardInfoTags facts={{type:'bug',root_cause_state:'pending',root_cause_reason:'conflict',estimate_status:'available',estimated_person_days:.5}} onRootCause={()=>{}}/>);expect(screen.getByRole('button').title).toContain('需核对');expect(screen.getByTestId('person-days-tag').textContent).toContain('0.5');
});

it.each([[0,'S'],[.5,'S'],[1,'S'],[1.01,'M'],[3,'M'],[3.01,'L'],[5,'L'],[5.01,'XL'],[10,'XL'],[10.01,'XXL'],[13,'XXL']])('classifies effort %s as %s', (days,size)=>{
 render(<CardInfoTags facts={{type:'requirement',estimate_status:'available',estimated_person_days:days as number}} onRootCause={()=>{}}/>);
 const tag=screen.getByTestId('person-days-tag');expect(tag.textContent?.trim()).toBe(`${size}·${days}人天`);expect(tag.className).toContain(`rc-effort-${String(size).toLowerCase()}`);expect(tag.title).toBe(`${size} · 预估开发${days}人天`);expect(tag.tagName).toBe('SPAN');
});
it.each([null,undefined,-1,NaN,Infinity,'3',true])('hides invalid effort %s',days=>{
 render(<CardInfoTags facts={{type:'bug',estimate_status:'available',estimated_person_days:days as number}} onRootCause={()=>{}}/>);expect(screen.queryByTestId('person-days-tag')).toBeNull();
});
it('identifies the source estimate without presenting it as actual time',()=>{
 render(<CardInfoTags facts={{type:'change',estimate_status:'available',estimated_person_days:3,estimate_source_issue_id:'BUG-0070-sample'}} onRootCause={()=>{}}/>);
 const tag=screen.getByTestId('person-days-tag');
 expect(tag.textContent).toBe('M·3人天');
 expect(tag.title).toContain('引用来源 BUG-0070-sample');
 expect(tag.title).toContain('非实际耗时');
});
