import pickle
import tempfile

import pytest

from hstrat.hstrat import pseudostochastic_algo


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(hash_salt):
    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    assert spec == spec
    assert spec == pseudostochastic_algo.PolicySpec(hash_salt)
    assert not spec == pseudostochastic_algo.PolicySpec(hash_salt + 1)


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetEvalCtor(hash_salt):
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith("hstrat.pseudostochastic_algo.PolicySpec(")
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)  # noqa
    assert spec == reconstituted


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(hash_salt):
    original = pseudostochastic_algo.PolicySpec(hash_salt)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "hash_salt",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetHashSalt(hash_salt):
    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    assert spec.GetHashSalt() == hash_salt


def test_GetAlgoIdentifier():
    hash_salt = 1
    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    hash_salt = 1
    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    assert spec.GetAlgoTitle()


def test_repr():
    hash_salt = 1
    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    assert str(hash_salt) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    hash_salt = 1
    spec = pseudostochastic_algo.PolicySpec(hash_salt)
    assert str(hash_salt) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
