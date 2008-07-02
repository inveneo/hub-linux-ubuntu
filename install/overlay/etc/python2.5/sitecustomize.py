import sys

# Inveneo Customization
INV_PATH='/opt/inveneo/lib/python'
if INV_PATH not in sys.path:
    sys.path.append(INV_PATH)


# install the apport exception handler if available
try:
    import apport_python_hook
except ImportError:
    pass
else:
    apport_python_hook.install()

