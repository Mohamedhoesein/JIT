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
/*
 * Copyright (C) 2008
 * Y. Hara, H. Tomiyama, S. Honda, H. Takada and K. Ishii
 * Nagoya University, Japan
 * All rights reserved.
 *
 * Disclaimer of Warranty
 *
 * These software programs are available to the user without any license fee or
 * royalty on an "as is" basis. The authors disclaims  any and all warranties, 
 * whether express, implied, or statuary, including any implied warranties or 
 * merchantability or of fitness for a particular purpose. In no event shall the
 * copyright-holder be liable for any incidental, punitive, or consequential damages
 * of any kind whatsoever arising from the use of these programs. This disclaimer
 * of warranty extends to the user of these programs and user's customers, employees,
 * agents, transferees, successors, and assigns.
 *
 */
#ifndef _INIT_H_
#define _INIT_H_
#include "decode.h"
#include "global.h"
extern int main_result;
/*
 * Output Buffer
 */
extern unsigned char *CurHuffReadBuf;
extern int OutData_image_width;
extern int OutData_image_height;
extern int OutData_comp_vpos[RGB_NUM];
extern int OutData_comp_hpos[RGB_NUM];
extern unsigned char OutData_comp_buf[RGB_NUM][BMP_OUT_SIZE];

/*
+--------------------------------------------------------------------------+
| * Test Vector (added for CHStone)                                        |
|     hana_jpg : input data                                                |
|     hana_bmp : expected output data                                      |
|     out_width : expected output data                                     |
|     out_length : expected output data                                    |
+--------------------------------------------------------------------------+
*/
#define JPEGSIZE 5207

extern const unsigned char hana_jpg[JPEGSIZE];

extern const unsigned char hana_bmp[RGB_NUM][BMP_OUT_SIZE];

extern int out_width;
extern int out_length;

#endif /* _INIT_H_ */