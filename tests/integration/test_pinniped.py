#
# Copyright 2024 Canonical, Ltd.
# See LICENSE file for licensing details
#

import pytest
from k8s_test_harness import harness
from k8s_test_harness.util import constants, env_util, k8s_util

IMG_PLATFORM = "amd64"
INSTALL_NAME = "pinniped"


@pytest.mark.parametrize("version", ["v0.30.0"])
def test_pinniped(function_instance: harness.Instance, version: str):
    rock = env_util.get_build_meta_info_for_rock_version(
        "pinniped-server", version, IMG_PLATFORM
    )

    # This helm chart requires the registry to be separated from the image.
    rock_image = rock.image
    registry = "docker.io"
    parts = rock_image.split("/")
    if len(parts) > 1:
        registry = parts[0]
        rock_image = "/".join(parts[1:])

    helm_command = k8s_util.get_helm_install_command(
        name=INSTALL_NAME,
        chart_name="oci://registry-1.docker.io/bitnamicharts/pinniped",
        images=[k8s_util.HelmImage(uri=rock_image)],
        namespace=constants.K8S_NS_KUBE_SYSTEM,
        set_configs=[f"image.registry={registry}"],
    )
    function_instance.exec(helm_command)

    k8s_util.wait_for_deployment(
        function_instance, "pinniped-concierge", constants.K8S_NS_KUBE_SYSTEM
    )

    k8s_util.wait_for_deployment(
        function_instance, "pinniped-supervisor", constants.K8S_NS_KUBE_SYSTEM
    )

    for name in ["pinniped-concierge", "pinniped-supervisor"]:
        # Sanity check: make sure there isn't an error in Pebble that it couldn't start the service.
        process = function_instance.exec(
            [
                "k8s",
                "kubectl",
                "logs",
                "-n",
                constants.K8S_NS_KUBE_SYSTEM,
                f"{constants.K8S_DEPLOYMENT}/{name}",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        assert '(Start service "pinniped") failed' not in process.stdout
