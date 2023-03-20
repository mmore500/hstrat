import sys


def is_in_coverage_run():
    """Check whether test is run with coverage."""
    gettrace = getattr(sys, "gettrace", None)

    if gettrace is None:  # pragma: no cover
        return False
    else:
        gettrace_result = gettrace()

    try:
        from coverage.pytracer import PyTracer
        from coverage.tracer import CTracer

        if isinstance(gettrace_result, (CTracer, PyTracer)):
            return True
    except ImportError:  # pragma: no cover
        pass

    return False  # pragma: no cover
