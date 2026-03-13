import argparse

from hstrat._auxiliary_lib import add_bool_arg


def test_default_false():
    parser = argparse.ArgumentParser()
    add_bool_arg(parser, "foo")
    args = parser.parse_args([])
    assert args.foo is False


def test_default_true():
    parser = argparse.ArgumentParser()
    add_bool_arg(parser, "foo", default=True)
    args = parser.parse_args([])
    assert args.foo is True


def test_flag_true():
    parser = argparse.ArgumentParser()
    add_bool_arg(parser, "foo")
    args = parser.parse_args(["--foo"])
    assert args.foo is True


def test_flag_false():
    parser = argparse.ArgumentParser()
    add_bool_arg(parser, "foo", default=True)
    args = parser.parse_args(["--no-foo"])
    assert args.foo is False


def test_hyphenated_name():
    parser = argparse.ArgumentParser()
    add_bool_arg(parser, "my-flag", default=False)
    args = parser.parse_args(["--my-flag"])
    assert args.my_flag is True
    args = parser.parse_args(["--no-my-flag"])
    assert args.my_flag is False


def test_multiple_flags():
    parser = argparse.ArgumentParser()
    add_bool_arg(parser, "insert", default=True)
    add_bool_arg(parser, "delete", default=True)
    add_bool_arg(parser, "update", default=True)

    args = parser.parse_args(["--no-insert"])
    assert args.insert is False
    assert args.delete is True
    assert args.update is True

    args = parser.parse_args(["--no-insert", "--no-update"])
    assert args.insert is False
    assert args.delete is True
    assert args.update is False
