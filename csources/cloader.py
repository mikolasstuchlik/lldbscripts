import os
from typing import Optional

class CLoader:
    def __init__(self, filename: str, comment: Optional[str] = None, requiresNull: bool = False):
        self.filename = filename
        self.requiresNull = requiresNull
        self.comment = comment

    def file_content(self, set_lldb_env: bool = False) -> str:
        dirname: str = os.path.dirname(os.path.abspath(__file__))
        handle = open( dirname + "/" + self.filename, "r")
        result: str = handle.read()
        if set_lldb_env == True:
            result = "#define LLDB_EXPR_ENV \n" + result
        handle.close()
        return result

class PrivateCFiles:
    lldb_null: CLoader = CLoader("commons/lldb_null.h", "LLDB sometimes lacks NULL, this defines NULL as 0")

class CFiles:
    printing: CLoader = CLoader("commons/printing.c", "Utilities for printing without printf", requiresNull=True)
    swift_printing: CLoader = CLoader("commons/swift_printing.c", "Utilities for printing Swift types", requiresNull=True)

    acrtool_resolution: CLoader = CLoader("arctool/arctool_resolution.c", requiresNull=True)
    alloc_override: CLoader = CLoader("arctool/allocobject_override.c", requiresNull=True)
    alloc_interpose: CLoader = CLoader("arctool/allocobject_interposer.c")
    retain_override: CLoader = CLoader("arctool/retain_override.c")
    retain_interpose: CLoader = CLoader("arctool/retain_interposer.c")
    release_override: CLoader = CLoader("arctool/release_override.c")
    release_interpose: CLoader = CLoader("arctool/release_interposer.c")

def load_c_file(file: CLoader) -> str:
    result: str = ""
    if file.requiresNull == True:
        result = PrivateCFiles.lldb_null.file_content(set_lldb_env=True)
    result = result + file.file_content(set_lldb_env = not file.requiresNull)
    return result
