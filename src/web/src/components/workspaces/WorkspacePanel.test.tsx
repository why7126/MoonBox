import {act, cleanup, fireEvent, render, screen} from '@testing-library/react';
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {WorkspacePanel} from './WorkspacePanel';
import {governanceRequest, GovernanceError} from '../workbench/governanceApi';
vi.mock('../workbench/governanceApi', async original => {
  const actual = await original<typeof import('../workbench/governanceApi')>();
  return {...actual, governanceRequest: vi.fn()};
});
beforeEach(() => vi.mocked(governanceRequest).mockImplementation(async url => String(url).includes('merge-capability') ? {can_operate_sprint:false,can_prepare:false,can_confirm:false} : {items:[]}));
afterEach(()=>{cleanup(); vi.resetAllMocks();});
const item = (id:string) => ({id,space_id:'space',repository_id:'repo',purpose:'main',base_commit:'a'.repeat(40),lifecycle:'ready',revision:1});

it('discards late responses when switching repository', async()=>{
  let late!: (value: unknown)=>void;
  vi.mocked(governanceRequest).mockImplementationOnce(()=>new Promise(resolve=>{late=resolve;}));
  vi.mocked(governanceRequest).mockResolvedValueOnce({items:[item('new-workspace')]});
  const {rerender}=render(<WorkspacePanel spaceId="space" repositoryId="old" onClose={()=>{}} />);
  rerender(<WorkspacePanel spaceId="space" repositoryId="new" onClose={()=>{}} />);
  await screen.findByRole('option', {name: '主工作区 · new-work'});
  await act(async()=>{late({items:[item('old-workspace')]});});
  expect(screen.queryByText('old-workspace')).toBeNull();
  expect((screen.getByTestId('workspace-picker') as HTMLSelectElement).value).toBe('new-workspace');
});

it('clears identity on permission revocation and remains closable', async()=>{
  vi.mocked(governanceRequest).mockResolvedValueOnce({items:[item('private-workspace')]});
  const close=vi.fn();
  render(<WorkspacePanel spaceId="space" repositoryId="repo" onClose={close} />);
  await screen.findByRole('option', {name: '主工作区 · private-'});
  vi.mocked(governanceRequest).mockRejectedValueOnce(new GovernanceError('无权限',403));
  fireEvent.click(screen.getByText('刷新'));
  await screen.findByText('当前没有访问此仓库的权限。');
  expect(screen.queryByText('private-workspace')).toBeNull();
  expect((screen.getByTestId('merge-confirm') as HTMLButtonElement).disabled).toBe(true);
  fireEvent.keyDown(screen.getByRole('dialog'),{key:'Escape'});
  expect(close).toHaveBeenCalledOnce();
});

it('keeps nested actions inside the workspace and closes only the top dialog', async()=>{
  vi.mocked(governanceRequest).mockResolvedValueOnce({items:[item('main-workspace')],can_create_development:true,can_register_main:true});
  const close=vi.fn();
  render(<WorkspacePanel spaceId="space" repositoryId="repo" onClose={close} />);
  await screen.findByRole('option',{name:'主工作区 · main-wor'});
  fireEvent.click(screen.getByTestId('workspace-create'));
  const field=screen.getByRole('textbox',{name:'独立交付 Change'});
  fireEvent.pointerDown(field);
  expect(screen.getByRole('dialog',{name:'创建独立工作区'})).toBeTruthy();
  fireEvent.keyDown(field,{key:'Escape'});
  expect(screen.queryByRole('dialog',{name:'创建独立工作区'})).toBeNull();
  expect(close).not.toHaveBeenCalled();
  fireEvent.click(screen.getByTestId('workspace-create'));
  fireEvent.pointerDown(document.body);
  expect(screen.queryByRole('dialog',{name:'创建独立工作区'})).toBeNull();
  expect(close).not.toHaveBeenCalled();
});
