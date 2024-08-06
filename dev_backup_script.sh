#!/bin/bash

# hopefully allows for a single script to be run while importing all of the custom path stuff
export PATH="$(~/.dotfiles/custom_path.sh)" && ~/bin/dev_backup.py
