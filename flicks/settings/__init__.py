from .base import *
try:
    from .local import *
except ImportError, exc:
    exc.args = tuple(['%s (did you rename settings/local.py-dist?)'
                      % exc.args[0]])
    raise exc
"""
import sys
if sys.argv[1] == 'test':
    try:
        from .test import *
    except ImportError:
        pass
"""
