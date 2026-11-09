import copy
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


CI = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, CI / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


upstream = load_module('upstream')


class SourceConfigurationTests(unittest.TestCase):
    def test_lock_identity(self):
        source = upstream.load_source()
        self.assertEqual(source['access']['ref'], f"refs/tags/{source['version']}")


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.source = {
            'name': 'ingress-gce',
            'version': 'v1.38.0',
            'type': 'git',
            'access': {
                'type': 'github',
                'repoUrl': 'github.com/kubernetes/ingress-gce',
                'ref': 'refs/tags/v1.38.0',
                'commit': 'a' * 40,
            },
        }

    def test_loads_valid_source(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'source.json'
            lock.write_text(json.dumps(self.source))
            self.assertEqual(upstream.load_source(lock), self.source)

    def test_snapshot_does_not_infer_future_source(self):
        before = copy.deepcopy(self.source)
        upstream.validate_release(self.source, 'snapshot', 'v1.99.0-dev')
        self.assertEqual(self.source, before)

    def test_release_allows_matching_or_higher_packaging_patch(self):
        for upstream_patch, packaging_patch in ((0, 0), (0, 1), (1, 1), (1, 2), (9, 10)):
            self.source['version'] = f'v1.38.{upstream_patch}'
            for suffix in ('', '-dev'):
                packaging_version = f'v1.38.{packaging_patch}{suffix}'
                with self.subTest(upstream=self.source['version'], packaging=packaging_version):
                    upstream.validate_release(self.source, 'release', packaging_version)

    def test_release_rejects_packaging_patch_below_upstream(self):
        for upstream_patch, packaging_patch in ((1, 0), (2, 1), (10, 9)):
            self.source['version'] = f'v1.38.{upstream_patch}'
            for suffix in ('', '-dev'):
                packaging_version = f'v1.38.{packaging_patch}{suffix}'
                with self.subTest(upstream=self.source['version'], packaging=packaging_version):
                    with self.assertRaisesRegex(ValueError, 'Packaging patch version'):
                        upstream.validate_release(self.source, 'release', packaging_version)

    def test_snapshot_allows_packaging_patch_below_pinned_upstream(self):
        self.source['version'] = 'v1.38.2'
        upstream.validate_release(self.source, 'snapshot', 'v1.38.1-dev')

    def test_release_rejects_minor_mismatch(self):
        with self.assertRaises(ValueError):
            upstream.validate_release(self.source, 'release', 'v1.39.0-dev')

    def test_release_rejects_major_mismatch(self):
        with self.assertRaises(ValueError):
            upstream.validate_release(self.source, 'release', 'v2.38.0')

    def test_release_rejects_malformed_version(self):
        for packaging_version in (
            'v1.38.0;echo bad', 'v1.38.0-sap.1', 'v1.38.0-rc.1',
            'v1.38.0+build.1', 'v1.38.0-dev-extra', 'v1.38.0-dev-dev',
            'v1.38.01', 'v1.38', '1.38.0',
        ):
            with self.subTest(packaging=packaging_version):
                with self.assertRaisesRegex(ValueError, 'Packaging version must be a stable release'):
                    upstream.validate_release(self.source, 'release', packaging_version)

    def test_rejects_missing_empty_or_unknown_mode(self):
        for mode in (None, '', 'other'):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(ValueError, 'Mode must be snapshot or release'):
                    upstream.validate_release(self.source, mode, 'v1.38.0')

    def test_rejects_invalid_source_fields(self):
        changes = (
            ('version', 'v1.38.0-dev'),
            ('version', 'v1.038.0'),
            ('type', 'directoryTree'),
            ('name', 'main-source'),
            ('commit', 'abc123'),
            ('commit', 'a' * 39 + ';'),
            ('ref', 'refs/heads/v1.38.0'),
            ('repoUrl', 'github.com/other/ingress-gce'),
            ('access-type', 'localBlob'),
        )
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'source.json'
            for field, value in changes:
                with self.subTest(field=field, value=value):
                    source = copy.deepcopy(self.source)
                    if field == 'access-type':
                        source['access']['type'] = value
                    elif field in source['access']:
                        source['access'][field] = value
                    else:
                        source[field] = value
                    lock.write_text(json.dumps(source))
                    with self.assertRaises(ValueError):
                        upstream.load_source(lock)


class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'origin'
        self.destination = self.root / 'checkout'
        self.env = {
            **os.environ,
            'GIT_CONFIG_COUNT': '2',
            'GIT_CONFIG_KEY_0': f'url.{self.repo.as_uri()}.insteadOf',
            'GIT_CONFIG_VALUE_0': 'https://github.com/kubernetes/ingress-gce.git',
            'GIT_CONFIG_KEY_1': 'protocol.file.allow',
            'GIT_CONFIG_VALUE_1': 'always',
            'GIT_AUTHOR_NAME': 'Test', 'GIT_COMMITTER_NAME': 'Test',
            'GIT_AUTHOR_EMAIL': 'test@example.org', 'GIT_COMMITTER_EMAIL': 'test@example.org',
        }
        self.git('init', '--quiet', str(self.repo), in_repo=False)
        self.git('-c', 'commit.gpgsign=false', 'commit', '--quiet', '--allow-empty', '-m', 'release')
        self.commit = self.git('rev-parse', 'HEAD').stdout.strip()

    def git(self, *args, in_repo=True):
        command = ['git']
        if in_repo:
            command += ['-C', str(self.repo)]
        return subprocess.run(command + list(args), env=self.env, check=True,
                              capture_output=True, text=True)

    def run_checkout(self, version='v1.38.0', commit=None):
        return subprocess.run(
            ['sh', str(CI / 'checkout-upstream.sh'), version,
             commit or self.commit, str(self.destination)],
            env=self.env, capture_output=True, text=True,
        )

    def test_lightweight_tag(self):
        self.git('tag', 'v1.38.0')
        self.assertEqual(self.run_checkout().returncode, 0)
        head = subprocess.check_output(['git', '-C', str(self.destination), 'rev-parse', 'HEAD'],
                                       env=self.env, text=True).strip()
        self.assertEqual(head, self.commit)
        detached = subprocess.run(['git', '-C', str(self.destination), 'symbolic-ref', '-q', 'HEAD'],
                                  env=self.env, capture_output=True)
        self.assertNotEqual(detached.returncode, 0)

    def test_annotated_tag_with_conflicting_branch(self):
        self.git('-c', 'tag.gpgsign=false', 'tag', '-a', 'v1.38.0', '-m', 'release')
        self.git('-c', 'commit.gpgsign=false', 'commit', '--quiet', '--allow-empty', '-m', 'other')
        self.git('branch', 'v1.38.0')
        self.assertEqual(self.run_checkout().returncode, 0)

    def test_branch_without_tag_is_rejected(self):
        self.git('branch', 'v1.38.0')
        self.assertNotEqual(self.run_checkout().returncode, 0)

    def test_missing_tag_is_rejected(self):
        self.assertNotEqual(self.run_checkout().returncode, 0)

    def test_moved_tag_is_rejected(self):
        self.git('-c', 'commit.gpgsign=false', 'commit', '--quiet', '--allow-empty', '-m', 'other')
        self.git('tag', 'v1.38.0')
        result = self.run_checkout()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('expected ' + self.commit, result.stderr)

    def test_annotated_tag_object_is_not_a_commit_pin(self):
        self.git('-c', 'tag.gpgsign=false', 'tag', '-a', 'v1.38.0', '-m', 'release')
        tag_object = self.git('rev-parse', 'refs/tags/v1.38.0').stdout.strip()
        self.assertNotEqual(self.run_checkout(commit=tag_object).returncode, 0)

    def test_rejects_invalid_arguments(self):
        for version, commit in [('v1.38.0-dev', self.commit), ('v1.38.0', 'abc123'),
                                ('v1.38.0;echo bad', self.commit)]:
            with self.subTest(version=version, commit=commit):
                self.assertNotEqual(self.run_checkout(version, commit).returncode, 0)
                self.assertFalse(self.destination.exists())

    def test_rejects_nonempty_destination(self):
        self.destination.mkdir()
        (self.destination / 'unreviewed.go').write_text('package main')
        self.assertNotEqual(self.run_checkout().returncode, 0)


if __name__ == '__main__':
    unittest.main()
