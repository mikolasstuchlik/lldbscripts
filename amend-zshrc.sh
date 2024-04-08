#!/bin/bash

#https://lldb.llvm.org/use/python-reference.html#using-the-lldb-py-module-in-python

ZSHRC_PATH="$HOME/.zshrc"

echo "" >> $ZSHRC_PATH
echo "# Add LLDB to PYTHON path https://lldb.llvm.org/use/python-reference.html#using-the-lldb-py-module-in-python" >> $ZSHRC_PATH
echo "PYTHONPATH=\$PYTHONPATH:\$(lldb -P)" >> $ZSHRC_PATH
echo "" >> $ZSHRC_PATH
