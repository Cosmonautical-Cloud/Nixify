#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Violet Caulfield
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Filters that convert Ansible-rendered YAML/Jinja data into Nix expressions."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible_collections.cosmonautical.nixify.plugins.module_utils.nix import NixRaw, to_nix


def to_nix_filter(value, indent_size=2):
    try:
        return to_nix(value, indent=0, indent_size=indent_size)
    except TypeError as exc:
        raise AnsibleFilterError(str(exc))


def nix_raw(text):
    """Wrap a string so ``to_nix`` emits it verbatim instead of quoting it."""
    return NixRaw(str(text))


class FilterModule(object):
    def filters(self):
        return {
            'to_nix': to_nix_filter,
            'nix_raw': nix_raw,
        }
