class ToolError(Exception):
    """An error caused by invalid tool usage or domain constraints."""


class ToolFatalError(Exception):
    """Unfixable error; agent should terminate."""
