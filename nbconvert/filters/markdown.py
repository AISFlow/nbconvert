"""Markdown filters

This file contains a collection of utility filters for dealing with
markdown within Jinja templates.
"""
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import re

from packaging.version import Version

from nbconvert.utils.pandoc import get_pandoc_version

try:
    from .markdown_mistune import markdown2html_mistune

except ImportError as e:
    _mistune_import_error = e

    def markdown2html_mistune(source: str) -> str:
        """mistune is unavailable, raise ImportError"""
        msg = f"markdown2html requires mistune: {_mistune_import_error}"
        raise ImportError(msg)


from .pandoc import convert_pandoc

__all__ = [
    "markdown2asciidoc",
    "markdown2html",
    "markdown2html_mistune",
    "markdown2html_pandoc",
    "markdown2latex",
    "markdown2rst",
]


_MARKDOWN_FMT = "markdown+lists_without_preceding_blankline"


def markdown2latex(source, markup=_MARKDOWN_FMT, extra_args=None):
    """
    Convert a markdown string to LaTeX via pandoc.

    This function will raise an error if pandoc is not installed.
    Any error messages generated by pandoc are printed to stderr.

    Parameters
    ----------
    source : string
        Input string, assumed to be valid markdown.
    markup : string
        Markup used by pandoc's reader
        default : pandoc extended markdown
        (see https://pandoc.org/README.html#pandocs-markdown)

    Returns
    -------
    out : string
        Output as returned by pandoc.
    """
    return convert_pandoc(source, markup, "latex", extra_args=extra_args)


def markdown2html_pandoc(source, extra_args=None):
    """
    Convert a markdown string to HTML via pandoc.
    """
    extra_args = extra_args or ["--mathjax"]
    return convert_pandoc(source, _MARKDOWN_FMT, "html", extra_args=extra_args)


def markdown2asciidoc(source, extra_args=None):
    """Convert a markdown string to asciidoc via pandoc"""

    # Prior to version 3.0, pandoc supported the --atx-headers flag.
    # For later versions, we must instead pass --markdown-headings=atx.
    # See https://pandoc.org/releases.html#pandoc-3.0-2023-01-18
    atx_args = ["--atx-headers"]
    pandoc_version = get_pandoc_version()
    if pandoc_version and Version(pandoc_version) >= Version("3.0"):
        atx_args = ["--markdown-headings=atx"]

    extra_args = extra_args or atx_args
    asciidoc = convert_pandoc(source, _MARKDOWN_FMT, "asciidoc", extra_args=extra_args)
    # workaround for https://github.com/jgm/pandoc/issues/3068
    if "__" in asciidoc:
        asciidoc = re.sub(r"\b__([\w \n-]+)__([:,.\n\)])", r"_\1_\2", asciidoc)
        # urls / links:
        asciidoc = re.sub(r"\(__([\w\/-:\.]+)__\)", r"(_\1_)", asciidoc)

    return asciidoc


# The mistune renderer is the default, because it's simple to depend on it
markdown2html = markdown2html_mistune


def markdown2rst(source, extra_args=None):
    """
    Convert a markdown string to ReST via pandoc.

    This function will raise an error if pandoc is not installed.
    Any error messages generated by pandoc are printed to stderr.

    Parameters
    ----------
    source : string
        Input string, assumed to be valid markdown.

    Returns
    -------
    out : string
        Output as returned by pandoc.
    """
    return convert_pandoc(source, _MARKDOWN_FMT, "rst", extra_args=extra_args)
