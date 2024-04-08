#!/bin/bash

LLDBINIT_PATH="$HOME/.lldbinit"

if [[ ! -z "$1" ]]
then 
    LLDBINIT_PATH="$LLDBINIT_PATH$1"
fi

echo "" >> $LLDBINIT_PATH
echo "# Registering scripts from mikolasstuchlik/lldbscripts" >> $LLDBINIT_PATH
echo "command script import $(pwd)/scripts/arctool.py" >> $LLDBINIT_PATH
echo "command script import $(pwd)/scripts/closure.py" >> $LLDBINIT_PATH
echo "command script import $(pwd)/scripts/touches.py" >> $LLDBINIT_PATH
