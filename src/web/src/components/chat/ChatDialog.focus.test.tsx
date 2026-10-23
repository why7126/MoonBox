import {cleanup,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import {ChatDialog} from './ChatDialog';
afterEach(cleanup);

it('recaptures focus after a pending action disables the focused control',()=>{
 const close=vi.fn();
 render(<><button>外部控件</button><ChatDialog title="确认" testId="dialog" onClose={close} footer={<button>提交</button>}>准确版本</ChatDialog></>);
 const outside=screen.getByText('外部控件');outside.focus();
 fireEvent.keyDown(document,{key:'Tab'});
 expect(document.activeElement).toBe(screen.getByLabelText('关闭确认'));
 outside.focus();fireEvent.keyDown(document,{key:'Tab',shiftKey:true});
 expect(document.activeElement).toBe(screen.getByText('提交'));
 fireEvent.keyDown(document,{key:'Escape'});expect(close).toHaveBeenCalledOnce();
});

it('keeps Escape inside the dialog instead of triggering global menu focus',()=>{
 const globalEscape=vi.fn();document.addEventListener('keydown',globalEscape);
 const close=vi.fn();
 const {rerender}=render(<ChatDialog title="确认" testId="dialog" onClose={close}>版本</ChatDialog>);
 fireEvent.keyDown(screen.getByRole('dialog'),{key:'Escape'});
 expect(close).toHaveBeenCalledOnce();expect(globalEscape).not.toHaveBeenCalled();
 rerender(<ChatDialog title="确认" testId="dialog" busy onClose={close}>版本</ChatDialog>);
 fireEvent.keyDown(screen.getByRole('dialog'),{key:'Escape'});
 expect(close).toHaveBeenCalledOnce();expect(globalEscape).not.toHaveBeenCalled();
 document.removeEventListener('keydown',globalEscape);
});
