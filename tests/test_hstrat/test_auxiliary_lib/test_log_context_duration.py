import time

import more_itertools as mit
import pandas as pd

from hstrat._auxiliary_lib import log_context_duration


def test_log_context_duration():
    log = []
    with log_context_duration("my_test_context", logger=log.append):
        time.sleep(0.05)

    logged_message = mit.one(log)
    assert "my_test_context" in logged_message

    timing_records = {
        k: v
        for line in logged_message.splitlines()
        if line.startswith("!!!")
        for k, v in eval(line.strip().removeprefix("!!!")).items()
    }
    timing_results = pd.DataFrame(
        {
            "what": timing_records.keys(),
            "duration (s)": timing_records.values(),
        },
    ).astype(
        {
            "what": str,
            "duration (s)": float,
        },
    )
    assert len(timing_results) == 1
    assert timing_results.at[0, "what"] == "my_test_context"
    assert timing_results.at[0, "duration (s)"] > 0
