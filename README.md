# ingress-gce

[![reuse compliant](https://reuse.software/badge/reuse-compliant.svg)](https://reuse.software/)

This repository is dedicated to building [kubernetes/ingress-gce](https://github.com/kubernetes/ingress-gce) images for the Gardener project.

## Repository structure

This repo contains no Go source code. Instead, it clones `kubernetes/ingress-gce` at a pinned upstream tag and commit during the Docker build and compiles it there. Two files control which upstream version is built:

- `VERSION` — the upstream tag to clone (e.g. `v1.38.2`), also used as the gardener release version
- `UPSTREAM_COMMIT` — the exact commit SHA that tag must resolve to; the Dockerfile hard-fails if they diverge

Both files **must be updated atomically** in the same PR whenever the upstream version changes. The `.ocm/base-component.yaml` `sources` entry must also be updated to reflect the new tag and commit.

## Bumping the upstream version

When a new [kubernetes/ingress-gce](https://github.com/kubernetes/ingress-gce) release is available:

1. Look up the commit SHA for the new tag:
   ```shell
   git ls-remote https://github.com/kubernetes/ingress-gce refs/tags/<NEW_TAG>
   # use the commit the tag points to (dereference ^{} entries for annotated tags)
   ```

2. Open a PR updating these three files together:
   - `VERSION` → new tag (e.g. `v1.38.3`)
   - `UPSTREAM_COMMIT` → the commit SHA from step 1
   - `.ocm/base-component.yaml` → update `sources[0].version`, `sources[0].access.ref`, and `sources[0].access.commit`

3. After the PR merges, trigger the release workflow.

## Triggering a release

Dispatch the **Release** workflow from `master` or a `release-*` branch via the GitHub web UI or CLI:

```shell
gh workflow run release.yaml -f next-version=bump-patch
# or: -f next-version=bump-minor
```

The workflow builds the image, publishes it to the Gardener GAR, creates a GitHub release, and bumps the version for the next development cycle.


## How to use this repository template

This template repository can be used to seed new git repositories in the gardener github organisation.

- [Create the new repository](https://docs.github.com/en/free-pro-team@latest/github/creating-cloning-and-archiving-repositories/creating-a-repository-from-a-template)
  based on this template repository
- Replacing placeholders:
  - In file `.reuse/dep5` replace placeholder `<repo name>` with the name of your new repository.
  - In file `CODEOWNERS` replace `<repo name>` and `<maintainer team>`. Use the name of the github team in [gardener teams](https://github.com/orgs/gardener/teams) defining maintainers of the new repository.
- Set the repository description in the "About" section of your repository
- Describe the new component in additional sections in this `README.md`
- Ask the [Owner of the gardener github organisation](https://github.com/orgs/gardener/people?query=role%3Aowner)
  - to double-check the initial content of this repository
  - to create the maintainer team for this new repository
  - to make this repository public
  - protect at least the master branch requiring mandatory code review by the maintainers defined in CODEOWNERS
  - grant admin permission to the maintainers team of the new repository defined in CODEOWNERS

## Maintain copyright and license information
By default all source code files are under `Apache 2.0` and all markdown files are under `Creative Commons` license.

When creating new source code files the license and copyright information should be provided using corresponding SPDX headers.

Example for go source code files (replace `<year>` with the current year)
```
/*
 * SPDX-FileCopyrightText: <year> Contributors to the Gardener project
 *
 * SPDX-License-Identifier: Apache-2.0
 */
```

### Third-party source code

If you copy third-party code into this repository or fork a repository, you must keep the license and copyright information (usually defined in the header of the file).

In addition you should adapt the `.reuse/dep5` file and assign the correct copyright and license information.

**Example `dep5` file if you copy source code into your repository:**
```
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: Gardener <repo name>
Upstream-Contact: The Gardener project <gardener@googlegroups.com>
Source: https://github.com/gardener/<repo name>

# --------------------------------------------------
# source code

Files: *
Copyright: Contributors to the Gardener project
License: Apache-2.0

# --------------------------------------------------
# documentation

Files: *.md
Copyright: Contributors to the Gardener project
License: CC-BY-4.0

# --------------------------------------------------
# third-party

# --- copied source code ---
Files: pkg/utils/validation/kubernetes/core/*
Copyright: 2014 The Kubernetes Authors.
License: Apache-2.0
```
**Example `dep5` file if you have forked a repository:**
```
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: Gardener fork of kubernetes/autoscaler
Upstream-Contact: The Gardener project <gardener@googlegroups.com>
Source: https://github.com/gardener/autoscaler
Comment: This is a fork of kubernetes/autoscaler (https://github.com/kubernetes/autoscaler)

# --------------------------------------------------
# source code

Files: *
Copyright: 2016-2018 The Kubernetes Authors.
License: Apache-2.0

Files: .ci/*
Copyright: Contributors to the Gardener project
License: Apache-2.0
```

#### Modifications
In case you modify copied/forked source code you must state this in the header via the following text:

**Modifications Copyright <year> Contributors to the Gardener project**


### Get your reuse badge
To get your project reuse compliant you should register it [here](https://api.reuse.software/register) using your SAP email address. After confirming your email, an inital reuse check is done by the reuse API.

To add the badge to your project's `README.md` file, use the snipped provided by the reuse API.
