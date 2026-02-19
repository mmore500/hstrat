import os
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_mark_clade_subtended_duration_ratio_sister_asexual_cli_help():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_clade_subtended_duration_ratio_sister_asexual",
            "--help",
        ],
        check=True,
    )


def test_alifestd_mark_clade_subtended_duration_ratio_sister_asexual_cli_version():
    subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat._auxiliary_lib._alifestd_mark_clade_subtended_duration_ratio_sister_asexual",
            "--version",
        ],
        check=True,
    )
