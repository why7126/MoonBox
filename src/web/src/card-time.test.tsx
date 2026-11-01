import {render,screen,cleanup} from '@testing-library/react';
import {afterEach,it,expect} from 'vitest';
import {CardTime} from './pages/catalog/CardTime';
afterEach(cleanup);
it.each([['updated','更新于'],['created','创建于'],['execution_completed','执行完成于'],['execution_started','执行开始于']] as const)('labels %s without inventing update time',(source,label)=>{
 render(<CardTime card_time="2026-10-31T20:15:00Z" card_time_source={source}/>);
 expect(screen.getByText(`${label} 26/11/01 04:15`)).toBeTruthy();
});
it('explains missing source instead of substituting legacy time',()=>{
 render(<CardTime card_time_source="missing" updatedAt="26/10/31 12:00"/>);
 expect(screen.getByText('时间未记录')).toBeTruthy();
});
it('preserves Issue and old API rendering',()=>{
 render(<CardTime updatedAt="26/10/31 12:00"/>);
 expect(screen.getByText('更新 26/10/31 12:00')).toBeTruthy();
});
it('does not render invalid projected values',()=>{
 render(<CardTime card_time="bad" card_time_source="updated"/>);
 expect(screen.getByText('时间未记录')).toBeTruthy();
});
