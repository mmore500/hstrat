import logging

from hstrat._auxiliary_lib import begin_prod_logging, get_hstrat_version


def test_smoke():
    begin_prod_logging()


def test_logs_version(caplog):
    with caplog.at_level(logging.INFO):
        begin_prod_logging()

    assert any(
        get_hstrat_version() in record.message for record in caplog.records
    )
