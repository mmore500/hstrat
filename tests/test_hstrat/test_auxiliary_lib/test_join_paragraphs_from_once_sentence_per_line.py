from hstrat._auxiliary_lib import join_paragraphs_from_one_sentence_per_line


def test_single_sentence_per_line():
    text = "This is a sentence.\nThis is another one."
    expected = "This is a sentence. This is another one."
    assert join_paragraphs_from_one_sentence_per_line(text) == expected


def test_multiple_paragraphs():
    text = "First paragraph sentence one.\nFirst paragraph sentence two.\n\nSecond paragraph sentence one.\nSecond paragraph sentence two."
    expected = "First paragraph sentence one. First paragraph sentence two. \nSecond paragraph sentence one. Second paragraph sentence two."
    assert join_paragraphs_from_one_sentence_per_line(text) == expected


def test_no_newlines():
    text = "This is a sentence. This is another one."
    expected = "This is a sentence. This is another one."
    assert join_paragraphs_from_one_sentence_per_line(text) == expected


def test_empty_input():
    text = ""
    expected = ""
    assert join_paragraphs_from_one_sentence_per_line(text) == expected


def test_newline_at_end():
    text = "This is a sentence.\n"
    expected = "This is a sentence. "
    assert join_paragraphs_from_one_sentence_per_line(text) == expected
