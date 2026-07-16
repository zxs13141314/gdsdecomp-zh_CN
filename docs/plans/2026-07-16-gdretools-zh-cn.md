# GDRE Tools Simplified Chinese Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Build a maintainable Simplified Chinese edition of GDRE Tools v2.6.0 and automatically produce a Windows package with GitHub Actions.

**Architecture:** Localization is split between the standalone PCK UI and C++ `RTR()` UI. The repository owns the `zh_CN` translation sources, localization integration, and a Windows-only workflow that checks out the required Godot fork, installs this module under `modules/gdsdecomp`, builds the binaries, exports the standalone application, and uploads a ZIP artifact.

**Tech Stack:** Custom Godot 4 source, C++, GDScript, Gettext PO, SCons, GitHub Actions, PowerShell.

---

### Task 1: Establish the localization repository

**Files:**
- Create: `docs/plans/2026-07-16-gdretools-zh-cn.md`
- Modify: `README.md`

**Steps:**
1. Create `zh_CN-v2.6.0` from the official `v2.6.0` tag.
2. Document the upstream repository, base version, license, and localization status.
3. Configure `upstream` for the official repository and `origin` for the Chinese repository.
4. Run `git status --short --branch` and verify the clean baseline.

### Task 2: Extract translatable UI text

**Files:**
- Create: `standalone/translations/gdre_tools.pot`
- Create: `tools/i18n/extract_translations.py`
- Create: `tools/i18n/check_translations.py`

**Steps:**
1. Extract scene `text`, `title`, and `tooltip_text` values.
2. Extract user-facing GDScript strings.
3. Extract C++ strings wrapped in `RTR()`.
4. Deduplicate and sort message IDs deterministically.
5. Validate placeholders, newlines, and duplicate entries.

### Task 3: Localize the standalone UI

**Files:**
- Create: `standalone/translations/gdre_tools.zh_CN.po`
- Modify: `standalone/project.godot`
- Modify: `standalone/gdre_main.gd`
- Modify: `standalone/gdre_config_dialog.gd`

**Steps:**
1. Register the Simplified Chinese translation resource.
2. Route dynamic UI strings through `tr()`.
3. Add a UI language setting for System, English, and Simplified Chinese.
4. Persist and restore the selected locale.
5. Verify Chinese font fallback in menus, logs, and file dialogs.

### Task 4: Localize C++ RTR strings

**Files:**
- Create: `translations/editor/gdre_tools.zh_CN.po`
- Create: `tools/i18n/merge_editor_translation.py`
- Modify: `.github/workflows/build_zh_CN_windows.yml`

**Steps:**
1. Maintain a dedicated PO for module-owned `RTR()` strings.
2. Merge module messages into Godot's `zh_CN` editor translation during CI.
3. Reject duplicate conflicts and invalid PO formatting.
4. Build Windows binaries and verify translated C++ dialogs.

### Task 5: Build Windows packages automatically

**Files:**
- Create: `.github/workflows/build_zh_CN_windows.yml`
- Create: `tools/ci/package_windows.ps1`

**Steps:**
1. Use `nikitalita/godot@gdre-wb-f964fa714f5` as required upstream.
2. Keep only Windows editor and template release builds.
3. Install Python/SCons, Rust, and .NET 10 SDK.
4. Import standalone resources and export `gdre_tools.exe` and `gdre_tools.pck`.
5. Package `GDRE_tools-v2.6.0-zh_CN-windows.zip`.
6. Upload the package with `actions/upload-artifact`.

### Task 6: Release and validate

**Files:**
- Create: `.github/workflows/release_zh_CN.yml`
- Modify: `README.md`

**Steps:**
1. Run translation validation on pushes and manual builds.
2. Publish a GitHub Release for `zh-v*` tags.
3. Attach the Windows ZIP, licenses, and coverage notes.
4. Test the main window, settings, recovery, export, and error dialogs.
5. Track untranslated strings for follow-up iterations.

