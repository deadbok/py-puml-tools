"""Keep the version number in the tags of a version control system (Git,
Mercurial, etc) instead of in the code, and automatically extract it from there
using setuptools_scm.
"""
from setuptools_scm import get_version
__version__ = get_version(root='..', relative_to=__file__)
