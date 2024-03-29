#ifndef ALLOCOBJECT_OVERRIDE_C
#define ALLOCOBJECT_OVERRIDE_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include "../commons/swift_printing.c"
#endif /*LLDB_EXPR_ENV*/

void * (*__lldbscript__original_swift_allocObject)(void *, size_t, size_t); 

void * __lldbscript__new_swift_allocObject(void * heap_metadata, size_t size, size_t alignment) {
    void * new_alloc = __lldbscript__original_swift_allocObject(heap_metadata, size, alignment);
    return new_alloc;
}

#endif /*ALLOCOBJECT_OVERRIDE_C*/
