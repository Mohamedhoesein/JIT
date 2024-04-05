/*
+--------------------------------------------------------------------------+
| CHStone : a suite of benchmark programs for C-based High-Level Synthesis |
| ======================================================================== |
|                                                                          |
| * Collected and Modified : Y. Hara, H. Tomiyama, S. Honda,               |
|                            H. Takada and K. Ishii                        |
|                            Nagoya University, Japan                      |
|                                                                          |
| * Remark :                                                               |
|    1. This source code is modified to unify the formats of the benchmark |
|       programs in CHStone.                                               |
|    2. Test vectors are added for CHStone.                                |
|    3. If "main_result" is 0 at the end of the program, the program is    |
|       correctly executed.                                                |
|    4. Please follow the copyright of each benchmark program.             |
+--------------------------------------------------------------------------+
*/
#ifndef SHA_H
#define SHA_H

/* NIST Secure Hash Algorithm */
/* heavily modified from Peter C. Gutmann's implementation */

/* Useful defines & typedefs */

typedef unsigned char BYTE;
typedef unsigned int INT32;

#define SHA_BLOCKSIZE		64

extern INT32 sha_info_digest[5];	/* message digest */
extern INT32 sha_info_count_lo, sha_info_count_hi;	/* 64-bit bit count */
extern INT32 sha_info_data[16];

void sha_init ();
void sha_update (const BYTE *, int);
void sha_final ();

void sha_stream ();
void sha_print ();

#define BLOCK_SIZE 8192
#define VSIZE 2

/*
+--------------------------------------------------------------------------+
| * Test Vectors (added for CHStone)                                       |
|     indata, in_i : input data                                            |
+--------------------------------------------------------------------------+
*/
extern const BYTE indata[VSIZE][BLOCK_SIZE];
extern const int in_i[VSIZE];
#endif /* SHA_H */
