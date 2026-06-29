"""Agent package for the InvoiceOps MVP."""

from importlib.util import find_spec


def adk_available() -> bool:
    """Return True when Google ADK is installed locally."""
    try:
        return find_spec("google.adk") is not None
    except ModuleNotFoundError:
        return False
