#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Violet Caulfield
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'module_utils'))

from nix import NixRaw, to_nix  # noqa: E402


def test_scalars():
    assert to_nix(None) == 'null'
    assert to_nix(True) == 'true'
    assert to_nix(False) == 'false'
    assert to_nix(42) == '42'
    assert to_nix(3.14) == '3.14'
    assert to_nix('hello') == '"hello"'


def test_string_escaping():
    assert to_nix('a "quoted" word') == '"a \\"quoted\\" word"'
    assert to_nix('a\\backslash') == '"a\\\\backslash"'
    assert to_nix('${interpolation}') == '"\\${interpolation}"'
    assert to_nix('line one\nline two') == '"line one\\nline two"'


def test_empty_collections():
    assert to_nix({}) == '{ }'
    assert to_nix([]) == '[ ]'


def test_simple_attrset():
    assert to_nix({'enable': True}) == '{\n  enable = true;\n}'


def test_simple_list():
    assert to_nix(['vim', 'git']) == '[\n  "vim"\n  "git"\n]'


def test_nested_attrset_indentation():
    value = {'networking': {'hostName': 'violet-nixos', 'firewall': {'enable': True}}}
    expected = (
        '{\n'
        '  networking = {\n'
        '    hostName = "violet-nixos";\n'
        '    firewall = {\n'
        '      enable = true;\n'
        '    };\n'
        '  };\n'
        '}'
    )
    assert to_nix(value) == expected


def test_list_of_attrsets():
    value = [{'name': 'violet'}]
    expected = '[\n  {\n    name = "violet";\n  }\n]'
    assert to_nix(value) == expected


def test_key_quoting_for_non_identifiers():
    value = {'not an identifier': 1, 'valid_key': 2}
    rendered = to_nix(value)
    assert '"not an identifier" = 1;' in rendered
    assert 'valid_key = 2;' in rendered


def test_nix_raw_emits_verbatim():
    value = {'packages': NixRaw('with pkgs; [ vim git tmux ]')}
    expected = '{\n  packages = with pkgs; [ vim git tmux ];\n}'
    assert to_nix(value) == expected


def test_raw_dict_sentinel_from_plain_yaml():
    value = {'home': {'__nix_raw__': './home.nix'}}
    expected = '{\n  home = ./home.nix;\n}'
    assert to_nix(value) == expected


def test_unsupported_type_raises():
    import pytest

    class Unsupported(object):
        pass

    with pytest.raises(TypeError):
        to_nix(Unsupported())
