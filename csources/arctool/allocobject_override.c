#ifndef ALLOCOBJECT_OVERRIDE_C
#define ALLOCOBJECT_OVERRIDE_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "../commons/swift_printing.c"
#include "arctool_resolution.c"
#endif /*LLDB_EXPR_ENV*/

void * (*__lldbscript__original_swift_allocObject)(void *, size_t, size_t); 

void * __lldbscript__new_swift_allocObject(void * heap_metadata, size_t size, size_t alignment) {
    void * new_alloc = __lldbscript__original_swift_allocObject(heap_metadata, size, alignment);
    
    const char * desciption = __lldbscript__StringDescribing(heap_metadata);
    if (desciption != NULL) {
        size_t len = __lldbscript__strlen(desciption);
        if (__lldbscript__match(desciption, len, true) >= 0) {
            __lldbscript__PutStr("Allocating: ", 12);
            __lldbscript__PutStr(desciption, len);
            __lldbscript__PutStr(" address: ", 10);
            __lldbscript__PutPtr(new_alloc);
            __lldbscript__PutStr("\n", 1);
            __lldbscript__breakpoint_slot();
        }
    }

    return new_alloc;
}

#endif /*ALLOCOBJECT_OVERRIDE_C*/
