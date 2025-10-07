"""Local extension package for the top-level ``docling`` namespace.

We keep an ``__init__`` here but make this a pkgutil-style namespace package
so that the installed ``docling`` package in site-packages is still visible
to Python. That allows this directory to provide additional plugin modules
under the ``docling.*`` namespace without shadowing the real package.

This pattern is compatible with projects that inspect modules by name (e.g.
plugin discovery) and will merge this path with other locations that provide
``docling`` (PEP 420 implicit namespaces or pkgutil-style namespaces).
"""

from pkgutil import extend_path

# Merge this package's __path__ with other contributions to the "docling"
# namespace (for example a package installed into site-packages). This makes
# imports like ``import docling.document_converter`` find the installed module
# when it isn't present locally.
__path__ = extend_path(__path__, __name__)


