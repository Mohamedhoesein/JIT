#ifndef JIT_STRINGTOARGV_H
#define JIT_STRINGTOARGV_H

typedef enum {
    STR2AV_OK       = 0,
    STR2AV_UNBALANCED_QUOTE
} str_to_argv_err_t;

str_to_argv_err_t string_to_argv(char const *str, int *argc_p, char ***argv_p);

#endif //JIT_STRINGTOARGV_H
