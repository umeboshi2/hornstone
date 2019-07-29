#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `hornstone` package."""

import io
import pytest

from hornstone.base import get_sha256sum, get_sha256sum_string
from hornstone.base import trailing_slash, remove_trailing_slash


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


hello_hash = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_hello_file():
    hfile = io.BytesIO(b'hello')
    fhash = get_sha256sum(hfile)
    assert fhash == hello_hash


def test_hash_hello_string():
    hello = b'hello'
    fhash = get_sha256sum_string(hello)
    assert fhash == hello_hash


def test_trailing_slash():
    u = 'hello/'
    res = trailing_slash(u)
    assert res == u


def test_trailing_slash_needed():
    u = 'hello'
    res = trailing_slash(u)
    assert res == 'hello/'


def test_rm_slash1():
    u = "end/"
    res = remove_trailing_slash(u)
    assert res == "end"


def test_rm_slash2():
    u = "end"
    res = remove_trailing_slash(u)
    assert res == "end"


def test_rm_slash3():
    u = "end/////"
    res = remove_trailing_slash(u)
    assert res == "end"
