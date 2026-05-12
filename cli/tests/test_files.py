import pytest
from pathlib import Path
from cli.utils import files


@pytest.fixture
def src_file(tmp_path):
    f = tmp_path / "template.md"
    f.write_text("# Template\n\nConteúdo de exemplo.\n")
    return f


class TestCopyTemplate:
    def test_copies_file(self, src_file, tmp_path):
        dest = tmp_path / "dest" / "output.md"
        files.copy_template(src_file, dest)
        assert dest.exists()
        assert dest.read_text() == src_file.read_text()

    def test_creates_parent_dirs(self, src_file, tmp_path):
        dest = tmp_path / "a" / "b" / "c" / "output.md"
        files.copy_template(src_file, dest)
        assert dest.exists()

    def test_raises_when_dest_exists_without_overwrite(self, src_file, tmp_path):
        dest = tmp_path / "output.md"
        dest.write_text("existente")
        with pytest.raises(FileExistsError):
            files.copy_template(src_file, dest)

    def test_overwrites_when_flag_set(self, src_file, tmp_path):
        dest = tmp_path / "output.md"
        dest.write_text("existente")
        files.copy_template(src_file, dest, overwrite=True)
        assert dest.read_text() == src_file.read_text()


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


class TestChecksum:
    def test_returns_hex_string(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_bytes(b"conteudo")
        result = files.checksum(f)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_same_content_same_checksum(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"igual")
        f2.write_bytes(b"igual")
        assert files.checksum(f1) == files.checksum(f2)

    def test_different_content_different_checksum(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_bytes(b"conteudo-a")
        f2.write_bytes(b"conteudo-b")
        assert files.checksum(f1) != files.checksum(f2)


class TestBumpVersion:
    def test_bumps_patch(self):
        assert files.bump_version('1.0.0') == '1.0.1'
        assert files.bump_version('1.2.3') == '1.2.4'
        assert files.bump_version('0.0.9') == '0.0.10'

    def test_returns_unchanged_for_invalid_format(self):
        assert files.bump_version('1.0') == '1.0'
        assert files.bump_version('abc') == 'abc'
        assert files.bump_version('') == ''
