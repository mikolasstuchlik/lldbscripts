#!/bin/bash

echo "You are using a special-use script used for development. This script is outside of regular setup."
LLDB_PY_PATH=$(echo "script help(lldb)" | lldb | grep -A2 FILE | grep '__init__.py' | tr -d ' ')
ln -s $LLDB_PY_PATH lldb.py
