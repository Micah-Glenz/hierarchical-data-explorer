"""
Sphinx configuration file for the Hierarchical Data Explorer documentation.

This file contains the Sphinx configuration settings for generating
readthedocs-style documentation.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'Hierarchical Data Explorer'
author = 'Data Explorer Team'
copyright = f'{datetime.now().year}, {author}'
version = '1.0.0'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'obj'

# -- Options for HTML output ------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Custom sidebar templates, must be a dictionary that maps document names
# to a template name.
html_sidebars = {
    '**': [
        'relations.html',
        'searchbox.html',
        'localtoc.html',
    ]
}

# Additional CSS files
html_css_files = [
    'css/custom.css',
]

# -- Extension configuration -------------------------------------------------
# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
}

# Todo extension settings
todo_include_todos = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# -- Nitpicky mode settings -----------------------------------------------
nitpicky = True
nitpick_ignore = [
    ('py:class', 'Path'),
    ('py:class', 'List'),
    ('py:class', 'Dict'),
    ('py:class', 'Any'),
    ('py:class', 'Optional'),
]