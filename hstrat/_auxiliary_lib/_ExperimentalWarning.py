class ExperimentalWarning(UserWarning):
    """Warning category for experimental functionality, whose interface and
    results can change in the future.

    Silence it by setting the environment variable
    `HSTRAT_WARN_EXPERIMENTAL_SUPPRESS`, or by filtering this category,
    e.g., `warnings.filterwarnings("ignore", category=ExperimentalWarning)`.

    See Also
    --------
    warn_experimental :
        Decorator that issues this warning when a function is called.
    """
