# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2025 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Module implementing the unit tests for csspin_python"""

import json
import os
from unittest import mock

import csspin
import pytest
from click import Abort
from path import Path

from csspin_frontend.node import (
    _determine_exact_node_version,
    _node_archive_name,
    configure,
    provision,
)


@pytest.fixture(scope="session")
def mock__fetch_node_dist_index():
    """
    Return the checked-in testdata
    """
    test_data_file = (
        Path(__file__).parent / "test_data" / "node_dist_index_response.json"
    )
    with mock.patch(
        "csspin_frontend.node._fetch_node_dist_index"
    ) as node_dist_index_mock:
        with open(test_data_file, encoding="utf-8") as fd:
            node_dist_index_mock.return_value = json.load(fd)
            yield


@pytest.mark.parametrize(
    "version_string, expected_version",
    (
        ("lts", "v22.17.1"),
        ("LTS", "v22.17.1"),
        ("20", "v20.19.4"),
        ("20.18", "v20.18.3"),
        ("20.18.1", "v20.18.1"),
        ("v20", "v20.19.4"),
        ("v20.18", "v20.18.3"),
        ("v20.18.1", "v20.18.1"),
    ),
)
@pytest.mark.usefixtures("mock__fetch_node_dist_index")
def test__determine_exact_node_version(version_string, expected_version):
    """
    Check whether determining the node version works.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = version_string
    assert _determine_exact_node_version(cfg_mock) == expected_version


@pytest.mark.parametrize("version_string", ("99.1.2", "v99.1.2"))
def test__determine_exact_node_version_exact_version_needs_no_index(version_string):
    """
    Check whether an exact version is returned without requesting the node index.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = version_string
    with mock.patch("csspin_frontend.node._fetch_node_dist_index") as index_mock:
        assert _determine_exact_node_version(cfg_mock) == "v99.1.2"
    index_mock.assert_not_called()


@pytest.mark.parametrize(
    "version_string",
    (
        ("foo"),
        ("vfoo"),
    ),
)
@pytest.mark.usefixtures("mock__fetch_node_dist_index")
def test__determine_exact_node_version_error(version_string):
    """
    Test whether determining the node version `die`s when the version cannot be
    found.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = version_string
    with pytest.raises(Abort):
        assert _determine_exact_node_version(cfg_mock)


@pytest.fixture
def isolated_env():
    """
    Let csspin's real `setenv` modify a copy of the process environment.
    """
    with (
        mock.patch.dict(os.environ),
        mock.patch.object(csspin, "EXPORTS", []),
        mock.patch.object(csspin, "echo"),
    ):
        for key in (
            "npm_config_registry",
            "YARN_NPM_REGISTRY_SERVER",
            "YARN_UNSAFE_HTTP_WHITELIST",
            "YARN_YARN_OFFLINE_MIRROR",
        ):
            os.environ.pop(key, None)
        yield


def _configure(
    registry_url=None,
    umbrella: str | None = "2026.2",
    yarn_offline_mirror=None,
    project_root=None,
):
    cfg_mock = mock.MagicMock()
    cfg_mock.node.version = "lts"
    cfg_mock.node.use = None
    cfg_mock.node.mirror = ""
    cfg_mock.node.registry_url = registry_url
    cfg_mock.node.yarn_offline_mirror = yarn_offline_mirror
    cfg_mock.contact_elements.umbrella = umbrella
    cfg_mock.spin.project_root = project_root
    configure(cfg_mock)
    return cfg_mock


def _assert_yarn_offline_mirror(cfg, expected):
    """
    Check that the configuration tree and the environment both hold `expected`.
    The comparison ignores the separator style, which differs between hosts.
    """
    expected = Path(expected).normpath()
    assert Path(cfg.node.yarn_offline_mirror).normpath() == expected
    assert Path(os.environ["YARN_YARN_OFFLINE_MIRROR"]).normpath() == expected


@pytest.mark.usefixtures("isolated_env")
class TestConfigureYarnSettings:
    """Tests for the Yarn related environment that `configure` exports."""

    def test_nothing_is_exported_by_default(self):
        """
        Without registry_url and yarn_offline_mirror, the environment stays untouched.
        """
        _configure()
        assert not csspin.EXPORTS

    @pytest.mark.parametrize("umbrella", ("2026.1", "2026.2"))
    def test_registry_url_for_yarn_classic(self, umbrella):
        """
        Yarn classic reads npm_config_registry, so the Yarn Berry variable stays
        unset.
        """
        _configure("https://mirror.example/npm/", umbrella=umbrella)
        assert os.environ["npm_config_registry"] == "https://mirror.example/npm/"
        assert "YARN_NPM_REGISTRY_SERVER" not in os.environ

    @pytest.mark.parametrize("umbrella", ("2027.1", "2027.2"))
    def test_registry_url_for_yarn_berry(self, umbrella):
        """
        Yarn Berry reads YARN_NPM_REGISTRY_SERVER, npm still reads
        npm_config_registry. An https registry needs no whitelist entry.
        """
        _configure("https://mirror.example/npm/", umbrella=umbrella)
        assert os.environ["npm_config_registry"] == "https://mirror.example/npm/"
        assert os.environ["YARN_NPM_REGISTRY_SERVER"] == "https://mirror.example/npm/"
        assert "YARN_UNSAFE_HTTP_WHITELIST" not in os.environ

    def test_http_registry_url_skips_whitelist_for_yarn_classic(self):
        """
        The whitelist is a Yarn Berry setting, so Yarn classic gets none for an
        http registry.
        """
        _configure("http://mirror.example:8080/npm/", umbrella="2026.2")
        assert os.environ["npm_config_registry"] == "http://mirror.example:8080/npm/"
        assert "YARN_UNSAFE_HTTP_WHITELIST" not in os.environ

    def test_http_registry_url_whitelists_registry_host_for_yarn_berry(self):
        """
        Yarn Berry blocks plain http unless the host is whitelisted, so the
        registry host becomes the whole whitelist when none exists.
        """
        _configure("http://mirror.example:8080/npm/", umbrella="2027.1")
        assert os.environ["YARN_UNSAFE_HTTP_WHITELIST"] == "mirror.example"

    def test_http_registry_url_keeps_existing_whitelist(self):
        """
        The registry host gets appended to an existing Yarn Berry whitelist,
        which Yarn reads as a comma-separated list.
        """
        os.environ["YARN_UNSAFE_HTTP_WHITELIST"] = "internal.example"
        _configure("http://mirror.example:8080/npm/", umbrella="2027.1")
        assert (
            os.environ["YARN_UNSAFE_HTTP_WHITELIST"]
            == "internal.example,mirror.example"
        )
        # The activate scripts of the virtual environment build on the
        # unresolved placeholder to append to the value found at activation time.
        assert (
            dict(csspin.EXPORTS)["YARN_UNSAFE_HTTP_WHITELIST"]
            == "{YARN_UNSAFE_HTTP_WHITELIST},mirror.example"
        )

    def test_absolute_yarn_offline_mirror_for_yarn_classic(self, tmp_path):
        """
        Yarn classic gets an absolute mirror directory unchanged through its
        environment, and the property keeps it.
        """
        mirror = tmp_path / "mirror"
        cfg = _configure(
            umbrella="2026.2",
            yarn_offline_mirror=str(mirror),
            project_root=Path(tmp_path) / "project",
        )
        _assert_yarn_offline_mirror(cfg, mirror)

    def test_relative_yarn_offline_mirror_resolves_against_project_root(self, tmp_path):
        """
        Yarn runs from many directories, so a relative mirror directory has to
        become absolute.
        """
        cfg = _configure(yarn_offline_mirror="offline", project_root=Path(tmp_path))
        _assert_yarn_offline_mirror(cfg, tmp_path / "offline")

    @pytest.mark.parametrize("mirror", ("~/yarn-mirror", "{MIRROR_HOME}/yarn-mirror"))
    def test_yarn_offline_mirror_expands_tilde(self, mirror, tmp_path):
        """
        csspin does not expand `~`, so without `configure` doing it the mirror
        lands in a directory named `~` inside the project root. A placeholder
        that resolves to a `~` path expands as well, because interpolation
        comes first.
        """
        os.environ["MIRROR_HOME"] = "~"
        cfg = _configure(
            yarn_offline_mirror=mirror, project_root=Path(tmp_path) / "project"
        )
        _assert_yarn_offline_mirror(cfg, Path(os.path.expanduser("~")) / "yarn-mirror")

    def test_yarn_offline_mirror_interpolates_placeholders(self, tmp_path):
        """
        csspin interpolates the property after `configure`, so it still holds
        the raw placeholder here. The placeholder has to resolve before the
        value joins the project root, or an absolute result gets the root
        prepended. The fixture leaves the csspin configuration empty, so the
        placeholder resolves against the environment.
        """
        os.environ["MIRROR_BASE"] = str(tmp_path / "shared")
        cfg = _configure(
            yarn_offline_mirror="{MIRROR_BASE}/offline",
            project_root=Path(tmp_path) / "project",
        )
        _assert_yarn_offline_mirror(cfg, tmp_path / "shared" / "offline")

    def test_yarn_offline_mirror_is_cleared_for_yarn_berry(self, tmp_path):
        """
        Yarn Berry aborts commands that read its configuration when it finds
        the Yarn classic setting, so it is not exported and the user gets a
        warning.
        """
        with mock.patch("csspin_frontend.node.warn") as warn:
            _configure(
                umbrella="2027.1",
                yarn_offline_mirror=str(tmp_path),
                project_root=Path(tmp_path),
            )
        assert "YARN_YARN_OFFLINE_MIRROR" not in os.environ
        warn.assert_called_once()


def _provision(yarn_offline_mirror=None):
    """
    Run `provision` with the Node.js and npm handling mocked away. csspin has
    resolved and typed `yarn_offline_mirror` by the time `provision` runs.
    """
    cfg_mock = mock.MagicMock()
    cfg_mock.verbosity = csspin.Verbosity.NORMAL
    cfg_mock.node.yarn_offline_mirror = (
        None if yarn_offline_mirror is None else Path(yarn_offline_mirror)
    )
    with (
        mock.patch("csspin_frontend.node.setenv"),
        mock.patch("csspin_frontend.node._get_npm_version"),
        mock.patch("csspin_frontend.node._install_requirements"),
    ):
        provision(cfg_mock)


@pytest.mark.usefixtures("isolated_env")
class TestProvisionYarnOfflineMirror:
    """Tests for the check of the mirror directory in `provision`."""

    def test_aborts_for_missing_directory(self, tmp_path, capsys):
        """
        `provision` stops with a message that names the property and the path,
        and does not create the directory. The path holds braces, which `die`
        interpolates unless told otherwise, so the message has to arrive
        verbatim.
        """
        mirror = Path(tmp_path) / "{offline}"
        with pytest.raises(Abort):
            _provision(mirror)
        message = capsys.readouterr().err
        assert message.endswith(
            f"node.yarn_offline_mirror is not an existing directory: {mirror}\n"
        )
        assert not mirror.exists()

    def test_accepts_existing_directory(self, tmp_path):
        """
        `provision` leaves an existing mirror directory and its tarballs as
        they are.
        """
        mirror = Path(tmp_path) / "offline"
        mirror.mkdir()
        (mirror / "left-pad-1.3.0.tgz").touch()
        _provision(mirror)
        assert [entry.name for entry in mirror.iterdir()] == ["left-pad-1.3.0.tgz"]

    def test_ignores_missing_directory_for_yarn_berry(self, tmp_path):
        """
        `configure` clears the property for Yarn Berry, so a mirror directory
        that does not exist does not stop `provision`.
        """
        with mock.patch("csspin_frontend.node.warn"):
            cfg = _configure(
                umbrella="2027.1",
                yarn_offline_mirror=str(tmp_path / "offline"),
                project_root=Path(tmp_path),
            )
        _provision(cfg.node.yarn_offline_mirror)
        assert not (tmp_path / "offline").exists()


@pytest.mark.parametrize(
    "sys_platform, machine, expected",
    (
        ("linux", "x86_64", ("node-v22.17.1-linux-x64", ".tar.xz")),
        ("linux", "aarch64", ("node-v22.17.1-linux-arm64", ".tar.xz")),
        ("linux", "armv7l", ("node-v22.17.1-linux-armv7l", ".tar.xz")),
        ("darwin", "x86_64", ("node-v22.17.1-darwin-x64", ".tar.xz")),
        ("darwin", "arm64", ("node-v22.17.1-darwin-arm64", ".tar.xz")),
        ("win32", "AMD64", ("node-v22.17.1-win-x64", ".zip")),
        ("win32", "ARM64", ("node-v22.17.1-win-arm64", ".zip")),
    ),
)
def test__node_archive_name(sys_platform, machine, expected):
    """
    Check whether the Node.js archive matching the platform and machine
    architecture is chosen.
    """
    with (
        mock.patch("csspin_frontend.node.sys.platform", sys_platform),
        mock.patch("csspin_frontend.node.platform.machine", return_value=machine),
    ):
        assert _node_archive_name("v22.17.1") == expected
