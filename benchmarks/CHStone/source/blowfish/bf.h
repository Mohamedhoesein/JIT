#ifndef HEADER_BF_H_
#define HEADER_BF_H_

#include "blowfish.h"
#include "bf_locl.h"
#include "bf_pi.h"

void
local_memcpy (BF_LONG * s1, const BF_LONG * s2, int n);

void
BF_set_key (int len, unsigned char *data);

void
BF_cfb64_encrypt (unsigned char *in, unsigned char *out, long length, unsigned char *ivec, int *num, int encrypt);

void
BF_encrypt (BF_LONG *data, int encrypt);

#endif /* HEADER_BF_H_ */
