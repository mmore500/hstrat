import numpy as np

from ._jit import jit


@jit(nopython=True, nogil=True, cache=True)
def _fit_fblr(
    X_train: np.ndarray,
    y_train: np.ndarray,
    fit_intercept: bool,
    epsilon: float,
    lambda_ssr: float,
    f: float,
    gamma: float,
    convergenceTolerance: float,
    minimumIteration: int,
    maximumIteration: int,
    warnConvergence: bool,
) -> np.ndarray:
    """Implementation detail."""

    # adapted from
    # https://github.com/NurdanS/fblr/blob/241db04b0d200834407f363c12483dd553bcbf55/customClassifier.py

    if fit_intercept:
        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))

    n = X_train.shape[0]
    d = X_train.shape[1]

    I = np.identity(d)  # noqa: E741

    beta = 1e-8
    A = (X_train.T).dot(X_train) + beta * I
    b = (X_train.T).dot(y_train)
    w_0 = np.linalg.solve(A, b)

    doRegularization = lambda_ssr > 0 or gamma > 0

    log2 = np.log(2.0)
    q = 0.5

    v = (1 / n) * (X_train.T).dot(y_train - q)

    w = w_0.copy()
    for iteration in range(maximumIteration + 1):
        w_hat = w.copy()

        o = X_train.dot(w_hat)
        z = (np.log(1.0 + np.exp(o)) - log2 - 0.5 * o) / (o * o + epsilon)

        # weight update
        if doRegularization:
            p = np.ones(d)
            # if interceptColumnIndex >= 0 and interceptColumnIndex < d:
            #     p[interceptColumnIndex] = 0

            h = p / (np.abs(w_hat) ** (2 - f) + epsilon)
            H = np.diag(h.flatten())

            # A = (2/n) * (X_train.T Z X_train) + (lambda_ssr/d)*I + (gamma/d)*H
            A = (
                (2 / n) * np.multiply(z, X_train.T).dot(X_train)
                + (lambda_ssr / d) * I
                + (gamma / d) * H
            )
            b = (lambda_ssr / d) * w + v
            w = np.linalg.solve(A, b)
        else:
            # A = (2/n) * (X_train.T Z X_train)
            A = (2 / n) * np.multiply(z, X_train.T).dot(X_train)
            w = np.linalg.solve(A, v)

        change = np.max(np.abs(w - w_hat))
        if iteration >= minimumIteration and change <= convergenceTolerance:
            break
    else:
        if warnConvergence:
            print(
                "warning: maximum number of fblr iterations reached without "
                "convergence.",
            )

    return w


def fit_fblr(
    X_train: np.ndarray,
    y_train: np.ndarray,
    *,
    fit_intercept: bool = False,
    epsilon: float = 1e-10,
    lambda_ssr: float = 0,
    f: float = 0,
    gamma: float = 0.001,
    convergenceTolerance: float = 1e-3,
    minimumIteration: int = 2,
    maximumIteration: int = 10,
    warnConvergence: bool = True,
) -> np.ndarray:
    """Fit a logistic regression model using the Fast Binary Logistic
    Regression (FBLR) algorithm proposed by Saran and Nar (2025).

    Parameters
    ----------
    X_train : np.ndarray
        The input data, shape (n_samples, n_features).
    y_train : np.ndarray
        The target values, shape (n_samples,).
    fit_intercept : bool, default False
        Whether to include an intercept term in the model.
    epsilon : float, default 1e-10
        A small value to prevent division by zero.
    lambda_ssr : float, default 0
        Slow-step-regularization (SSR) parameter.
    f : float, default 0
        Regularization parameter for L_f norm penalty.
    gamma : float, default 0.001
        Regulariation parameter.
    convergenceTolerance : float, default 1e-3
        The tolerance for convergence.
    minimumIteration : int, default 2
        The minimum number of iterations to perform.
    maximumIteration : int, default 10
        The maximum number of iterations to perform.
    warnConvergence : bool, default True
        Whether to issue a warning if the maximum number of iterations is
        reached without convergence.

    Returns
    -------
    np.ndarray
        The estimated coefficients of the logistic regression model.

        If `fit_intercept` is True, the first element corresponds to the
        intercept term, and the remaining elements correspond to the
        coefficients for each feature in `X_train`. If `fit_intercept` is
        False, all elements correspond to the coefficients for each feature
        in `X_train`.

    Notes
    -----
    Anecdotally, approximations by this alborithm appear to systematically
    underestimate the true slope of the logistic regression line. However, they
    are still useful for estimating the sign and magnitude of the slope, and
    the algorithm is much faster than the standard logistic regression
    algorithm.

    References
    ----------
    Saran NA, Nar F. 2025. Fast binary logistic regression. PeerJ Computer
        Science 11:e2579 https://doi.org/10.7717/peerj-cs.2579
    """

    X_train = np.asarray(X_train, dtype=np.float64)
    y_train = np.asarray(y_train, dtype=np.float64)

    # handle simple singular case
    if np.ptp(X_train) < 1e-6:
        return np.zeros(X_train.shape[1])

    return _fit_fblr(
        X_train,
        y_train,
        fit_intercept=fit_intercept,
        epsilon=epsilon,
        lambda_ssr=lambda_ssr,
        f=f,
        gamma=gamma,
        convergenceTolerance=convergenceTolerance,
        minimumIteration=minimumIteration,
        maximumIteration=maximumIteration,
        warnConvergence=warnConvergence,
    )
