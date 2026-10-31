"""Independent diagnostic probes; one missing capability does not stop dispatch."""
import os
import time
from app.verification.runner import probe_browser_image, RunnerUnavailable
from app.verification.python_probe import probe_image
from app.verification.acceptance_template import approved_template
from app.verification.acceptance_state import Conflict


def inspect_worker_capabilities(image):
    try:
        browser=probe_browser_image(image)
        if (browser['node_version']!=os.getenv('MOONBOX_VERIFICATION_NODE_VERSION') or
                browser['pnpm_version']!=os.getenv('MOONBOX_VERIFICATION_PNPM_VERSION')):
            raise RunnerUnavailable('verification_toolchain_mismatch')
    except (RunnerUnavailable,OSError) as error:
        browser={'reason_code':error.code if isinstance(error,RunnerUnavailable) else 'browser_probe_failed'}
    template_key = None
    try:
        template=approved_template()
        template_key=template.key
        result=probe_image(template.data['base']['python_image'])
        python={'template_key':template.key,'status':result['status'],'checked_at':time.time()}
    except (Conflict,RunnerUnavailable,OSError) as error:
        reason = error.code if isinstance(error, RunnerUnavailable) else 'python_test_runtime_unavailable'
        python={'template_key':template_key,'status':'unavailable','checked_at':time.time(),
                'reason_code':reason}
    return {'browser':browser,'python':python}
