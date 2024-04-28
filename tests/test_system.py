import subprocess
import platform
from unittest.mock import patch, MagicMock
import pytest
from src.core.system import (
    get_last_boot_time,
    get_system_uptime,
    get_user_count_unix,
    get_system_info,
)


# # Test get_last_boot_time_macos
# @pytest.mark.parametrize(
#     "output,expected",
#     [
#         ("{ sec = 1625097600, usec = 0 }", 1625097600.0),  # ID: valid-output
#         ("", 0.0),  # ID: empty-output
#         ("invalid output", 0.0),  # ID: invalid-output
#     ],
#     ids=["valid-output", "empty-output", "invalid-output"],
# )
# def test_get_last_boot_time_macos(output, expected):
#     with patch("subprocess.run") as mocked_run:
#         mocked_run.return_value = MagicMock(stdout=output)

#         # Act
#         result = get_last_boot_time_macos()

#         # Assert
#         assert result == expected


# # Test get_system_uptime
# @pytest.mark.parametrize("output,expected", [
#     ("13:05  up 3 days, 18:53, 5 users", "13:05  up 3 days,  18:53"),  # ID: normal-case
#     ("", ""),  # ID: empty-output
#     ("uptime: unexpected output", "uptime: unexpected output"),  # ID: unexpected-output
# ], ids=["normal-case", "empty-output", "unexpected-output"])
# def test_get_system_uptime(output, expected):
#     with patch("subprocess.run") as mocked_run:
#         mocked_run.return_value = MagicMock(stdout=output)

#         # Act
#         result = get_system_uptime()

#         # Assert
#         assert result == expected

@pytest.mark.skipif(platform.system() != "Darwin", reason="Running on non-Darwin system")
def test_get_last_boot_time_darwin():
    with patch("platform.system", return_value="Darwin"), patch(
        "subprocess.run", return_value=MagicMock(stdout="kern.boottime = { sec = 1625097600, usec = 0 } Mon Jun  1 00:00:00 2020")
    ):
        assert get_last_boot_time() == 1625097600.0

    with patch("platform.system", return_value="Darwin"), patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "sysctl")
    ):
        assert get_last_boot_time() == 0.0

@pytest.mark.skipif(platform.system() != "Linux", reason="Running on non-Linux system")
def test_get_last_boot_time_linux():
    with patch("platform.system", return_value="Linux"), patch(
        "subprocess.run", return_value=MagicMock(stdout="2020-06-01 00:00:00")
    ):
        assert get_last_boot_time() == 1590969600.0

    with patch("platform.system", return_value="Linux"), patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "uptime")
    ):
        assert get_last_boot_time() == 0.0


@pytest.mark.skipif(platform.system() != "Linux", reason="Running on non-Linux system")
def test_get_system_uptime_linux():
    with patch("platform.system", return_value="Linux"), patch(
        "os.stat", return_value=MagicMock(st_ctime=1000)
    ), patch("time.time", return_value=2000):
        assert get_system_uptime() == "0 days, 0 hours, 16 minutes"

    with patch("platform.system", return_value="Linux"), patch(
        "os.stat", side_effect=Exception("Error")
    ):
        assert get_system_uptime() == "Error in obtaining uptime"


@pytest.mark.skipif(
    platform.system() != "Darwin", reason="Running on non-Darwin system"
)
def test_get_system_uptime_darwin():
    with patch("platform.system", return_value="Darwin"), patch(
        "subprocess.run", return_value=MagicMock(stdout="10:00 up 1 day, 2:00")
    ):
        assert get_system_uptime() == "10:00 up 1 day,  2:00"

    with patch("platform.system", return_value="Darwin"), patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "uptime")
    ):
        assert get_system_uptime() == "Error in obtaining uptime"


# Test get_user_count_unix
@pytest.mark.parametrize(
    "path,dirs,expected",
    [
        ("/Users", ["user1", "Shared", "user2"], 2),  # ID: normal-case
        ("/invalid/path", [], 0),  # ID: invalid-path
    ],
    ids=["normal-case", "invalid-path"],
)
def test_get_user_count_unix(path, dirs, expected):
    with patch("os.listdir") as mocked_listdir, patch("os.path.isdir") as mocked_isdir:
        mocked_listdir.return_value = dirs
        mocked_isdir.side_effect = lambda x: x != "/invalid/path"

        # Act
        result = get_user_count_unix(path)

        # Assert
        assert result == expected


# TODO: test is currently missing uptime and last_boot_time
@pytest.mark.parametrize(
    "os_type,expected_keys",
    [
        (
            "Linux",
            [
                "os_type",
                "hostname",
                "kernel_info",
                "architecture",
                "dist",
                "dist_version",
                "users_nb",
                "current_date",
            ],
        ),  # ID: linux
        (
            "Darwin",
            [
                "os_type",
                "hostname",
                "kernel_info",
                "architecture",
                "dist",
                "dist_version",
                "users_nb",
                "current_date",
            ],
        ),  # ID: darwin
    ],
    ids=["linux", "darwin"],
)
def test_get_system_info(os_type, expected_keys):

    with patch("platform.system", return_value=os_type), patch(
        "platform.node", return_value="test_hostname"
    ), patch("platform.uname", return_value=MagicMock(release="test_release")), patch(
        "platform.machine", return_value="test_machine"
    ), patch(
        "platform.mac_ver", return_value=("10.15.1", "", "")
    ), patch(
        "os.listdir"
    ), patch(
        "os.path.isdir", return_value=True
    ), patch(
        "time.time", return_value=1625097600
    ), patch(
        "distro.name", return_value="Ubuntu"
    ), patch(
        "distro.version", return_value="20.04"
    ):

        # Act
        result = get_system_info()

        # Assert
        for key in expected_keys:
            assert key in result
