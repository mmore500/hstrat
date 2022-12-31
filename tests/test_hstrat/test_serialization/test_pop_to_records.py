import json
import random

import pytest

from hstrat import genome_instrumentation, hstrat


@pytest.mark.parametrize(
    "impl",
    [genome_instrumentation.HereditaryStratigraphicColumn],
    # TODO
    # genome_instrumentation._HereditaryStratigraphicColumn_.impls,
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
        None,
    ],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 8, 16, 32, 64],
)
@pytest.mark.parametrize(
    "popsize",
    [0, 1, 8],
)
def test_col_to_records(
    impl,
    retention_policy,
    ordered_store,
    differentia_bit_width,
    popsize,
):

    pop = [
        impl(
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(popsize)
    ]
    for _ in range(100):
        random.shuffle(pop)
        if pop:
            pop[0] = pop[-1].CloneDescendant()

    print(hstrat.pop_to_records(pop))

    assert hstrat.pop_to_records(pop) == hstrat.pop_to_records(pop)
    records = hstrat.pop_to_records(pop)
    for field in (
        "policy",
        "policy_algo",
        "policy_spec",
        "differentia_bit_width",
        "hstrat_version",
    ):
        assert field in records
        assert not any(field in col_rec for col_rec in records["columns"])

    reconstituted = hstrat.pop_from_records(records)
    if (
        ordered_store == hstrat.HereditaryStratumOrderedStoreList
        and impl == genome_instrumentation.HereditaryStratigraphicColumn
    ):
        assert reconstituted == pop
    else:
        assert hstrat.pop_to_records(reconstituted) == hstrat.pop_to_records(
            pop
        )

    records = hstrat.pop_to_records(pop)
    json_str = json.dumps(records)
    reconstituted = hstrat.pop_from_records(json.loads(json_str))
    if (
        ordered_store == hstrat.HereditaryStratumOrderedStoreList
        and impl == genome_instrumentation.HereditaryStratigraphicColumn
    ):
        assert reconstituted == pop
    else:
        assert hstrat.pop_to_records(reconstituted) == hstrat.pop_to_records(
            pop
        )
