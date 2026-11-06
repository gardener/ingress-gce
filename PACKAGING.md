# Packaging History

Packaging releases share the upstream major/minor version. Their patch is at
least the upstream patch and increases for every new packaging release in that
line, including build-only changes. See [the version policy](README.md#updating-versions)
for version selection and collision handling.

For every release, add a row recording the packaging version, upstream version,
Go toolchain, and changes. Keep previous rows unchanged. Review the upstream
source descriptor, [`.ocm/upstream-source.json`](.ocm/upstream-source.json),
at the packaging release tag for the exact upstream commit; this table does not
replace that descriptor.

## Release Mapping

| Packaging version | Upstream version | Go toolchain | Changes / status |
| --- | --- | --- | --- |
| Unreleased (version pending) | vX.Y.Z | X.Y.Z | Migrate upstream source pin to `.ocm/upstream-source.json`, add packaging version policy and release mapping. |
| v1.38.3 | v1.38.3 | 1.26.0 | Historical baseline before source pinning migration; upstream commit was recorded in `.ocm/base-component.yaml`. |

When preparing a release, fill in all three version columns:

- Replace `Unreleased (version pending)` with the packaging version.
- Replace upstream `vX.Y.Z` with the selected upstream version.
- Replace Go toolchain `X.Y.Z` with the Go version used for the release build.

Update [`.ocm/upstream-source.json`](.ocm/upstream-source.json) to match the
selected upstream release and commit.

## Active Downstream Differences

- The build selects Go 1.26.0 in the Dockerfile. Review the toolchain against
  upstream requirements and security updates for each release.
- No downstream source patches or dependency overrides are applied.
