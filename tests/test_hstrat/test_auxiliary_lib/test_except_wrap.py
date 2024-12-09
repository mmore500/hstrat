import pytest

from hstrat._auxiliary_lib import except_wrap


def test_except_wrap():
    def fail_division(a, b):
        return a / b

    # Wrap the function to return `float('inf')` on ZeroDivisionError
    safe_divide = except_wrap(
        fail_division,
        {ZeroDivisionError: "Division by zero!"},
        sentinel=float("inf"),
    )

    # Test that dividing by zero returns sentinel and emits a warning
    with pytest.warns(UserWarning, match="Division by zero!"):
        assert safe_divide(1, 0) == float("inf")

    # Test a successful division returns the correct result
    assert safe_divide(4, 2) == 2.0

    # Test that another exception not in errors is still raised
    with pytest.raises(TypeError):
        safe_divide("4", "2")
