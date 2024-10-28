#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import pytest
from k8s_test_harness.util import docker_util, env_util

# In the future, we may also test ARM
IMG_PLATFORM = "amd64"
IMG_NAME = "pinniped-server"

EXPECTED_FILES = [
    "/usr/local/bin/pinniped-server",
    "/usr/local/bin/pinniped-concierge-kube-cert-agent",
    "/usr/local/bin/pinniped-concierge",
    "/usr/local/bin/pinniped-supervisor",
    "/usr/local/bin/local-user-authenticator",
]

EXPECTED_HELPSTR = "pinniped-concierge provides a generic API for mapping "


@pytest.mark.parametrize("version", ["v0.30.0"])
def test_pinniped(version: str):
    rock = env_util.get_build_meta_info_for_rock_version(
        IMG_NAME, version, IMG_PLATFORM
    )

    docker_run = docker_util.run_in_docker(
        rock.image, ["/usr/local/bin/pinniped-concierge", "--help"]
    )
    assert EXPECTED_HELPSTR in docker_run.stdout

    # check rock filesystem
    docker_util.ensure_image_contains_paths_bare(rock.image, EXPECTED_FILES)
