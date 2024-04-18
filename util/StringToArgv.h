#ifndef JIT_STRINGTOARGV_H
#define JIT_STRINGTOARGV_H

#include <vector>

/**
 * An indication of the from a string to argv is successful.
 */
typedef enum {
    STR2AV_OK       = 0,
    STR2AV_UNBALANCED_QUOTE
} str_to_argv_err_t;

/**
 * Convert a string to an argv array, from [here](https://stackoverflow.com/questions/2342162/stdstring-formatting-like-sprintf).
 * @param str The original string from which to extract the argv array.
 * @param argc_p The number of arguments in the string.
 * @param argv_p The arguments in the string.
 * @return
 */
str_to_argv_err_t string_to_argv(char const *str, int *argc_p, char ***argv_p);

/**
 * Convert a string to an argv vector.
 * @param str The original string from which to extract the argv array.
 * @param argv_p The arguments in the string.
 * @return
 */
str_to_argv_err_t string_to_argv_vector(char const *str, std::vector<std::string>* argv_p);

#endif //JIT_STRINGTOARGV_H
