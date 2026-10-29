# Registry installation repair — H3 Video Controller 1.2.3

Checked 2026-10-29 against the public API and Manager source.

## Confirmed observations

- Public API /nodes/h3-video-controller/versions returned NodeVersionStatusFlagged for 1.2.2 and previous versions.
- The repository's 1.2.2 Registry publish workflow completed successfully. That confirms upload/publishing, not scan acceptance.
- Simple Prompt 1.0.0 was Active and Audio Controller 1.0.0 was Pending at the same observation time. They must not be described as having the same confirmed status.
- The user's terminal log reports the dedicated Git URL permission gate. Manager treats Nightly as a Git/source installation, not a versioned CNR archive, and checks unknown repository URLs against its default-channel catalog.

## What was corrected

The old optional tests/test_upstream_contract.py dynamically executed extracted upstream source. It is replaced by read-only AST checks. Runtime node code did not use that mechanism. Unit-test module loading now uses an ordinary package import. .comfyignore excludes tests and .github development files from the distributed runtime archive as documented by ComfyUI.

The documented Comfy security policy scrutinizes dynamic execution. This is a plausible flag trigger; the exact private scan finding was NOT available and must not be presented as confirmed. These changes remove an unnecessary executable-source test rather than disabling the scanner or weakening user security. All controller runtime files except version metadata are unchanged.

## Release

Upload all changed files, including tests and the NEW .comfyignore, to the repository root. Keep the web directory unchanged. Existing .github workflows and .gitignore are unchanged.

Commit: Remove dynamic test execution and package runtime-only Registry release
Version: 1.2.3
Tag: v1.2.3
Title: H3 Video Controller v1.2.3

The existing publish workflow triggers when pyproject.toml is pushed to main. Do not separately rerun the workflow for the same immutable version if it already published successfully.

After publishing, check the Registry version status. Only claim resolution after 1.2.3 becomes Active AND a fresh normal-security Manager installation of the numbered 1.2.3 archive succeeds. Select the numbered Registry version, not Nightly. A runtime package cannot grant its own Git install privileges; the gate runs before package code.

If still Flagged/Pending, request review through Comfy's official security review channel, supplying the Registry node ID, version and code diff. Do not disable security checks, falsify package identity, or keep bumping versions without a concrete correction.

## Local verification

Python unit tests and JavaScript migration/resolution tests were run. Optional native source checks require COMFYUI_H3_SOURCE. No Registry publish was performed from this environment, and the private Registry security scanner / comfy node validate was not available. A grep/AST check is not a substitute for those validations.

## Primary references

https://api.comfy.org/nodes/h3-video-controller/versions
https://github.com/Comfy-Org/ComfyUI-Manager/blob/main/glob/manager_server.py
https://blog.comfy.org/p/comfyui-2025-jan-security-update
https://docs.comfy.org/registry/publishing
