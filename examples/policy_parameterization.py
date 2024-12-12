#!/usr/bin/env python3

from hstrat import hstrat

if __name__ == "__main__":

    for target_exact_absolute_mrca_uncertainty in (8, 127):
        for algo in (
            hstrat.geom_seq_nth_root_tapered_algo,
            hstrat.fixed_resolution_algo,
            hstrat.recency_proportional_resolution_algo,
        ):
            print("stratum retention algorithm", algo.__name__)
            print(f"{target_exact_absolute_mrca_uncertainty=}")

            stratum_retention_policy = algo.Policy(
                parameterizer=hstrat.PropertyAtMostParameterizer(
                    target_value=target_exact_absolute_mrca_uncertainty,
                    policy_evaluator=hstrat.MrcaUncertaintyAbsExactEvaluator(
                        at_num_strata_deposited=256,
                        at_rank=0,
                    ),
                    param_lower_bound=1,
                    param_upper_bound=1024,
                ),
            )
            print("   parameterized policy", stratum_retention_policy)

            provided_exact_absolute_mrca_uncertainty = (
                stratum_retention_policy.CalcMrcaUncertaintyAbsExact(
                    first_num_strata_deposited=256,
                    second_num_strata_deposited=256,
                    actual_rank_of_mrca=0,
                )
            )
            print(f"   {provided_exact_absolute_mrca_uncertainty=}")
            print()
