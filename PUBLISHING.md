# GitHub and Registry publication

Author: Aman Dolorain

This is a new repository and a separate Registry package. Do not upload these files into ComfyUI-Video-Control or replace that package's releases.

## Fixed identities

| Field | Value |
| --- | --- |
| GitHub repository | H3-Video-Controller |
| Registry/Manager display name | H3 Video Controller |
| Canvas node title | H3 Video Controller |
| Registry package ID | h3-video-controller |
| Registered Python node ID | H3VideoController |
| Publisher ID | amandolorain |
| Author | Aman Dolorain |
| Version | 1.0.0 |

The Registry must confirm that the package ID is available at first publication. No publication is claimed by this prepared source package.

## Create the GitHub repository

Sign in to GitHub, create a public repository named H3-Video-Controller, and leave initial README, license and gitignore options unselected because these files are included.

Suggested description: `MiniMax H3 video control for ComfyUI: flexible resolution, square presets, joint video/audio latent and shared timing metadata.`

Upload the contents inside H3VideoController at the repository root. Do not upload the outer folder or the ZIP alone. Include web/author.js and the tests directory. Commit message: `Initial release: H3 Video Controller v1.0.0`.

The dot-prefixed files are configuration, not credentials. If browser upload omits them, use Add file > Create new file and paste the exact filename/path and contents:

- `.gitignore`
- `.github/workflows/tests.yml`
- `.github/workflows/publish.yml`

This pack's .github directory is distinct from the previous repository. Those files must be added to the new repository even if a similarly named workflow exists elsewhere.

## Add the publishing secret to THIS repository

The same Registry publisher can own multiple packs. A GitHub repository secret does not automatically carry over from another repository.

Use an existing retained publishing key for amandolorain or create a new publisher API key in Comfy Registry. In the new GitHub repository, open Settings > Secrets and variables > Actions > New repository secret.

Name: `REGISTRY_ACCESS_TOKEN`. Value: the publishing key. Save it privately. Never put this value in a source file, screenshot or chat.

## Publish and verify

Open Actions > Publish H3 node to Comfy Registry > Run workflow, branch main. The workflow runs unit tests before publishing. Later commits changing pyproject.toml trigger the workflow automatically.

Check the successful job log and the Registry publisher page. The new package should have the exact display name from the identity table. Registry validation/approval is separate from upload success. Published version numbers cannot be overwritten.

If the node-level title needs correction, use Registry Edit details > Node name. Do not rename the immutable package ID or republish code merely to refresh a title. Once the Registry title is correct, leave it alone.

Manager uses a Registry metadata cache separate from the legacy channel-list mode. If a correct Registry title has not reached Manager, use DB Channel remote, Channel default and Check Update/Fetch Updates when available; let the ComfyRegistry data fetch complete, then reopen the list. Do not delete versions to solve a cached title.

## Later updates

Increment the version consistently in pyproject.toml, __init__.py and README. Commit all changed source files together. Check Actions before asking users to update. GitHub hosts source, Registry distributes versioned packages, and Manager installs a local copy; none of these moves model inference to GitHub.
