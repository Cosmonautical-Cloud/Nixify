#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Violet Caulfield
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Pure-Python conversion of plain data (the output of YAML + Jinja - dicts,
lists, strings, numbers, booleans, None) into Nix expression source text.

Shared by the ``to_nix``/``nix_raw`` filters and anything else in this
collection that needs to render Nix, kept dependency-free so it can also be
unit tested without an Ansible controller.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re

# Nix's own unquoted-identifier grammar: letters/underscore, then
# alphanumerics, underscore, apostrophe or hyphen.
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_'-]*$")

# The single dict key that marks "emit this value's text verbatim, don't
# quote it as a string" when authoring raw Nix straight in YAML (no Jinja
# filter available there, since YAML alone can't construct a Python object).
RAW_KEY = '__nix_raw__'


class NixRaw(object):
    """A string that ``to_nix`` emits verbatim instead of quoting.

    Used for Nix code that has to be real expressions rather than string
    literals: package references (``pkgs.vim``), function calls
    (``lib.mkDefault true``), paths (``./hardware-configuration.nix``), etc.
    """

    __slots__ = ('text',)

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'NixRaw(%r)' % (self.text,)

    def __eq__(self, other):
        return isinstance(other, NixRaw) and self.text == other.text

    def __hash__(self):
        return hash(('NixRaw', self.text))


def _is_raw_dict(value):
    return isinstance(value, dict) and list(value.keys()) == [RAW_KEY]


def _quote_string(value):
    escaped = (
        value.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace('${', '\\${')
             .replace('\n', '\\n')
             .replace('\t', '\\t')
    )
    return '"%s"' % escaped


def _quote_key(key):
    key = str(key)
    if _IDENTIFIER_RE.match(key):
        return key
    return _quote_string(key)


def to_nix(value, indent=0, indent_size=2):
    """Render ``value`` as a Nix expression, pretty-printed at ``indent`` levels."""
    pad = ' ' * (indent * indent_size)
    child_pad = ' ' * ((indent + 1) * indent_size)

    if isinstance(value, NixRaw):
        return value.text

    if _is_raw_dict(value):
        return str(value[RAW_KEY])

    if value is None:
        return 'null'

    if isinstance(value, bool):
        return 'true' if value else 'false'

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        return repr(value)

    if isinstance(value, str):
        return _quote_string(value)

    if isinstance(value, dict):
        if not value:
            return '{ }'
        lines = ['{']
        for key, val in value.items():
            rendered = to_nix(val, indent + 1, indent_size)
            lines.append('%s%s = %s;' % (child_pad, _quote_key(key), rendered))
        lines.append('%s}' % pad)
        return '\n'.join(lines)

    if isinstance(value, (list, tuple)):
        if not value:
            return '[ ]'
        lines = ['[']
        for item in value:
            rendered = to_nix(item, indent + 1, indent_size)
            lines.append('%s%s' % (child_pad, rendered))
        lines.append('%s]' % pad)
        return '\n'.join(lines)

    raise TypeError('Cannot convert value of type %s to a Nix expression' % type(value).__name__)
