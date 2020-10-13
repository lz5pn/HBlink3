#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016-2018  Cortney T. Buffington, N0MJS <n0mjs@me.com>
#   Copyright (C) 2015 by Jonathan Naylor G4KLX
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################


from bitarray import bitarray
from dmr_utils3 import hamming, crc, rs129

# Does anybody read this stuff? There's a PEP somewhere that says I should do this.
__author__     = 'Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2016-2018 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__    = 'Jonathan Naylor, G4KLX; Ian Wraith'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'


#------------------------------------------------------------------------------
# Interleaver Index
#------------------------------------------------------------------------------

INDEX_181 = (
0, 181, 166, 151, 136, 121, 106, 91, 76, 61, 46, 31, 16, 1, 182, 167, 152, 137,
122, 107, 92, 77, 62, 47, 32, 17, 2, 183, 168, 153, 138, 123, 108, 93, 78, 63,
48, 33, 18, 3, 184, 169, 154, 139, 124, 109, 94, 79, 64, 49, 34, 19, 4, 185, 170,
155, 140, 125, 110, 95, 80, 65, 50, 35, 20, 5, 186, 171, 156, 141, 126, 111, 96,
81, 66, 51, 36, 21, 6, 187, 172, 157, 142, 127, 112, 97, 82, 67, 52, 37, 22, 7,
188, 173, 158, 143, 128, 113, 98, 83, 68, 53, 38, 23, 8, 189, 174, 159, 144, 129,
114, 99, 84, 69, 54, 39, 24, 9, 190, 175, 160, 145, 130, 115, 100, 85, 70, 55, 40,
25, 10, 191, 176, 161, 146, 131, 116, 101, 86, 71, 56, 41, 26, 11, 192, 177, 162,
147, 132, 117, 102, 87, 72, 57, 42, 27, 12, 193, 178, 163, 148, 133, 118, 103, 88,
73, 58, 43, 28, 13, 194, 179, 164, 149, 134, 119, 104, 89, 74, 59, 44, 29, 14,
195, 180, 165, 150, 135, 120, 105, 90, 75, 60, 45, 30, 15)


#------------------------------------------------------------------------------
# BPTC(196,96) Decoding Routings
#------------------------------------------------------------------------------

def decode_full_lc(_data):
    binlc = bitarray(endian='big')   
    binlc.extend([_data[136],_data[121],_data[106],_data[91], _data[76], _data[61], _data[46], _data[31]])
    binlc.extend([_data[152],_data[137],_data[122],_data[107],_data[92], _data[77], _data[62], _data[47], _data[32], _data[17], _data[2]  ])
    binlc.extend([_data[123],_data[108],_data[93], _data[78], _data[63], _data[48], _data[33], _data[18], _data[3],  _data[184],_data[169]])
    binlc.extend([_data[94], _data[79], _data[64], _data[49], _data[34], _data[19], _data[4],  _data[185],_data[170],_data[155],_data[140]])
    binlc.extend([_data[65], _data[50], _data[35], _data[20], _data[5],  _data[186],_data[171],_data[156],_data[141],_data[126],_data[111]])
    binlc.extend([_data[36], _data[21], _data[6],  _data[187],_data[172],_data[157],_data[142],_data[127],_data[112],_data[97], _data[82] ])
    binlc.extend([_data[7],  _data[188],_data[173],_data[158],_data[143],_data[128],_data[113],_data[98], _data[83]])
    '''
    This is the rest of the Full LC data -- the RS1293 FEC that we don't need
     _data[68],_data[53],_data[174],_data[159],_data[144],_data[129],_data[114],_data[99],_data[84],_data[69],_data[54],_data[39],
    _data[24],_data[145],_data[130],_data[115],_data[100],_data[85],_data[70],_data[55],_data[40],_data[25],_data[10],_data[191]
    '''
    return binlc

#------------------------------------------------------------------------------
# BPTC(196,96) Encoding Routings
#------------------------------------------------------------------------------

def interleave_19696(_data):
    inter = bitarray(196, endian='big')
    for index in range(196):
        inter[INDEX_181[index]] = _data[index]  # the real math is slower: deint[index] = _data[(index * 181) % 196]
    return inter

# Accepts 12 byte LC header + RS1293, converts to binary and pads for 196 bit
# encode hamming 15113 to rows and 1393 to columns
def encode_19696(_data):
    # Create a bitarray from the 4 bytes of LC data (includes RS1293 ECC)
    _bdata = bitarray(endian='big')
    _bdata.frombytes(_data)
    
    # Insert R0-R3 bits
    for i in range(4):
        _bdata.insert(0, 0)
    
    # Get row hamming 15,11,3 and append. +1 is to account for R3 that makes an even 196bit string
    for index in range(9):
        spos = (index*15) + 1
        epos= spos + 11
        _rowp = hamming.enc_15113(_bdata[spos:epos])
        for pbit in range(4):
            _bdata.insert(epos+pbit,_rowp[pbit])
    
    # Get column hamming 13,9,3 and append. +1 is to account for R3 that makes an even 196bit string
    # Pad out the bitarray to a full 196 bits. Can't insert into 'columns'
    for i in range(60):
        _bdata.append(0)
    
    column = bitarray(9, endian='big')  # Temporary bitarray to hold column data
    for col in range(15):
        spos = col + 1
        for index in range(9):
            column[index] = _bdata[spos]
            spos += 15
        _colp = hamming.enc_1393(column)
        
        # Insert bits into matrix...
        cpar = 136 + col                # Starting location in the matrix for column bits
        for pbit in range(4):
            _bdata[cpar] =  _colp[pbit]
            cpar += 15

    return _bdata

def encode_header_lc(_lc):
    full_lc = _lc + rs129.lc_header_encode(_lc)
    full_lc = encode_19696(full_lc)
    full_lc = interleave_19696(full_lc)
    return full_lc
    
def encode_terminator_lc(_lc):
    full_lc = _lc + rs129.lc_terminator_encode(_lc)
    full_lc = encode_19696(full_lc)
    full_lc = interleave_19696(full_lc)
    return full_lc
    
#------------------------------------------------------------------------------
# BPTC Embedded LC Decoding Routines
#------------------------------------------------------------------------------

def decode_emblc(_elc):
    
    _binlc = bitarray(endian='big')
    _binlc.extend([_elc[0],_elc[8], _elc[16],_elc[24],_elc[32],_elc[40],_elc[48],_elc[56],_elc[64],_elc[72] ,_elc[80]])
    _binlc.extend([_elc[1],_elc[9], _elc[17],_elc[25],_elc[33],_elc[41],_elc[49],_elc[57],_elc[65],_elc[73] ,_elc[81]])
    _binlc.extend([_elc[2],_elc[10],_elc[18],_elc[26],_elc[34],_elc[42],_elc[50],_elc[58],_elc[66],_elc[74]])
    _binlc.extend([_elc[3],_elc[11],_elc[19],_elc[27],_elc[35],_elc[43],_elc[51],_elc[59],_elc[67],_elc[75]])
    _binlc.extend([_elc[4],_elc[12],_elc[20],_elc[28],_elc[36],_elc[44],_elc[52],_elc[60],_elc[68],_elc[76]])
    _binlc.extend([_elc[5],_elc[13],_elc[21],_elc[29],_elc[37],_elc[45],_elc[53],_elc[61],_elc[69],_elc[77]])
    _binlc.extend([_elc[6],_elc[14],_elc[22],_elc[30],_elc[38],_elc[46],_elc[54],_elc[62],_elc[70],_elc[78]])
    
    return(_binlc.tobytes())

#------------------------------------------------------------------------------
# BPTC Embedded LC Encoding Routines
#------------------------------------------------------------------------------


# Accepts 12 byte LC header + 5-bit checksum, converts to binary and builts out the BPTC
# encoded result with hamming(16,11,4) and parity.
def encode_emblc(_lc):
    
    # Get the 5-bit checksum for the Embedded LC
    _csum = crc.csum5(_lc)
    
    # Create a bitarray from the 4 bytes of LC data (includes 5-bit checksum).
    _binlc = bitarray(endian='big')
    _binlc.frombytes(_lc)
    
    # Insert the checksum bits at the right location in the matrix (this is actually faster than with a for loop)
    _binlc.insert(32,_csum[0])
    _binlc.insert(43,_csum[1])
    _binlc.insert(54,_csum[2])
    _binlc.insert(65,_csum[3])
    _binlc.insert(76,_csum[4])

    # Insert the hamming bits at the right location in the matrix
    for index in range(0,112,16):
        for hindex,hbit in zip(range(index+11,index+16), hamming.enc_16114(_binlc[index:index+11])):
            _binlc.insert(hindex,hbit)
    
    # Insert the column parity bits at the right location in the matrix
    for index in range(0,16):
        _binlc.insert(index+112, _binlc[index+0] ^ _binlc[index+16] ^ _binlc[index+32] ^ _binlc[index+48] ^ _binlc[index+64] ^ _binlc[index+80] ^ _binlc[index+96])
    
    # Create Embedded LC segments in 48 bit blocks
    emblc_b = bitarray(endian='big')
    emblc_b.extend([_binlc[0], _binlc[16],_binlc[32],_binlc[48],_binlc[64],_binlc[80],_binlc[96], _binlc[112]])
    emblc_b.extend([_binlc[1], _binlc[17],_binlc[33],_binlc[49],_binlc[65],_binlc[81],_binlc[97], _binlc[113]])
    emblc_b.extend([_binlc[2], _binlc[18],_binlc[34],_binlc[50],_binlc[66],_binlc[82],_binlc[98], _binlc[114]])
    emblc_b.extend([_binlc[3], _binlc[19],_binlc[35],_binlc[51],_binlc[67],_binlc[83],_binlc[99], _binlc[115]])
    
    emblc_c = bitarray(endian='big')
    emblc_c.extend([_binlc[4], _binlc[20],_binlc[36],_binlc[52],_binlc[68],_binlc[84],_binlc[100],_binlc[116]])
    emblc_c.extend([_binlc[5], _binlc[21],_binlc[37],_binlc[53],_binlc[69],_binlc[85],_binlc[101],_binlc[117]])
    emblc_c.extend([_binlc[6], _binlc[22],_binlc[38],_binlc[54],_binlc[70],_binlc[86],_binlc[102],_binlc[118]])
    emblc_c.extend([_binlc[7], _binlc[23],_binlc[39],_binlc[55],_binlc[71],_binlc[87],_binlc[103],_binlc[119]])
    
    emblc_d = bitarray(endian='big')
    emblc_d.extend([_binlc[8], _binlc[24],_binlc[40],_binlc[56],_binlc[72],_binlc[88],_binlc[104],_binlc[120]])
    emblc_d.extend([_binlc[9], _binlc[24],_binlc[41],_binlc[57],_binlc[73],_binlc[89],_binlc[105],_binlc[121]])
    emblc_d.extend([_binlc[10],_binlc[26],_binlc[42],_binlc[58],_binlc[74],_binlc[90],_binlc[106],_binlc[122]])
    emblc_d.extend([_binlc[11],_binlc[27],_binlc[43],_binlc[59],_binlc[75],_binlc[91],_binlc[107],_binlc[123]])
    
    emblc_e = bitarray(endian='big')
    emblc_e.extend([_binlc[12],_binlc[28],_binlc[44],_binlc[60],_binlc[76],_binlc[92],_binlc[108],_binlc[124]])
    emblc_e.extend([_binlc[13],_binlc[29],_binlc[45],_binlc[61],_binlc[77],_binlc[93],_binlc[109],_binlc[125]])
    emblc_e.extend([_binlc[14],_binlc[30],_binlc[46],_binlc[62],_binlc[78],_binlc[94],_binlc[110],_binlc[126]])
    emblc_e.extend([_binlc[15],_binlc[31],_binlc[47],_binlc[63],_binlc[79],_binlc[95],_binlc[111],_binlc[127]])
    
    return({1: emblc_b, 2: emblc_c, 3: emblc_d, 4: emblc_e})

#------------------------------------------------------------------------------
# Used to execute the module directly to run built-in tests
#------------------------------------------------------------------------------

if __name__ == '__main__':
    from binascii import b2a_hex as ahex
    from time import time
        
    # Validation Example
    
    voice_h = b'\x2b\x60\x04\x10\x1f\x84\x2d\xd0\x0d\xf0\x7d\x41\x04\x6d\xff\x57\xd7\x5d\xf5\xde\x30\x15\x2e\x20\x70\xb2\x0f\x80\x3f\x88\xc6\x95\xe2'
    voice_hb = bitarray(endian='big')
    voice_hb.frombytes(voice_h)
    voice_hb = voice_hb[0:98] + voice_hb[166:264]
    
    # Header LC -- Terminator similar
    lc = b'\x00\x10\x20\x00\x0c\x30\x2f\x9b\xe5'   # \xda\xd4\x5a
    t0 = time()
    full_lc_encode = encode_header_lc(lc)
    t1 = time()
    encode_time = t1-t0
    
    t0 = time()
    full_lc_dec = decode_full_lc(full_lc_encode)
    t1 = time()
    decode_time = t1-t0
    
    print('VALIDATION ROUTINES:')
    print('Orig Data:     {}, {} bytes'.format(ahex(lc), len(lc)))
    print('Orig Encoded:  {}, {} bytes'.format(ahex(voice_hb.tobytes()), len(voice_hb.tobytes())))
    print()
    print('BPTC(196,96):')
    print('Encoded data:  {}, {} bytes'.format(ahex(full_lc_encode.tobytes()), len(full_lc_encode.tobytes())))
    print('Encoding time: {} seconds'.format(encode_time))
    print('Decoded data:  {}'.format(ahex(full_lc_dec.tobytes())))
    print('Decode Time:   {} seconds'.format(decode_time))

    # Embedded LC
    t0 = time()
    emblc = encode_emblc(lc)
    t1 = time()
    encode_time = t1 -t0
    
    t0 = time()
    decemblc = decode_emblc(emblc[1] + emblc[2] + emblc[3] + emblc[4])
    t1 = time()
    decode_time = t1 -t0
    
    print('\nEMBEDDED LC:')
    print('Encoded Data:  Burst B:{} Burst C:{} Burst D:{} Burst E:{}'.format(ahex(emblc[1].tobytes()), ahex(emblc[2].tobytes()), ahex(emblc[3].tobytes()), ahex(emblc[4].tobytes())))
    print('Endoding Time: {}'.format(encode_time))
    print('Decoded data:  {}'.format(ahex(decemblc)))
    print('Decoding Time: {}'.format(decode_time))    