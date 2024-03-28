#ifndef RELEASE_OVERRIDE_C
#define RELEASE_OVERRIDE_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "../commons/swift_printing.c"
#endif /*LLDB_EXPR_ENV*/

void (*__lldbscript__original_swift_release)(void *); 

void __lldbscript__new_release(void * ptr) {
    (void)__lldbscript__PrintRetainCount(ptr, "will release: ", 14);
    __lldbscript__original_swift_release(ptr); 
}

#endif /*RELEASE_OVERRIDE_C*/