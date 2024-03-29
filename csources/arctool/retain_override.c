#ifndef RETAIN_OVERRIDE_C
#define RETAIN_OVERRIDE_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "../commons/swift_printing.c"
#include "arctool_resolution.c"
#endif /*LLDB_EXPR_ENV*/

void *(*__lldbscript__original_swift_retain)(void *); 

void *__lldbscript__new_retain(void * ptr) { 
    const char * desciption = __lldbscript__StringDescribing(__lldbscript__HeapObject2Metadata(ptr));
    if (desciption != NULL) {
        size_t len = __lldbscript__strlen(desciption);
        if (__lldbscript__match(desciption, len, true) >= 0) {
            __lldbscript__PrintRetainCount(ptr, "Will retain: ", 13);
            __lldbscript__breakpoint_slot();
        }
    }
    return __lldbscript__original_swift_retain(ptr); 
}

void *(*__lldbscript__original_swift_retain_n)(void *, uint32_t); 

void *__lldbscript__new_retain_n(void * ptr, uint32_t n) { 
    const char * desciption = __lldbscript__StringDescribing(__lldbscript__HeapObject2Metadata(ptr));
    if (desciption != NULL) {
        size_t len = __lldbscript__strlen(desciption);
        if (__lldbscript__match(desciption, len, true) >= 0) {
            __lldbscript__PrintRetainCount(ptr, "Will retain n: ", 15);
            __lldbscript__breakpoint_slot();
        }
    }
    return __lldbscript__original_swift_retain_n(ptr, n); 
}

void *(*__lldbscript__original_swift_tryRetain)(void *); 

void *__lldbscript__new_tryRetain(void * ptr) { 
    const char * desciption = __lldbscript__StringDescribing(__lldbscript__HeapObject2Metadata(ptr));
    if (desciption != NULL) {
        size_t len = __lldbscript__strlen(desciption);
        if (__lldbscript__match(desciption, len, true) >= 0) {
            __lldbscript__PrintRetainCount(ptr, "Will try retain: ", 17);
            __lldbscript__breakpoint_slot();
        }
    }
    return __lldbscript__original_swift_tryRetain(ptr); 
}

#endif /*RETAIN_OVERRIDE_C*/
