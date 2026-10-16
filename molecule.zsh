#! /bin/zsh

# This script runs the collection's Molecule scenarios (molecule/*/) in
# a nixos/nix container. Needs Docker, plus:
#   pip install molecule "molecule-plugins[docker]"
#   ansible-galaxy collection install community.docker
# Extra arguments are passed through, e.g. `-s default --destroy never`.
if (( $# )); then
  molecule test "$@"
else
  molecule test --all
fi
