from hstrat._auxiliary_lib import GetAttrLaunderShim


def test_GetAttrLaunderShim_dummy1():
    pass


def test_GetAttrLaunderShim_dummy2():
    pass


def test_GetAttrLaunderShim():
    shim = GetAttrLaunderShim(
        globals().__getitem__,  # current module
        ["test_GetAttrLaunderShim_dummy1"].__contains__,
        "foobar",
    )
    a = shim("test_GetAttrLaunderShim_dummy1")
    assert a.__module__ == "foobar"

    b = shim("test_GetAttrLaunderShim_dummy2")
    assert b.__module__ == test_GetAttrLaunderShim.__module__
