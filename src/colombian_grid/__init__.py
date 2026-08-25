"""colombian_grid — extract Colombian electrical-sector data from Paratec and XM."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version

from colombian_grid.core.ido import AsyncIdoClient
from colombian_grid.core.paratec import AsyncParatecClient
from colombian_grid.core.xm import AsyncXMClient, SyncXMClient

try:
    __version__ = _package_version("colombian-grid")
except PackageNotFoundError:  # package is not installed
    __version__ = "0.0.0.dev0"

__all__ = [
    "AsyncIdoClient",
    "AsyncParatecClient",
    "AsyncXMClient",
    "SyncXMClient",
    "__version__",
]
