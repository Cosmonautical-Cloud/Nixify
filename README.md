# Nixify

An Ansible collection that converts the plain data you already get from YAML + Jinja — dicts, lists, strings, numbers, booleans, `None` — into [Nix](https://nix.dev/) expression source text, so inventory/group variables can be templated straight into `.nix` files.

This collection only goes one way (YAML/Jinja data → Nix text). It doesn't know anything about NixOS, `/etc/nixos`, or `nixos-rebuild` — that's [Annix](https://github.com/Cosmonautical-Cloud/Annix) (`cosmonautical.annix`), which depends on this collection and uses it to template and activate a NixOS configuration.

## Requirements

- Ansible installed on the control machine
- `nix-instantiate` on the target host, only if you use the `nix_check` module

## Filters

### `to_nix`

Converts a value into Nix source. Dicts become attrsets, lists become lists, strings are quoted (with `"`, `\`, `${` and newlines escaped so Jinja-rendered content can never break out of the string or trigger unintended interpolation), and `null`/`true`/`false`/numbers map to their Nix equivalents.

```yaml
- name: Render configuration.nix
  ansible.builtin.copy:
    content: |
      { config, pkgs, ... }:
      {{ nixos_config | cosmonautical.nixify.to_nix }}
    dest: /etc/nixos/configuration.nix
  vars:
    nixos_config:
      networking:
        hostName: violet-nixos
        firewall:
          enable: true
      services:
        openssh:
          enable: true
```

produces:

```nix
{ config, pkgs, ... }:
{
  networking = {
    hostName = "violet-nixos";
    firewall = {
      enable = true;
    };
  };
  services = {
    openssh = {
      enable = true;
    };
  };
}
```

### `nix_raw`

Some values need to be real Nix expressions, not string literals — package references, function calls, paths. Wrap them with `nix_raw` inside a template/task, or use the `__nix_raw__` dict key directly in plain YAML (inventory/group_vars files can't construct Python objects, so there's no filter available there):

```yaml
# In a template, via the filter:
packages: "{{ 'with pkgs; [ vim git tmux ]' | cosmonautical.nixify.nix_raw }}"

# Straight in inventory YAML, via the sentinel key:
imports:
  __nix_raw__: "[ ./hardware-configuration.nix ]"
```

Both render as the literal text (`with pkgs; [ vim git tmux ]` / `[ ./hardware-configuration.nix ]`), not a quoted Nix string.

The `__nix_raw__` sentinel is the safer default for inventory/group_vars authoring: it's a plain string, so it survives being passed around between vars files and roles like any other value. A value wrapped by the `nix_raw` filter, on the other hand, is a real Python object until it reaches `to_nix` — it must stay nested inside the dict/list you pass to `to_nix` in the same expression. Assigning it to its own variable and using that variable later (or passing it straight to a module like `debug`) fails with `Type 'NixRaw' is unsupported for variable storage`.

## Modules

### `nix_check`

Validates that a Nix expression parses (`nix-instantiate --parse`), either from a string (`content`) or an existing file (`path`). Syntax-only — no evaluation, no network or channel/flake access required. Useful as a guard before a generated file is copied anywhere that acts on it:

```yaml
- name: Validate before it's ever written to /etc/nixos
  cosmonautical.nixify.nix_check:
    content: "{{ nixos_config | cosmonautical.nixify.to_nix }}"
```

## Installing

```
ansible-galaxy collection install cosmonautical.nixify
```
