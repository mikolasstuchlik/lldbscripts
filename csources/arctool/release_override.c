#ifndef RELEASE_OVERRIDE_C
#define RELEASE_OVERRIDE_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "../commons/swift_printing.c"
#include "arctool_resolution.c"
#endif /*LLDB_EXPR_ENV*/

void (*__lldbscript__original_swift_release)(void *); 

void __lldbscript__new_release(void * ptr) {
    const char * desciption = __lldbscript__StringDescribing(__lldbscript__HeapObject2Metadata(ptr));
    if (desciption != NULL) {
        size_t len = __lldbscript__strlen(desciption);
        if (__lldbscript__match(desciption, len, true) >= 0) {
            __lldbscript__PrintRetainCount(ptr, "Will release: ", 14);
            __lldbscript__breakpoint_slot();
        }
    }

    __lldbscript__original_swift_release(ptr); 
}

void (*__lldbscript__original_swift_release_n)(void *, uint32_t); 

void __lldbscript__new_release_n(void * ptr, uint32_t n) {
    const char * desciption = __lldbscript__StringDescribing(__lldbscript__HeapObject2Metadata(ptr));
    if (desciption != NULL) {
        size_t len = __lldbscript__strlen(desciption);
        if (__lldbscript__match(desciption, len, true) >= 0) {
            __lldbscript__PrintRetainCount(ptr, "Will release n: ", 16);
            __lldbscript__breakpoint_slot();
        }
    }

    __lldbscript__original_swift_release_n(ptr, n); 
}

#endif /*RELEASE_OVERRIDE_C*/
