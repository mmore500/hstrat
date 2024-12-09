import pytest

from hstrat._auxiliary_lib import except_wrap_sentinel


def test_except_wrap_sentinel():
    def fail_division(a, b):
        assert a != 0
        return a / b

    # Wrap the function to return `float('inf')` on ZeroDivisionError
    safe_divide = except_wrap_sentinel(
        fail_division,
        {
            ZeroDivisionError: "Division by zero!",
            AssertionError: "Division with zero!",
        },
        sentinel=float("inf"),
    )

    # Test that dividing by zero returns sentinel and emits a warning
    with pytest.warns(UserWarning, match="Division by zero!"):
        assert safe_divide(1, 0) == float("inf")

    # Test that a different error type has its corresponding warning
    with pytest.warns(UserWarning, match="Division with zero!"):
        assert safe_divide(0, 2) == float("inf")

    # Test a successful division returns the correct result
    assert safe_divide(4, 2) == 2.0

    # Test that another exception not in errors is still raised
    with pytest.raises(TypeError):
        safe_divide("4", "2")
