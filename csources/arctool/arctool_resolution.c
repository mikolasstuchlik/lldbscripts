#ifndef ARCTOOL_RESOLUTION_C
#define ARCTOOL_RESOLUTION_C

#ifndef LLDB_EXPR_ENV
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "../commons/lldb_null.h"
#include "../commons/printing.c"
#endif /*LLDB_EXPR_ENV*/

struct __lldbscript__TypeResolverHeader {
    bool is_valid: 1;
    bool is_end: 1;
    uint64_t size: 62;
    const char * last_equal_str_ptr;
};

void * __lldbscript__resolutionBuffer;

#define RESOLUTION_BUFFER_ALLOC_SIZE 1024

void __lldbscript__initialize_buffer();
void __lldbscript__make_end_node(size_t);
size_t __lldbscript__end_node_offset();
size_t __lldbscript__next_node(size_t);
bool __lldbscript__insert(const char *, size_t);
bool __lldbscript__remove(const char *, size_t);
void __lldbscript__defragment();
int __lldbscript__match(const char *, size_t, bool);
void __lldbscript__print_buffer();
void __lldbscript__breakpoint_slot();
size_t __lldbscript__move(size_t, size_t);

void __lldbscript__initialize_buffer() {
    void * new_buffer = (void *)malloc(RESOLUTION_BUFFER_ALLOC_SIZE);
    if (new_buffer == NULL) {
        __lldbscript__resolutionBuffer = NULL;
        return;
    }
    __lldbscript__resolutionBuffer = new_buffer;
    __lldbscript__make_end_node(0);
}

void __lldbscript__make_end_node(size_t offset) {
    struct __lldbscript__TypeResolverHeader * current 
            = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + offset);
    current->is_valid = false;
    current->is_end = true;
    current->size = 0;
    current->last_equal_str_ptr = NULL;
}

size_t __lldbscript__next_node(size_t current_node) {
    struct __lldbscript__TypeResolverHeader * current 
            = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + current_node);
    if (current->is_end) {
        return 0;
    }
    return current_node + sizeof(struct __lldbscript__TypeResolverHeader) + current->size;
}

size_t __lldbscript__end_node_offset() {
    size_t offset = 0;
    while(true) {
        size_t next = __lldbscript__next_node(offset);
        if (next == 0) {
            return offset;
        }
        offset = next;
        if (offset >= RESOLUTION_BUFFER_ALLOC_SIZE) {
            (void)__builtin_trap();
        }
    }
}

bool __lldbscript__insert(const char * type_name, size_t length) {
    if (__lldbscript__match(type_name, length, false) >= 0) {
        return true;
    }

    size_t free_offset = __lldbscript__end_node_offset();
    size_t required_space = free_offset + 2 * sizeof(struct __lldbscript__TypeResolverHeader) + length;
    if (required_space > RESOLUTION_BUFFER_ALLOC_SIZE) {
        return false;
    }

    __lldbscript__make_end_node(free_offset + sizeof(struct __lldbscript__TypeResolverHeader) + length);
    struct __lldbscript__TypeResolverHeader * current 
            = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + free_offset);
    current->is_end = false;
    current->is_valid = true;
    current->last_equal_str_ptr = NULL;
    current->size = length;

    char * name_buffer_ptr = (char *)((size_t)current + sizeof(struct __lldbscript__TypeResolverHeader));
    for (size_t i = 0; i < length; i++) {
        name_buffer_ptr[i] = type_name[i];
    }

    return true;
}

bool __lldbscript__remove(const char * match_ptr, size_t length) {
    int match = __lldbscript__match(match_ptr, length, false);
    if (match < 0) {
        return false;
    }
    struct __lldbscript__TypeResolverHeader * current 
            = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + (size_t)match);
    current->is_valid = false;

    return true;
}

void __lldbscript__defragment() {
    size_t nextOffset = 0;
    size_t freeOffset = 0;
    while(true) {
        struct __lldbscript__TypeResolverHeader * current 
                = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + nextOffset);

        if (nextOffset != freeOffset && current->is_valid) {
            freeOffset = __lldbscript__move(nextOffset, freeOffset);
        } else if (nextOffset == freeOffset && current->is_valid) {
            freeOffset = __lldbscript__next_node(nextOffset);
        }

        size_t next = __lldbscript__next_node(nextOffset);
        if (next == 0) {
            break;
        }
        nextOffset = next;
        if (nextOffset >= RESOLUTION_BUFFER_ALLOC_SIZE) {
            (void)__builtin_trap();
        }
    }
    __lldbscript__make_end_node(freeOffset);
}

int __lldbscript__match(const char * match_ptr, size_t length, bool save_match_ptr) {
    size_t offset = 0;
    while(true) {
        struct __lldbscript__TypeResolverHeader * current 
                = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + offset);
        if (current->is_valid) {
            if (current->last_equal_str_ptr == match_ptr) {
                return (int)offset;
            }
            if (current->size != length) {
                goto NextCycle;
            }
            char * name_buffer_ptr = (char *)((size_t)current + sizeof(struct __lldbscript__TypeResolverHeader));
            for (size_t i = 0; i < length; i++) {
                if (name_buffer_ptr[i] != match_ptr[i]) {
                    goto NextCycle;
                }
            }
            if (save_match_ptr) {
                current->last_equal_str_ptr = match_ptr;
            }
            return (int)offset;
        }

        NextCycle:
        size_t next = __lldbscript__next_node(offset);
        if (next == 0) {
            return -1;
        }
        offset = next;
        if (offset >= RESOLUTION_BUFFER_ALLOC_SIZE) {
            (void)__builtin_trap();
        }
    }
}

void __lldbscript__print_buffer() {
    __lldbscript__PutStr("Resolution buffer length: ", 26);
    __lldbscript__PutUnsignedDecimal(RESOLUTION_BUFFER_ALLOC_SIZE);
    __lldbscript__PutStr(" address: ", 10);
    __lldbscript__PutPtr(__lldbscript__resolutionBuffer);
    __lldbscript__PutStr("\n\n", 2);

    size_t offset = 0;
    while(true) {
        struct __lldbscript__TypeResolverHeader * current 
                = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + offset);

        __lldbscript__PutStr("Offset: ", 8);
        __lldbscript__PutUnsignedDecimal(offset);
        __lldbscript__PutStr("\n", 1);

        __lldbscript__PutStr("    is valid: ", 14);
        if (current->is_valid) {
            __lldbscript__PutStr("yes", 3);
        } else {
            __lldbscript__PutStr("no", 2);
        }
        __lldbscript__PutStr("\n", 1);


        __lldbscript__PutStr("    is end: ", 12);
        if (current->is_end) {
            __lldbscript__PutStr("yes", 3);
        } else {
            __lldbscript__PutStr("no", 2);
        }
        __lldbscript__PutStr("\n", 1);

        __lldbscript__PutStr("    size: ", 10);
        __lldbscript__PutUnsignedDecimal(current->size);
        __lldbscript__PutStr("\n", 1);

        __lldbscript__PutStr("    last resolved ptr: ", 23);
        __lldbscript__PutPtr((void *)current->last_equal_str_ptr);
        __lldbscript__PutStr("\n", 1);

        __lldbscript__PutStr("    content: ", 13);
        __lldbscript__PutStr((char *)((size_t)current + sizeof(struct __lldbscript__TypeResolverHeader)), current->size);
        __lldbscript__PutStr("\n", 1);

        __lldbscript__PutStr("\n", 1);

        size_t next = __lldbscript__next_node(offset);
        if (next == 0) {
            return;
        }
        offset = next;
        if (offset >= RESOLUTION_BUFFER_ALLOC_SIZE) {
            (void)__builtin_trap();
        }
    }
}

size_t __lldbscript__move(size_t from, size_t to) {
    struct __lldbscript__TypeResolverHeader * current 
                = (struct __lldbscript__TypeResolverHeader *)((size_t)__lldbscript__resolutionBuffer + from);

    size_t copy_size = current->size + sizeof(struct __lldbscript__TypeResolverHeader);
    uint8_t *from_ptr = (uint8_t *)((size_t)__lldbscript__resolutionBuffer + from);
    uint8_t *to_ptr = (uint8_t *)((size_t)__lldbscript__resolutionBuffer + to);

    for(size_t i = 0; i < copy_size; i++) {
        to_ptr[i] = from_ptr[i];
    }

    return to + copy_size;
}

void __lldbscript__breakpoint_slot() {
    // This function does nothing. It gets triggered by all monitored instances.
}

#endif /*ARCTOOL_RESOLUTION_C   */
