import sys
from pathlib import Path


TOOLKIT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLKIT_DIR))

from port_cleaner import collect_from_root, port_root_exclusion


def test_nested_port_excludes_its_root_directory(tmp_path):
    nested_root = tmp_path / "nested"
    port = nested_root / "port"
    port.mkdir(parents=True)
    loose_dir = tmp_path / "loose"
    loose_dir.mkdir()

    excluded = {port_root_exclusion(tmp_path, port)}
    targets = collect_from_root(tmp_path, excluded, set())

    assert nested_root not in targets
    assert loose_dir in targets


def test_external_port_needs_no_root_exclusion(tmp_path):
    assert port_root_exclusion(tmp_path, tmp_path.parent / "external-port") is None
