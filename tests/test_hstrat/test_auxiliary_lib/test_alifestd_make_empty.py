from hstrat._auxiliary_lib import alifestd_make_empty, alifestd_validate


def test_alifestd_make_empty():
    assert len(alifestd_make_empty()) == 0
    assert alifestd_validate(alifestd_make_empty())
    assert "id" in alifestd_make_empty()
    assert "ancestor_list" in alifestd_make_empty()
