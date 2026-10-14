# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project follows [semantic versioning](https://semver.org/).

## [0.1.0] - 2026-10-13

### Added

- Initial release: the `to_nix` filter, converting plain YAML/Jinja data (dicts, lists, strings, numbers, booleans, `None`) into pretty-printed Nix expression source, with string escaping for `"`, `\`, `${` and newlines.
- The `nix_raw` filter and the `__nix_raw__` dict-key sentinel, both for emitting literal Nix source (package references, function calls, paths) instead of a quoted string — the sentinel key exists so raw expressions can be authored directly in inventory/group_vars YAML, which can't construct Python objects for the filter to receive.
- The `nix_check` module, validating a rendered Nix expression's syntax via `nix-instantiate --parse` before anything downstream acts on it.
- Conversion logic lives in `plugins/module_utils/nix.py`, kept dependency-free and covered by `tests/unit/test_nix.py` so it can be verified without a full Ansible controller.
