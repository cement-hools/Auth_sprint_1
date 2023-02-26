"""Fixtures"""
import asyncio

import aiohttp
import pytest
from multidict import CIMultiDictProxy

from fastapi_tests.functional.settings import test_settings

pytest_plugins = (
    "functional.fixtures.elastic",
    "functional.fixtures.async_http",
)


def pytest_configure():
    pytest.strange_unicode_str = "\uFFFF~𝘈Ḇ𝖢𝕯٤ḞԍНǏ𝙅ƘԸⲘ𝙉০Ρ𝗤Ɍ𝓢ȚЦ𝒱Ѡ𝓧ƳȤѧᖯć𝗱ễ𝑓𝙜Ⴙ𝞲𝑗𝒌ļṃŉо𝞎𝒒ᵲꜱ𝙩ừ𝗏ŵ𝒙𝒚ź���!@#$%^&*()大-_=+[{]};:"


@pytest.fixture(scope="session")
def event_loop():
    """
    Redefining Pytest default function-scoped event_loop fixture.
    A hack from https://stackoverflow.com/a/72104554/196171 prevents 'RuntimeError: Event loop is closed'
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
