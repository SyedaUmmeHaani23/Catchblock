from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class Fix:
    path: str
    content: str
    mode: str = "create"  # "create" never overwrites; "append" only adds to the end
    diff: str = ""        # filled in by the scanner: a git-style preview of this fix

@dataclass
class Finding:
    id: str
    category: str
    status: Literal["pass", "warn", "fail"]
    severity: Literal["low", "medium", "high", "critical"]
    weight: int
    title: str
    why: str
    fix: Optional[Fix] = None
