from __future__ import annotations

from legal_research_skill.constants import (
    PACKAGE_SCHEMAS_DIR,
    WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR,
    resolve_schemas_dir,
)


def test_default_mode_always_uses_packaged_schemas_even_if_worktree_dir_exists(tmp_path):
    project_root = tmp_path / "checkout"
    worktree_schemas = project_root / "schemas"
    worktree_schemas.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    resolved = resolve_schemas_dir(
        project_root=project_root,
        worktree_schemas_dir=worktree_schemas,
        package_schemas_dir=PACKAGE_SCHEMAS_DIR,
        environ={},
    )
    assert resolved == PACKAGE_SCHEMAS_DIR


def test_env_flag_alone_without_pyproject_toml_does_not_activate_override(tmp_path):
    # Guards against an unrelated ancestor directory that happens to have a
    # schemas/ folder (e.g. a nested venv or monorepo) being trusted just
    # because the environment variable is set.
    project_root = tmp_path / "unrelated"
    worktree_schemas = project_root / "schemas"
    worktree_schemas.mkdir(parents=True)
    # Deliberately no pyproject.toml here.

    resolved = resolve_schemas_dir(
        project_root=project_root,
        worktree_schemas_dir=worktree_schemas,
        package_schemas_dir=PACKAGE_SCHEMAS_DIR,
        environ={WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR: "1"},
    )
    assert resolved == PACKAGE_SCHEMAS_DIR


def test_env_flag_with_genuine_checkout_activates_override(tmp_path, capsys):
    project_root = tmp_path / "checkout"
    worktree_schemas = project_root / "schemas"
    worktree_schemas.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    resolved = resolve_schemas_dir(
        project_root=project_root,
        worktree_schemas_dir=worktree_schemas,
        package_schemas_dir=PACKAGE_SCHEMAS_DIR,
        environ={WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR: "1"},
    )
    assert resolved == worktree_schemas
    assert "Using worktree schemas" in capsys.readouterr().err


def test_env_flag_with_missing_worktree_dir_falls_back_to_package(tmp_path):
    project_root = tmp_path / "checkout"
    project_root.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    worktree_schemas = project_root / "schemas"  # never created

    resolved = resolve_schemas_dir(
        project_root=project_root,
        worktree_schemas_dir=worktree_schemas,
        package_schemas_dir=PACKAGE_SCHEMAS_DIR,
        environ={WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR: "1"},
    )
    assert resolved == PACKAGE_SCHEMAS_DIR


def test_env_flag_with_wrong_value_does_not_activate_override(tmp_path):
    project_root = tmp_path / "checkout"
    worktree_schemas = project_root / "schemas"
    worktree_schemas.mkdir(parents=True)
    (project_root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")

    for value in ("true", "yes", "0", ""):
        resolved = resolve_schemas_dir(
            project_root=project_root,
            worktree_schemas_dir=worktree_schemas,
            package_schemas_dir=PACKAGE_SCHEMAS_DIR,
            environ={WORKTREE_SCHEMAS_OVERRIDE_ENV_VAR: value},
        )
        assert resolved == PACKAGE_SCHEMAS_DIR
