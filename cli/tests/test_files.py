import pytest
from pathlib import Path
from cli.utils import files


class TestEnsureDir:
    def test_creates_directory(self, tmp_path):
        target = tmp_path / "novo" / "diretorio"
        files.ensure_dir(target)
        assert target.is_dir()

    def test_idempotent(self, tmp_path):
        target = tmp_path / "dir"
        files.ensure_dir(target)
        files.ensure_dir(target)
        assert target.is_dir()


class TestBumpVersion:
    def test_bumps_patch(self):
        assert files.bump_version('1.0.0') == '1.0.1'
        assert files.bump_version('1.2.3') == '1.2.4'
        assert files.bump_version('0.0.9') == '0.0.10'

    def test_returns_unchanged_for_invalid_format(self):
        assert files.bump_version('1.0') == '1.0'
        assert files.bump_version('abc') == 'abc'
        assert files.bump_version('') == ''
