#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Contributors to the Gardener project
#
# SPDX-License-Identifier: Apache-2.0
#
# Verifies that the upstream-ingress-gce source entry in .ocm/base-component.yaml
# is in sync with VERSION. The -dev suffix is stripped from VERSION before comparing
# since it is absent in the OCM entry and in the upstream tag.

import sys
import yaml

with open('VERSION') as f:
    version = f.read().strip().split('-')[0]
with open('.ocm/base-component.yaml') as f:
    ocm = yaml.safe_load(f)

sources = ocm.get('sources', [])
upstream = next((s for s in sources if s.get('name') == 'upstream-ingress-gce'), None)

errors = []
if upstream is None:
    errors.append("no 'upstream-ingress-gce' entry found in .ocm/base-component.yaml sources")
else:
    ocm_ref = str(upstream.get('access', {}).get('ref', ''))
    ocm_commit = str(upstream.get('access', {}).get('commit', ''))

    if ocm_ref != version:
        errors.append(f"sources[upstream-ingress-gce].access.ref={ocm_ref!r} != VERSION={version!r}")
    if not ocm_commit:
        errors.append("sources[upstream-ingress-gce].access.commit is empty")

if errors:
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

print(f"OK: OCM source pin ref={ocm_ref} commit={ocm_commit}")
