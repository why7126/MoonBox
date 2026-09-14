"""Verify the actual governance overlay mount policy in a disposable Compose project."""
import json,os,secrets,subprocess,tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[3]
def main():
    overlay=yaml.safe_load((ROOT/'deploy/docker-compose.governance.yml').read_text())['services']
    with tempfile.TemporaryDirectory(prefix='moonbox-governance-compose-',dir='/private/tmp') as folder:
        root=Path(folder);services={}
        for name in ('issues','iterations','openspec','docs','rules','private','data'):(root/name).mkdir()
        for name in ('backend','governance-controller'):
            declared=overlay[name]['volumes'];volumes=[]
            # Resolve only data roots; preserve the source overlay's read/write modes.
            for item in declared:
                if item.startswith('${MOONBOX_GOVERNANCE_HOST_STATE_ROOT}'):item=str(root/'private')+':/app/governance-state'
                elif item.startswith('./data/runtime/backend:'):item=str(root/'data')+':/app/data'
                elif item.startswith('./'):item=str(root/item.split(':')[0][2:])+':'+':'.join(item.split(':')[1:])
                volumes.append(item)
            if name=='backend':
                # These readonly mounts are inherited from the existing base Compose.
                for part in ('iterations','docs','rules'):volumes.append(str(root/part)+f':/app/governance/{part}:ro')
            services[name]={'image':'moonbox-backend:local','user':f'{os.getuid()}:{os.getgid()}','read_only':True,'cap_drop':['ALL'],'security_opt':['no-new-privileges:true'],'volumes':volumes,'network_mode':'none','entrypoint':['python','-c']}
        compose=root/'compose.yml';compose.write_text(yaml.safe_dump({'services':services}))
        project='mb-governance-probe-'+secrets.token_hex(4)
        def run(service,code):
            result=subprocess.run(['docker','compose','-p',project,'-f',str(compose),'run','--rm','--no-deps',service,code],capture_output=True,text=True)
            if result.returncode:raise RuntimeError(service+' mount validation failed')
            return json.loads(result.stdout.strip())
        try:
            api=run('backend',"from pathlib import Path; import json\np=Path('/app/governance/issues/probe.md')\ntry:p.write_text('unexpected');allowed=True\nexcept OSError:allowed=False\nassert not allowed;print(json.dumps({'source_write':allowed}))")
            writer=run('governance-controller',"from pathlib import Path; import json\np=Path('/app/governance/issues/probe.md');p.write_text('writer-only')\nassert not Path('/var/run/docker.sock').exists();print(json.dumps({'source_write':True,'socket_mounted':False}))")
            assert (root/'issues/probe.md').read_text()=='writer-only'
            report={'actual_overlay':True,'api':api,'controller':writer,'same_host_source':True,'temporary_project':True}
            destination=Path(os.environ.get('GOVERNANCE_PROBE_REPORT', str(ROOT/'openspec/changes/add-local-project-governance-loop/evidence/compose-permissions.json')));destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
        finally:subprocess.run(['docker','compose','-p',project,'-f',str(compose),'down','--remove-orphans'],capture_output=True)
if __name__=='__main__':main()
