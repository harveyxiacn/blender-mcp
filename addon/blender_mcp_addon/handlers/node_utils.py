"""Node utilities shared by handlers."""

from typing import Optional


def find_principled_bsdf(nodes) -> Optional[object]:
    """Find a Principled BSDF node in a node collection."""
    if not nodes:
        return None

    # Prefer canonical node name when present.
    named = nodes.get("Principled BSDF") if hasattr(nodes, "get") else None
    if named is not None:
        return named

    # Fallback by node type for localized/custom names.
    for node in nodes:
        if getattr(node, "type", None) == "BSDF_PRINCIPLED":
            return node
    return None
