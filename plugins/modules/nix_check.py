#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Violet Caulfield
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: nix_check
short_description: Validate that a Nix expression parses
version_added: "0.1.0"
description:
  - Parses a Nix expression with C(nix-instantiate --parse) to catch syntax
    errors before a generated file is copied anywhere that acts on it (e.g.
    C(/etc/nixos)).
  - This only checks syntax, not evaluation — it does not require network
    access or a working channel/flake registry.
  - Never reports C(changed) — it's a read-only check.
options:
  content:
    description:
      - The Nix expression text to validate. Mutually exclusive with O(path).
    type: str
  path:
    description:
      - Path to an existing C(.nix) file to validate. Mutually exclusive
        with O(content).
    type: path
  nix_instantiate_bin:
    description:
      - Name or path of the C(nix-instantiate) binary.
    type: str
    default: nix-instantiate
author:
  - Violet Caulfield
'''

EXAMPLES = r'''
- name: Render configuration.nix
  ansible.builtin.set_fact:
    rendered_config: "{{ annix_nixos_config | cosmonautical.nixify.to_nix }}"

- name: Validate it before it's ever written to /etc/nixos
  cosmonautical.nixify.nix_check:
    content: "{{ rendered_config }}"

- name: Validate an already-templated file
  cosmonautical.nixify.nix_check:
    path: /etc/nixos/configuration.nix
'''

RETURN = r'''
stdout:
  description: The parser's standard output (normally empty on success).
  type: str
  returned: always
stderr:
  description: The parser's standard error, including the syntax error on failure.
  type: str
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            content=dict(type='str'),
            path=dict(type='path'),
            nix_instantiate_bin=dict(type='str', default='nix-instantiate'),
        ),
        required_one_of=[['content', 'path']],
        mutually_exclusive=[['content', 'path']],
        supports_check_mode=True,
    )

    bin_path = module.get_bin_path(module.params['nix_instantiate_bin'], required=True)

    if module.params['path']:
        cmd = [bin_path, '--parse', module.params['path']]
        rc, out, err = module.run_command(cmd)
    else:
        cmd = [bin_path, '--parse', '-']
        rc, out, err = module.run_command(cmd, data=module.params['content'], binary_data=False)

    if rc != 0:
        module.fail_json(
            msg='Nix expression failed to parse: %s' % err.strip(),
            stdout=out,
            stderr=err,
        )

    module.exit_json(changed=False, stdout=out, stderr=err)


if __name__ == '__main__':
    main()
