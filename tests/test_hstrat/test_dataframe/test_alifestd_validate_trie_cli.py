import os
import pathlib
import subprocess

assets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def test_alifestd_validate_trie_cli_help():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.alifestd_validate_trie",
            "--help",
        ],
        check=True,
    )


def test_alifestd_validate_trie_cli_version():
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.alifestd_validate_trie",
            "--version",
        ],
        check=True,
    )


def test_alifestd_validate_trie_cli_pipe_from_unpack_reconstruct():
    trie_file = (
        "/tmp/hstrat_validate_trie_unpack.pqt"  # nosec B108
    )
    output_file = (
        "/tmp/hstrat_validate_trie_output.pqt"  # nosec B108
    )
    pathlib.Path(trie_file).unlink(missing_ok=True)
    pathlib.Path(output_file).unlink(missing_ok=True)

    # first, unpack reconstruct with --no-drop-dstream-metadata
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            trie_file,
            "--no-drop-dstream-metadata",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(trie_file)

    # then, validate the trie output
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.alifestd_validate_trie",
            output_file,
        ],
        check=True,
        input=trie_file.encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_validate_trie_cli_csv():
    trie_file = (
        "/tmp/hstrat_validate_trie_unpack.csv"  # nosec B108
    )
    output_file = (
        "/tmp/hstrat_validate_trie_output.csv"  # nosec B108
    )
    pathlib.Path(trie_file).unlink(missing_ok=True)
    pathlib.Path(output_file).unlink(missing_ok=True)

    # first, unpack reconstruct with --no-drop-dstream-metadata
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            trie_file,
            "--no-drop-dstream-metadata",
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(trie_file)

    # then, validate the trie output
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.alifestd_validate_trie",
            output_file,
        ],
        check=True,
        input=trie_file.encode(),
    )
    assert os.path.exists(output_file)


def test_alifestd_validate_trie_cli_fails_without_metadata():
    """Validate CLI fails when dstream metadata is dropped (default)."""
    trie_file = (
        "/tmp/hstrat_validate_trie_no_meta.pqt"  # nosec B108
    )
    output_file = (
        "/tmp/hstrat_validate_trie_no_meta_out.pqt"  # nosec B108
    )
    pathlib.Path(trie_file).unlink(missing_ok=True)
    pathlib.Path(output_file).unlink(missing_ok=True)

    # unpack reconstruct with default metadata dropping
    subprocess.run(
        [
            "python3",
            "-m",
            "hstrat.dataframe.surface_unpack_reconstruct",
            trie_file,
        ],
        check=True,
        input=f"{assets}/packed.csv".encode(),
    )
    assert os.path.exists(trie_file)

    # validation should fail due to missing columns
    result = subprocess.run(  # nosec B603
        [
            "python3",
            "-m",
            "hstrat.dataframe.alifestd_validate_trie",
            output_file,
        ],
        input=trie_file.encode(),
    )
    assert result.returncode != 0
