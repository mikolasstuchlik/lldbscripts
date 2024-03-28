#ifndef RETAIN_OVERRIDE_C
#define RETAIN_OVERRIDE_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "../commons/swift_printing.c"
#endif /*LLDB_EXPR_ENV*/

void *(*__lldbscript__original_swift_retain)(void *); 

void *__lldbscript__new_retain(void * ptr) { 
    (void)__lldbscript__PrintRetainCount(ptr, "will retain: ", 13);
    return __lldbscript__original_swift_retain(ptr); 
}

#endif /*RETAIN_OVERRIDE_C*/
