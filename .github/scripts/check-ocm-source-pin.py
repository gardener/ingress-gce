#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Contributors to the Gardener project
#
# SPDX-License-Identifier: Apache-2.0
#
# Verifies that the upstream-ingress-gce source entry in .ocm/base-component.yaml
# is in sync with VERSION and UPSTREAM_COMMIT. Run as part of the build workflow
# to catch cases where these three files are updated non-atomically.

import sys
import yaml

with open('VERSION') as f:
    version = f.read().strip()
with open('UPSTREAM_COMMIT') as f:
    upstream_commit = f.read().strip()
with open('.ocm/base-component.yaml') as f:
    ocm = yaml.safe_load(f)

sources = ocm.get('sources', [])
upstream = next((s for s in sources if s.get('name') == 'upstream-ingress-gce'), None)

errors = []
if upstream is None:
    errors.append("no 'upstream-ingress-gce' entry found in .ocm/base-component.yaml sources")
else:
    ocm_version = str(upstream.get('version', ''))
    ocm_ref = str(upstream.get('access', {}).get('ref', ''))
    ocm_commit = str(upstream.get('access', {}).get('commit', ''))
    if ocm_version != version:
        errors.append(f"sources[upstream-ingress-gce].version={ocm_version!r} != VERSION={version!r}")
    if ocm_ref != version:
        errors.append(f"sources[upstream-ingress-gce].access.ref={ocm_ref!r} != VERSION={version!r}")
    if ocm_commit != upstream_commit:
        errors.append(
            f"sources[upstream-ingress-gce].access.commit={ocm_commit!r} != UPSTREAM_COMMIT={upstream_commit!r}"
        )

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

print(f"OK: OCM source pin matches VERSION={version} UPSTREAM_COMMIT={upstream_commit}")
