# ingress-gce

[![reuse compliant](https://reuse.software/badge/reuse-compliant.svg)](https://reuse.software/)

This repository is dedicated to building [kubernetes/ingress-gce](https://github.com/kubernetes/ingress-gce) images for the Gardener project.

## Repository structure

This repo contains no Go source code. Instead, it clones `kubernetes/ingress-gce` at a pinned upstream tag and commit during the Docker build and compiles it there. Two files control versioning:

- **`VERSION`** — the *packaging version* of the image this repository produces (e.g. `v1.38.3`)
- **`.ocm/upstream-source.json`** — the upstream release and commit to build

These are separate because a packaging release can differ from the upstream release — for example, a Go toolchain security update produces a new packaging patch version while the upstream source stays the same.

## Updating versions

### Adopting a new upstream release

When a new [kubernetes/ingress-gce](https://github.com/kubernetes/ingress-gce) release is available, update `version`, `access.ref`, and `access.commit` in `.ocm/upstream-source.json` together. Obtain the upstream commit ID with:

```shell
git ls-remote https://github.com/kubernetes/ingress-gce.git \
  'refs/tags/v1.38.3' 'refs/tags/v1.38.3^{}'
```

Some Git tags are annotated and return two lines; use the commit ID from the `^{}` line. For a lightweight tag, use the single returned ID.

### Selecting the packaging version

For each new release in a major/minor line, choose the packaging patch as `max(upstream patch, latest published packaging patch + 1)`. This keeps versions equal when possible and gives build-only changes (e.g. Go toolchain bumps) a new version. For example:

- Upstream `v1.38.0`, no prior packaging release → packaging `v1.38.0`
- Go toolchain CVE fix, upstream still `v1.38.0` → packaging `v1.38.1`
- Upstream bumps to `v1.38.1` → packaging `v1.38.2` (since `v1.38.1` is already published)
- Upstream bumps to `v1.38.5` → packaging `v1.38.5`

The release build enforces that major/minor match and packaging patch >= upstream patch. Check [published releases](https://github.com/gardener/ingress-gce/releases) before selecting a version and never overwrite an existing release.

Set `VERSION` to the intended packaging version (with `-dev` suffix during development). Update `.ocm/upstream-source.json` to match. Record the release in [PACKAGING.md](PACKAGING.md).

### Go toolchain update (CVE fix)

1. Update `FROM golang:X.Y.Z` in the `Dockerfile`
2. Bump `VERSION` to the next packaging patch (e.g. `v1.38.0` → `v1.38.1-dev`)
3. Leave `.ocm/upstream-source.json` unchanged
4. Add a row to `PACKAGING.md`

## Triggering a release

Dispatch the **Release** workflow from `master` or a `release-*` branch via the GitHub web UI or CLI:

```shell
gh workflow run release.yaml -f next-version=bump-patch
# or: -f next-version=bump-minor
```

The workflow validates that `VERSION` and `.ocm/upstream-source.json` are consistent, builds the image, publishes it to the Gardener GAR, creates a GitHub release, and bumps the version for the next development cycle.


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
