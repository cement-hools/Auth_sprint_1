"""Fixtures"""

import pytest

from tests.functional.fixtures.async_http import (
    aiohttp_client_session,
    aiohttp_get,
    aiohttp_post,
)
from tests.functional.fixtures.http import (
    client_session,
    http_delete,
    http_get,
    http_post,
    http_put,
)


def pytest_configure():
    pytest.strange_unicode_str = "\uFFFF~𝘈Ḇ𝖢𝕯٤ḞԍНǏ𝙅ƘԸⲘ𝙉০Ρ𝗤Ɍ𝓢ȚЦ𝒱Ѡ𝓧ƳȤѧᖯć𝗱ễ𝑓𝙜Ⴙ𝞲𝑗𝒌ļṃŉо𝞎𝒒ᵲꜱ𝙩ừ𝗏ŵ𝒙𝒚ź���!@#$%^&*()大-_=+[{]};:"
