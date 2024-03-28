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

void *(*__lldbscript__original_swift_retain_n)(void *, uint32_t); 

void *__lldbscript__new_retain_n(void * ptr, uint32_t n) { 
    (void)__lldbscript__PrintRetainCount(ptr, "will retain n: ", 15);
    return __lldbscript__original_swift_retain_n(ptr, n); 
}

void *(*__lldbscript__original_swift_tryRetain)(void *); 

void *__lldbscript__new_tryRetain(void * ptr) { 
    (void)__lldbscript__PrintRetainCount(ptr, "try retain: ", 12);
    return __lldbscript__original_swift_tryRetain(ptr); 
}

#endif /*RETAIN_OVERRIDE_C*/
