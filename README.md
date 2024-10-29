# lldbscripts

This repository contains set of lldb scripts for Swift developers.

**You can find scripts related to my talks in the `/talks` directory.**

## Install

Clone this repository

```bash
git clone https://github.com/mikolasstuchlik/lldbscripts.git
```

Add scripts to your `.lldbinit`, either manually (replace `{pwd}` with absolute path to the repository):

```
command script import {pwd}/scripts/arctool.py
```

or using script, which will append all imports at the end of your `.lldbinit`:

```bash
./amend-lldbinit.sh
```

If script was imported, you should see a message like this in your LLDB on each start: `Script `arctool` is installed.`

## Contents

### Bash files

The repository contains a set of bash files, which are used during installation or development.

`amend-lldbinit.sh` will append script import commands at the end of a `.lldbinit` in your home directory.
`amend-zshrc.sh` will add the path to LLDB modules into `.zshrc`.
`simlink-lldbpy.sh` will create a symbolic link to the `__init__.py` file in the LLDB module directory.

### Script `arctool`

Script `arctool` is used to hook on Swift ARC function calls. The script has an internal state, which is initialized by calling `arctool init` while the process is running.

The arctool accepts a list of names of monitored types and opaque summaries. It then logs every ARC call involving an instance of such type. You may enable a breakpoint using `arctool toggle`.

#### Usage

```
(lldb) help arctool
usage: arctool [command]
optional arguments:
  -h, --help            show this help message and exit
Available commands:
  {init,monitor,list,toggle,defragment}
    init                Initializes the arctool. Use when process is running.
    monitor             Print events related to a specific type.
    list                Lists currently observed types
    toggle              Toggles the breakpoint or on off
    defragment          Optimizes the resolution buffer.
Expects 'raw' input (see 'help raw-input'.)

Syntax: arctool
```

### Script `closure_summary_provider`

This script is a custom type decorator. It replaces (amends) the default type decorator for closures. It additionally dumps the closure context. Notice, that the regular expression determining for which types should the decorator be used is kept intentionally simplified. It may not cover all cases - such as higher-order closures etc. It also refrains from making ANY expression evaluator calls.

The script has no *usage*. It is being used by the GUI and `frame variable` command.

### Script `closuredesc`

Script `closuredest` is similar to `closure_summary_provider`, as it only dumps description of certain (local) closure. However, unlike the `closure_summary_provider`, it uses expression evaluator and image lookup to provide additional information about the function pointer and the closure context.

#### Usage
```
(lldb) help closuredesc
usage: closuredesc
optional arguments:
  -h, --help            show this help message and exit
  -n VAR_NAME, --name VAR_NAME
                        Name of a closure variable in current frame or global scope
  -d, --describe        Will try to add description closure and context
Expects 'raw' input (see 'help raw-input'.)

Syntax: closuredesc
```

### Script `closuresearch`

This script is not intended for day-to-day use, but it is kept here as an example. It backtracks from the current stack frame and tries to locate a closure context on the stack. It does so by backtracking through ARM assembly.

### Script `heapobject`

Uses `getTypeName` and `OpaqueSummary` to describe an address of a Swift heap object. 

#### Usage
```
(lldb) help heapobject
Describes raw HeapObject  Expects 'raw' input (see 'help raw-input'.)

Syntax: heapobject
```

### Script `touch`

Much like the script `closuresearch`, this script is kept here as an example of creating a simple breakpoint with a callback.