import * as api from '../../../api/generated/capture';
import { readAccessToken } from '../../workbench/workbenchAccount';
import { GovernanceError, type Project } from '../../workbench/governanceApi';
export type { Candidate, CapabilitiesResult, ConfirmationResult, DraftContent, DraftResult, MaterialResult, SourceResult, OrganizeResult } from '../../../api/generated/capture';

type Wire = { status: number; headers: Headers; data: unknown };
async function unwrap<T>(promise: Promise<Wire>): Promise<T> {
  const reply = await promise;
  const body = reply.data as { data?: T; message?: string; code?: number } | null;
  if (reply.status < 200 || reply.status >= 300 || !body || !('data' in body)) {
    const reason = body?.data as { kind?: string } | null | undefined;
    throw new GovernanceError(body?.message || `采集请求失败（${reply.status}）`, reply.status, body?.code, reason?.kind, reply.headers.get('X-Request-ID') || undefined);
  }
  return body.data as T;
}

/** Scope and cancellation are fixed per workspace; callers replace this on project changes. */
export function captureApi(project: Project, signal: AbortSignal) {
  const scope = { space_id: project.space_id, repository_id: project.repository_id };
  const trace = crypto.randomUUID();
  const options = (behavior = false): RequestInit => {
    const token = readAccessToken();
    return { signal, headers: {
      Accept: 'application/json', 'X-Chat-Client': 'web',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(behavior ? { 'X-Behavior-Event-ID': crypto.randomUUID(), 'X-Behavior-Trace-ID': trace } : {}),
    } };
  };
  return {
    create: () => unwrap<api.DraftResult>(api.createApiV1RequirementCenterCaptureDraftsPost(scope, options())),
    list: (page = 1) => unwrap<api.DraftList>(api.listingApiV1RequirementCenterCaptureDraftsGet({ ...scope, page, page_size: 20 }, options())),
    get: (id: string) => unwrap<api.DraftResult>(api.getApiV1RequirementCenterCaptureDraftsDraftIdGet(id, scope, options())),
    save: (id: string, version: number, content: api.DraftContent) => unwrap<api.DraftResult>(api.saveApiV1RequirementCenterCaptureDraftsDraftIdPatch(id, { ...content, expected_revision: version }, scope, options(true))),
    remove: (id: string, version: number) => unwrap<api.DeleteResult>(api.removeApiV1RequirementCenterCaptureDraftsDraftIdDelete(id, { expected_revision: version }, scope, options())),
    upload: (id: string, file: File) => unwrap<api.MaterialResult>(api.uploadApiV1RequirementCenterCaptureDraftsDraftIdMaterialsPost(id, { file }, scope, options(true))),
    organize: (id: string, version: number) => unwrap<api.OrganizeResult>(api.organizeApiV1RequirementCenterCaptureDraftsDraftIdOrganizePost(id, { expected_revision: version }, scope, options(true))),
    organized: (id: string, task: string) => unwrap<api.OrganizeResult>(api.organizedApiV1RequirementCenterCaptureDraftsDraftIdOrganizeTasksTaskIdGet(id, task, scope, options())),
    confirm: (id: string, version: number, key: string) => unwrap<api.ConfirmationResult>(api.confirmApiV1RequirementCenterCaptureDraftsDraftIdConfirmationsPost(id, { expected_revision: version, idempotency_key: key }, scope, options(true))),
    status: (task: string) => unwrap<api.ConfirmationResult>(api.statusApiV1RequirementCenterCaptureConfirmationsTaskIdGet(task, scope, options())),
    retry: (task: string) => unwrap<api.ConfirmationResult>(api.retryApiV1RequirementCenterCaptureConfirmationsTaskIdRetriesPost(task, scope, options(true))),
    source: (issue: string) => unwrap<api.SourceResult>(api.sourceApiV1RequirementCenterCaptureSourcesIssueIdGet(issue, scope, options())),
    capabilities: () => unwrap<api.CapabilitiesResult>(api.capabilitiesApiV1RequirementCenterCaptureCapabilitiesGet(scope, options())),
    image: async (id: string): Promise<Blob> => {
      const reply = await fetch(api.getImageApiV1RequirementCenterCaptureMaterialsMediaIdContentGetUrl(id, scope), options());
      if (!reply.ok) throw new GovernanceError('图片暂不可读，请重试', reply.status);
      return reply.blob();
    },
  };
}
