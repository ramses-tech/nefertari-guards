from __future__ import absolute_import

import pytest


@pytest.fixture(scope='module')
def engine_mock(request):
    import nefertari_guards
    from nefertari_guards import engine
    from mock import Mock

    original_engine = engine
    nefertari_guards.engine = Mock()
    nefertari_guards.engine.BaseDocument = object

    def clear():
        nefertari_guards.engine = original_engine
    request.addfinalizer(clear)

    return nefertari_guards.engine
