"""Serve the real MoonBox API and compiled web UI in the isolated container."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('acceptance_product_adapter', Path(__file__).with_name('acceptance_product_adapter.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.application()
