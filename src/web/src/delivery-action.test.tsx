import {cleanup,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,it,expect,vi} from 'vitest';
import {DeliveryActionDialog} from './pages/catalog/DeliveryActionDialog';
afterEach(cleanup);
it('requires an explicit source and replaces the command when selection changes',()=>{
 const next=vi.fn(); const close=vi.fn();
 render(<DeliveryActionDialog changeId="shared-delivery" project="space / repo" label="开始开发" command="/opsx-apply" sources={[
 {id:'REQ-0001-first',type:'requirement',title:'首个来源'}, {id:'BUG-0002-second',type:'bug',title:'另一个来源'}
 ]} onClose={close} onContinue={next}/>);
 const proceed=screen.getByRole('button',{name:'开始开发 · 前往 Chat'}) as HTMLButtonElement;
 expect(proceed.disabled).toBe(true);
 fireEvent.change(screen.getByLabelText('选择来源事项'),{target:{value:'REQ-0001-first'}});
 expect(screen.getByText('/opsx-apply REQ-0001-first')).toBeTruthy();
 fireEvent.change(screen.getByLabelText('选择来源事项'),{target:{value:'BUG-0002-second'}});
 expect(screen.queryByText('/opsx-apply REQ-0001-first')).toBeNull();
 fireEvent.click(proceed);expect(next).toHaveBeenCalledWith('BUG-0002-second');
 fireEvent.keyDown(screen.getByRole('dialog'),{key:'Escape'});expect(close).toHaveBeenCalledOnce();
});
