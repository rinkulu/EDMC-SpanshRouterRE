# pyright: reportAssignmentType=false

import logging
from dataclasses import dataclass
from pathlib import Path
from semantic_version import Version
from typing import TYPE_CHECKING


# to avoid circular imports, local imports go here
if TYPE_CHECKING:
    from .SpanshRouter import SpanshRouter


@dataclass
class Context:
    plugin_name: str = None
    plugin_version: Version = None
    plugin_dir: Path = None
    logger: logging.Logger = None
    router: 'SpanshRouter' = None

    system: str | None = None
