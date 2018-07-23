#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `comeon_core` package."""

import pytest

from comeon_core import comeon_core
from comeon_core import init_db, update
#from comeon_core import comeon_core


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_package(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    
   # from comeon_core import update
    init_db()
    update()
    assert True 

