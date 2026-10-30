"""Build local acceptance overlays from installed, inspected images; no pulls."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    if os.environ.get('MOONBOX_PRODUCT_ACCEPTANCE_LIVE') != '1':
        raise SystemExit('explicit opt-in required')
    project = Path(__file__).resolve().parents[3]
    web = project / 'src/web/dist'
    if not (web / 'index.html').is_file():
        raise SystemExit('build src/web first')
    for tag in ('moonbox-backend:local', 'moonbox-verification:req0048-synthetic'):
        subprocess.run(['docker', 'image', 'inspect', tag], check=True, stdout=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory(prefix='moonbox-acceptance-images-') as folder:
        root = Path(folder)
        product = root / 'product'; product.mkdir()
        shutil.copytree(web, product / 'web')
        (product / 'Dockerfile').write_text('FROM moonbox-backend:local\nCOPY web /opt/moonbox-product-web\n')
        browser = root / 'browser'; browser.mkdir()
        shutil.copyfile(project / 'src/backend/container/verification_acceptance.cjs', browser / 'acceptance.cjs')
        (browser / 'Dockerfile').write_text('FROM moonbox-verification:req0048-synthetic\nCOPY acceptance.cjs /opt/moonbox-verification/acceptance.cjs\nENV MOONBOX_VERIFICATION_SYSTEM_CHROMIUM=1\n')
        for name, context in (('moonbox-backend:req0048-product', product), ('moonbox-verification:req0048-product', browser)):
            subprocess.run(['docker', 'build', '--pull=false', '--network=none', '-t', name, str(context)], check=True)


if __name__ == '__main__':
    main()
