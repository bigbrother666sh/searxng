# Simplified SearXNG Engines Package

__version__ = "1.0.0"
__description__ = "简化版SearXNG搜索引擎聚合器"

from . import config
from . import utils
from . import engines
from .main import run_search

__all__ = ['config', 'utils', 'engines', 'run_search']
