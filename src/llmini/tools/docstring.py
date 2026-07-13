import re
from typing import Any


def parse_google_docstring(docstring: str) -> dict[str, Any]:
    """
    Parses a Google-style docstring.
    Returns:
      {
        "description": str,
        "params": { param_name: description }
      }
    """
    if not docstring:
        return {"description": "", "params": {}}

    lines = docstring.strip().splitlines()
    description = lines[0].strip()
    params = {}

    in_args = False
    for line in lines[1:]:
        line = line.rstrip()
        if line.startswith("Args:"):
            in_args = True
            continue
        if in_args:
            if not line.strip():
                continue
            m = re.match(r"\s*(\w+):\s*(.+)", line)
            if m:
                name, desc = m.groups()
                params[name] = desc.strip()
            else:
                if params:
                    last = list(params.keys())[-1]
                    params[last] += " " + line.strip()

    return {"description": description, "params": params}
