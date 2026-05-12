import json
import pytest
from pathlib import Path
from cli.utils import registry


SAMPLE_REGISTRY = {
    "version": "1.0.0",
    "updated": "2026-01-01",
    "skills": [
        {
            "name": "skill-existente",
            "version": "1.0.0",
            "description": "Skill de teste",
            "tags": ["teste"],
            "updated": "2026-01-01"
        }
    ],
    "agents": [],
    "hooks": [],
    "commands": [],
    "plugins": []
}


@pytest.fixture
def hub_dir(tmp_path):
    reg_file = tmp_path / "registry.json"
    reg_file.write_text(
        json.dumps(SAMPLE_REGISTRY, indent=2, ensure_ascii=False) + '\n'
    )
    return tmp_path


class TestLoad:
    def test_loads_registry(self, hub_dir):
        data = registry.load(hub_dir)
        assert data['version'] == '1.0.0'
        assert len(data['skills']) == 1

    def test_raises_when_file_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            registry.load(tmp_path)


class TestSave:
    def test_saves_with_newline(self, hub_dir):
        data = registry.load(hub_dir)
        data['version'] = '2.0.0'
        registry.save(hub_dir, data)
        content = (hub_dir / "registry.json").read_text()
        assert content.endswith('\n')

    def test_saved_data_is_valid_json(self, hub_dir):
        data = registry.load(hub_dir)
        data['version'] = '2.0.0'
        registry.save(hub_dir, data)
        reloaded = registry.load(hub_dir)
        assert reloaded['version'] == '2.0.0'

    def test_preserves_unicode(self, hub_dir):
        data = registry.load(hub_dir)
        data['skills'][0]['description'] = 'Descrição com acentuação'
        registry.save(hub_dir, data)
        reloaded = registry.load(hub_dir)
        assert reloaded['skills'][0]['description'] == 'Descrição com acentuação'


class TestFind:
    def test_finds_existing_entry(self, hub_dir):
        result = registry.find(hub_dir, 'skill', 'skill-existente')
        assert result is not None
        assert result['name'] == 'skill-existente'

    def test_returns_none_for_missing(self, hub_dir):
        result = registry.find(hub_dir, 'skill', 'nao-existe')
        assert result is None

    def test_returns_none_for_wrong_type(self, hub_dir):
        result = registry.find(hub_dir, 'agent', 'skill-existente')
        assert result is None


class TestUpsert:
    def test_inserts_new_entry(self, hub_dir):
        registry.upsert(hub_dir, 'skill', 'nova-skill', {
            'version': '1.0.0',
            'description': 'Nova skill',
            'tags': ['nova'],
            'updated': '2026-05-12'
        })
        result = registry.find(hub_dir, 'skill', 'nova-skill')
        assert result is not None
        assert result['version'] == '1.0.0'

    def test_updates_existing_entry(self, hub_dir):
        registry.upsert(hub_dir, 'skill', 'skill-existente', {
            'version': '2.0.0',
            'description': 'Atualizada',
            'tags': ['teste'],
            'updated': '2026-05-12'
        })
        result = registry.find(hub_dir, 'skill', 'skill-existente')
        assert result['version'] == '2.0.0'
        assert result['description'] == 'Atualizada'

    def test_does_not_duplicate_entry(self, hub_dir):
        registry.upsert(hub_dir, 'skill', 'skill-existente', {
            'version': '2.0.0',
            'description': 'Atualizada',
            'tags': [],
            'updated': '2026-05-12'
        })
        data = registry.load(hub_dir)
        names = [s['name'] for s in data['skills']]
        assert names.count('skill-existente') == 1

    def test_updates_root_updated_field(self, hub_dir):
        from datetime import date
        registry.upsert(hub_dir, 'skill', 'nova-skill', {
            'version': '1.0.0',
            'description': 'Nova',
            'tags': [],
            'updated': '2026-05-12'
        })
        data = registry.load(hub_dir)
        assert data['updated'] == str(date.today())
