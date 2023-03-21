from hstrat._auxiliary_lib import render_to_base64url


def test_render_to_base64url():
    assert render_to_base64url(163) == "Cj"
    assert render_to_base64url(63) == "_"
    assert render_to_base64url(62) == "-"
    assert render_to_base64url(42) == "q"
    assert render_to_base64url(7) == "H"
    assert render_to_base64url(0) == "A"
