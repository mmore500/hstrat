import pandas as pd
import pytest

from hstrat._auxiliary_lib import alifestd_convert_root_ancestor_token


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("token", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_empty(mutate, token):
    ancestor_list_series = pd.Series(dtype=str)
    expected_output = pd.Series(dtype=str)
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, token, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_singleton(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series([f"[{tokenfrom}]"])
    expected_output = pd.Series([f"[{tokento}]"])
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_single_root1(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series([f"[{tokenfrom}]", "[0]", "[0,1]"])
    expected_output = pd.Series([f"[{tokento}]", "[0]", "[0,1]"])
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_single_root2(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series(["[1]", f"[{tokenfrom}]", "[1]"])
    expected_output = pd.Series(["[1]", f"[{tokento}]", "[1]"])
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_multiple_roots1(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series(
        [f"[{tokenfrom}]", f"[{tokenfrom}]", "[1]"]
    )
    expected_output = pd.Series([f"[{tokento}]", f"[{tokento}]", "[1]"])
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_multiple_roots2(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series(
        [f"[{tokenfrom}]", f"[{tokenfrom}]", "[0, 1]"]
    )
    expected_output = pd.Series([f"[{tokento}]", f"[{tokento}]", "[0, 1]"])
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_multiple_roots3(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series(
        [f"[{tokenfrom}]", "[0, 1]", f"[{tokenfrom}]"]
    )
    expected_output = pd.Series([f"[{tokento}]", "[0, 1]", f"[{tokento}]"])
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize("mutate", [True, False])
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_multiple_roots4(
    mutate, tokenfrom, tokento
):
    ancestor_list_series = pd.Series(
        [f"[{tokenfrom}]", f"[{tokenfrom}]", f"[{tokenfrom}]"]
    )
    expected_output = pd.Series(
        [f"[{tokento}]", f"[{tokento}]", f"[{tokento}]"]
    )
    output = alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=mutate
    )
    pd.testing.assert_series_equal(output, expected_output)


@pytest.mark.parametrize(
    "subject",
    [
        "pd.Series(dtype=str)",
        'pd.Series([f"[{tokenfrom}]"])',
        'pd.Series([f"[{tokenfrom}]", "[0]", "[0,1]"])',
        'pd.Series(["[1]", f"[{tokenfrom}]", "[1]"])',
        'pd.Series([f"[{tokenfrom}]", f"[{tokenfrom}]", "[1]"])',
        'pd.Series([f"[{tokenfrom}]", f"[{tokenfrom}]", "[0, 1]"])',
        'pd.Series([f"[{tokenfrom}]", f"[{tokenfrom}]", f"[{tokenfrom}]"])',
        'pd.Series([f"[{tokenfrom}]", "[0, 1]", f"[{tokenfrom}]"])',
    ],
)
@pytest.mark.parametrize("tokenfrom", ["none", "None", ""])
@pytest.mark.parametrize("tokento", ["none", "None", ""])
def test_alifestd_convert_root_ancestor_token_with_multiple_roots5(
    subject, tokenfrom, tokento
):
    ancestor_list_series = eval(subject)
    alifestd_convert_root_ancestor_token(
        ancestor_list_series, tokento, mutate=False
    )
    pd.testing.assert_series_equal(ancestor_list_series, eval(subject))
