#include <cstdlib>
#include <iostream>
#include <cstring>
#include "StringToArgv.h"
#include "Util.h"

#ifndef NUL
#define NUL '\0'
#endif

static str_to_argv_err_t copy_raw_string(char ** dest_p, char ** src_p);

static str_to_argv_err_t copy_cooked_string(char ** dest_p, char ** src_p);

static char escape_convt(char ** src_p);

str_to_argv_err_t string_to_argv(char const * str, int * argc_p, char *** argv_p)
{
    int     argc = 0;
    int     act  = 10;
    char ** res  = (char **)malloc(sizeof(char *) * 10);
    char ** argv = res;
    char *  scan;
    char *  dest;
    str_to_argv_err_t err;

    while (isspace((unsigned char)*str))  str++;
    str = scan = strdup(str);

    for (;;) {
        while (isspace((unsigned char)*scan))  scan++;
        if (*scan == NUL)
            break;

        if (++argc >= act) {
            act += act / 2;
            res  = (char **)realloc(res, act * sizeof(char *));
            argv = res + (argc - 1);
        }

        *(argv++) = dest = scan;

        for (;;) {
            char ch = *(scan++);
            switch (ch) {
                case NUL:
                    goto done;

                case '\\':
                    if ( (*(dest++) = *(scan++)) == NUL)
                        goto done;
                    break;

                case '\'':
                    err = copy_raw_string(&dest, &scan);
                    if (err != STR2AV_OK)
                        goto error_leave;
                    break;

                case '"':
                    err = copy_cooked_string(&dest, &scan);
                    if (err != STR2AV_OK)
                        goto error_leave;
                    break;

                case ' ':
                case '\t':
                case '\n':
                case '\f':
                case '\r':
                case '\v':
                case '\b':
                    goto token_done;

                default:
                    *(dest++) = ch;
            }
        }

        token_done:
        *dest = NUL;
    }

    done:

    *argv_p = res;
    *argc_p = argc;
    *argv   = NULL;
    if (argc == 0)
        free((void *)str);

    return STR2AV_OK;

    error_leave:

    free(res);
    free((void *)str);
    return err;
}

static str_to_argv_err_t copy_raw_string(char ** dest_p, char ** src_p)
{
    for (;;) {
        char ch = *((*src_p)++);

        switch (ch) {
            case NUL: return STR2AV_UNBALANCED_QUOTE;
            case '\'':
                *(*dest_p) = NUL;
                return STR2AV_OK;

            case '\\':
                ch = *((*src_p)++);
                switch (ch) {
                    case NUL:
                        return STR2AV_UNBALANCED_QUOTE;

                    default:
                        /*
                         * unknown/invalid escape.  Copy escape character.
                         */
                        *((*dest_p)++) = '\\';
                        break;

                    case '\\':
                    case '\'':
                        break;
                }
                /* FALLTHROUGH */

            default:
                *((*dest_p)++) = ch;
                break;
        }
    }
}

static char escape_convt(char ** src_p)
{
    char ch = *((*src_p)++);

    /*
     *  Escape character is always eaten.  The next character is sometimes
     *  treated specially.
     */
    switch (ch) {
        case 'a': ch = '\a'; break;
        case 'b': ch = '\b'; break;
        case 't': ch = '\t'; break;
        case 'n': ch = '\n'; break;
        case 'v': ch = '\v'; break;
        case 'f': ch = '\f'; break;
        case 'r': ch = '\r'; break;
    }

    return ch;
}


static str_to_argv_err_t copy_cooked_string(char ** dest_p, char ** src_p)
{
    for (;;) {
        char ch = *((*src_p)++);
        switch (ch) {
            case NUL: return STR2AV_UNBALANCED_QUOTE;
            case '"':
                *(*dest_p) = NUL;
                return STR2AV_OK;

            case '\\':
                ch = escape_convt(src_p);
                if (ch == NUL)
                    return STR2AV_UNBALANCED_QUOTE;
                /* FALLTHROUGH */

            default:
                *((*dest_p)++) = ch;
                break;
        }
    }
}

str_to_argv_err_t string_to_argv_vector(char const *str, std::vector<std::string>* argv_p) {
    int argc;
    char **argv;
    str_to_argv_err_t r = string_to_argv(str, &argc, &argv);
    if (r != 0)
        return r;
    argv_p->reserve(argc);
    for (int i = 0; i < argc; i++)
        argv_p->emplace_back(argv[i]);
    return str_to_argv_err_t::STR2AV_OK;
}