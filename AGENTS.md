# LibreSVIP — Notes for AI Coding Assistants

## Commands

- uv-managed; Python 3.11+. Install dev deps: `uv sync --all-extras --group linting`
- Type check: `uv run pyrefly check .` (the default gate, finishes in ~1s)
- Lint / format: `uv run ruff check --fix .`; `uv run ruff format --config pyproject.toml --exclude tests/ .`
- Tests: `uv run pytest tests/ -v`
- All hooks (same entry point as CI): `uv run prek run --all-files`
  - LF line endings, no trailing whitespace; tombi formats TOML and rumdl formats Markdown — don't align tables by hand

## ⚠️ The type checker is pyrefly, not mypy

- The default type checker has moved from mypy to **pyrefly** (the `pyrefly-check` hook in `.pre-commit-config.yaml` is the gate). mypy (with the pydantic.mypy plugin) is still in the `linting` group, but it is slow and noticeably stricter — **do not treat its output as a pass/fail bar**, and do not change code just to satisfy it.
- `[tool.pyrefly.errors]` / `[tool.ty.rules]` in `pyproject.toml` ignore a batch of call-shape errors — this is deliberate (see next bullet). Don't "fix" those ignore configs.
- This repo is dense with pydantic models (`libresvip/model/base.py` and every plugin) whose `__init__` is synthesized via dataclass_transform. pyright / basedpyright / ty cannot resolve it and will flood ordinary model constructions with false "missing argument / unexpected keyword" errors (**including files you never touched**). When you see this noise:
  - don't add `# type: ignore` or restructure working pydantic code to silence it;
  - dozens of such errors from an IDE / LSP / AI probe (e.g. pi-lens' basedpyright) is tool noise, not a code problem;
  - the one and only standard: `uv run pyrefly check .` reports zero errors.

## Project layout

Multiple frontends share one conversion core — **format-conversion logic always lives in the core and plugins, never in a frontend**:

| Entry | Tech | Location |
| --- | --- | --- |
| Desktop GUI | PySide6 / QML | `libresvip/gui/` (UI is QML in `libresvip/res/`, compiled into resources.rcc) |
| TUI | textual | `libresvip/tui/` |
| Web | in-house pages | `libresvip/web/` |
| Mobile | flet | `libresvip/mobile/` |
| CLI | typer | `libresvip/cli/` (incl. `rpc/`, entry point `libresvip-cli`) |

Core:

- `libresvip/model/` — internal project models: `base.py` (pydantic base for all models, `populate_by_name=True`) plus pitch/curve conversion modules (`synthv_pitch`, `relative_pitch_curve`, `reset_time_axis`, `vocaloid/`, …)
- `libresvip/core/` — tick math (`tick_counter`), time sync (`time_sync`), g2p (`lyric_phoneme/`), exceptions & warning types
- `libresvip/extension/` — plugin system: `SVSConverter` base class (`base.py`), loading & metadata (`manager.py`)
- `libresvip/middlewares/` — pre/post-conversion pipeline (pitch shift, zoom, lyric cleanup, lyric replacement, …)

Format plugins `libresvip/plugins/<format>/` (~40 formats, ace through y77):

- Fixed roles: `model.py` (pydantic model of the target format — external fields always use camelCase aliases `Field(alias="startOffset")`, serialize with `by_alias=True`), `<format>_parser.py` (format → internal `Project`), `<format>_generator.py` (`Project` → format), `<format>_converter.py` (`SVSConverter` subclass, the load/dump entry point), `options.py` (input/output options)
- Plugin metadata in `<format>.yapsy-plugin`; translations in `locales/<lang>/LC_MESSAGES/` (wrap user-visible strings with `gettext_lazy` as `_()`); complex plugins may add constants/helper modules, but the roles above stay
- Version compatibility: migrate legacy keys on read with `model_validator(mode="before")`; emit per-version output with `model_serializer(mode="wrap")`

Around it:

- `scripts/` — codegen & compile scripts (proto, snake_case pyi, Qt resources, babel catalogs). The CI compile-files workflow compiles `.mo` / `resources.rcc` / `requirements-*.txt` and commits them back on push to main — do not produce these artifacts by hand
- `tests/` — flat `test_*.py` + `data/` & `files/` fixtures
- `docs/` (built with zensical), `packaging/` (per-platform packaging), `deprecated/`, `experimental/`
- Chinese developer docs live under `docs/` (`setup.md`, `contributing.md`, `coding_style.md`, `best_practices.md`); this file stays English

## Verification habits

- Before and after touching a plugin, run the converter's load/dump end-to-end on a real file of the target format, not just model validation — serialization round-trips are what expose alias and optional-field mistakes
- Prefer aliases for pydantic fields; make legacy fields optional with defaults rather than letting `load` blow up on an older format version
