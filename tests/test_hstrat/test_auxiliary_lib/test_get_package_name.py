from hstrat._auxiliary_lib import get_package_name


def test_get_package_name():
    assert get_package_name("baz") == ""
    assert get_package_name("foo.bar") == "foo"
    assert get_package_name("foo.baz.bar") == "foo.baz"
