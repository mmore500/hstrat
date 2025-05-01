import numpy as np
import pytest
from scipy.special import expit

from hstrat._auxiliary_lib._fit_fblr import fit_fblr


@pytest.mark.parametrize(
    "n_samples, min_corr",
    [
        (10, 0.4),  # very noisy -> weak positive correlation
        (50, 0.6),  # small -> moderate correlation
        (500, 0.8),  # medium -> strong correlation
        (5000, 0.95),  # large -> very strong correlation
    ],
)
def test_beta_estimate_correlation_across_slopes(
    n_samples: int, min_corr: float
):
    """
    For each sample size, generate many different true slopes beta,
    simulate y ~ Bernoulli(expit(X * beta)), fit logistic regression
    (no intercept), and check that the Pearson correlation between
    [beta_true] and [beta_estimated] exceeds min_corr.
    """
    rng = np.random.RandomState(0)

    # choose a grid of true betas to span weak to strong effects
    true_betas = np.linspace(-3.0, 5.0, 12)

    est_betas = []
    for beta in true_betas:
        # simulate
        X = rng.randn(n_samples, 1)
        logits = X.flatten() * beta
        y = rng.binomial(1, expit(logits))

        # fit
        w = fit_fblr(
            X_train=X,
            y_train=y,
            fit_intercept=False,
        )
        assert w.shape == (1,)
        est_betas.append(w[0])

    corr_matrix = np.corrcoef(true_betas, est_betas)
    corr = corr_matrix[0, 1]

    assert corr >= min_corr
