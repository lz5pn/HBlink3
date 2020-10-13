#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2017 Mike Zingman N4IRR
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

'''
'''
from binascii import b2a_hex as ahex
from bitarray import bitarray
from bitstring import BitArray
from bitstring import BitString

__author__     = 'Mike Zingman, N4IRR and Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2017 Mike Zingman N4IRR'
__credits__    = 'Cortney T. Buffington, N0MJS; Colin Durbridge, G4EML, Steve Zingman, N4IRS; Jonathan Naylor, G4KLX; Hans Barthen, DL5DI; Torsten Shultze, DG1HT'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'

##
# DMR AMBE interleave schedule
##
rW = [
      0, 1, 0, 1, 0, 1,
      0, 1, 0, 1, 0, 1,
      0, 1, 0, 1, 0, 1,
      0, 1, 0, 1, 0, 2,
      0, 2, 0, 2, 0, 2,
      0, 2, 0, 2, 0, 2
      ]

rX = [
      23, 10, 22, 9, 21, 8,
      20, 7, 19, 6, 18, 5,
      17, 4, 16, 3, 15, 2,
      14, 1, 13, 0, 12, 10,
      11, 9, 10, 8, 9, 7,
      8, 6, 7, 5, 6, 4
      ]

rY = [
      0, 2, 0, 2, 0, 2,
      0, 2, 0, 3, 0, 3,
      1, 3, 1, 3, 1, 3,
      1, 3, 1, 3, 1, 3,
      1, 3, 1, 3, 1, 3,
      1, 3, 1, 3, 1, 3
      ]

rZ = [
      5, 3, 4, 2, 3, 1,
      2, 0, 1, 13, 0, 12,
      22, 11, 21, 10, 20, 9,
      19, 8, 18, 7, 17, 6,
      16, 5, 15, 4, 14, 3,
      13, 2, 12, 1, 11, 0
      ]


# This function calculates [23,12] Golay codewords.
# The format of the returned longint is [checkbits(11),data(12)].
def golay2312(cw):
    POLY = 0xAE3                #/* or use the other polynomial, 0xC75 */
    cw = cw & 0xfff             # Strip off check bits and only use data
    c = cw                      #/* save original codeword */
    for i in range(1,13):       #/* examine each data bit */
        if (cw & 1):            #/* test data bit */
            cw = cw ^ POLY      #/* XOR polynomial */
        cw = cw >> 1            #/* shift intermediate result */
    return((cw << 12) | c)      #/* assemble codeword */

# This function checks the overall parity of codeword cw.
# If parity is even, 0 is returned, else 1.
def parity(cw):
    #/* XOR the bytes of the codeword */
    p = cw & 0xff
    p = p ^ ((cw >> 8) & 0xff)
    p = p ^ ((cw >> 16) & 0xff)
    
    #/* XOR the halves of the intermediate result */
    p = p ^ (p >> 4)
    p = p ^ (p >> 2)
    p = p ^ (p >> 1)
    
    #/* return the parity result */
    return(p & 1)

# Demodulate ambe frame (C1)
# Frame is an array [4][24]
def demodulateAmbe3600x2450(ambe_fr):
    pr = [0] * 115
    foo = 0

    # create pseudo-random modulator
    for i in range(23, 11, -1):
        foo = foo << 1
        foo = foo | ambe_fr[0][i]
    pr[0] = (16 * foo)
    for i in range(1, 24):
        pr[i] = (173 * pr[i - 1]) + 13849 - (65536 * (((173 * pr[i - 1]) + 13849) // 65536))
    for i in range(1, 24):
        pr[i] = pr[i] // 32768

    # demodulate ambe_fr with pr
    k = 1
    for j in range(22, -1, -1):
        ambe_fr[1][j] = ((ambe_fr[1][j]) ^ pr[k])
        k = k + 1
    return ambe_fr  # Pass it back since there is no pass by reference

def eccAmbe3600x2450Data(ambe_fr):
    ambe = bitarray()
    
    # just copy C0
    for j in range(23, 11, -1):
        ambe.append(ambe_fr[0][j])
    
#        # ecc and copy C1
#        gin = 0
#        for j in range(23):
#            gin = (gin << 1) | ambe_fr[1][j]
#
#        gout = BitArray(hex(golay2312(gin)))
#        for j in range(22, 10, -1):
#            ambe[bitIndex] = gout[j]
#            bitIndex += 1
    for j in range(22, 10, -1):
        ambe.append(ambe_fr[1][j])

    # just copy C2
    for j in range(10, -1, -1):
        ambe.append(ambe_fr[2][j])

    # just copy C3
    for j in range(13, -1, -1):
        ambe.append(ambe_fr[3][j])

    return ambe

# Convert a 49 bit raw AMBE frame into a deinterleaved structure (ready for decode by AMBE3000)
def convert49BitAmbeTo72BitFrames( ambe_d ):
    index = 0
    ambe_fr = [[None for x in range(24)] for y in range(4)]

    #Place bits into the 4x24 frames.  [bit0...bit23]
    #fr0: [P e10 e9 e8 e7 e6 e5 e4 e3 e2 e1 e0 11 10 9 8 7 6 5 4 3 2 1 0]
    #fr1: [e10 e9 e8 e7 e6 e5 e4 e3 e2 e1 e0 23 22 21 20 19 18 17 16 15 14 13 12 xx]
    #fr2: [34 33 32 31 30 29 28 27 26 25 24 x x x x x x x x x x x x x]
    #fr3: [48 47 46 45 44 43 42 41 40 39 38 37 36 35 x x x x x x x x x x]

    # ecc and copy C0: 12bits + 11ecc + 1 parity
    # First get the 12 bits that actually exist
    # Then calculate the golay codeword
    # And then add the parity bit to get the final 24 bit pattern

    tmp = 0
    for i in range(11, -1, -1):      #grab the 12 MSB
        tmp = (tmp << 1) | ambe_d[i]
    tmp = golay2312(tmp)               #Generate the 23 bit result
    parityBit = parity(tmp)
    tmp = tmp | (parityBit << 23)               #And create a full 24 bit value
    for i in range(23, -1, -1):
        ambe_fr[0][i] = (tmp & 1)
        tmp = tmp >> 1

    # C1: 12 bits + 11ecc (no parity)
    tmp = 0
    for i in range(23,11, -1) :         #grab the next 12 bits
        tmp = (tmp << 1) | ambe_d[i]
    tmp = golay2312(tmp)                    #Generate the 23 bit result
    for j in range(22, -1, -1):
        ambe_fr[1][j] = (tmp & 1)
        tmp = tmp >> 1;

    #C2: 11 bits (no ecc)
    for j in range(10, -1, -1):
        ambe_fr[2][j] = ambe_d[34 - j]

    #C3: 14 bits (no ecc)
    for j in range(13, -1, -1):
        ambe_fr[3][j] = ambe_d[48 - j];

    return ambe_fr
        
def interleave(ambe_fr):
    bitIndex = 0
    w = 0
    x = 0
    y = 0
    z = 0
    data = bytearray(9)
    for i in range(36):
        bit1 = ambe_fr[rW[w]][rX[x]] # bit 1
        bit0 = ambe_fr[rY[y]][rZ[z]] # bit 0


        data[bitIndex // 8] = ((data[bitIndex // 8] << 1) & 0xfe) | (1 if (bit1 == 1) else 0)
        bitIndex += 1

        data[bitIndex // 8] = ((data[bitIndex // 8] << 1) & 0xfe) | (1 if (bit0 == 1) else 0)
        bitIndex += 1

        w += 1
        x += 1
        y += 1 
        z += 1
    return data

def deinterleave(data):
    
    ambe_fr = [[None for x in range(24)] for y in range(4)]

    bitIndex = 0
    w = 0
    x = 0
    y = 0
    z = 0
    for i in range(36):
        bit1 = 1 if data[bitIndex] else 0
        bitIndex += 1

        bit0 = 1 if data[bitIndex] else 0
        bitIndex += 1

        ambe_fr[rW[w]][rX[x]] = bit1; # bit 1
        ambe_fr[rY[y]][rZ[z]] = bit0; # bit 0

        w += 1
        x += 1
        y += 1
        z += 1

    return ambe_fr

def convert72BitTo49BitAMBE( ambe72 ):
    ambe_fr = deinterleave(ambe72)                     # take 72 bit ambe and lay it out in C0-C3
    ambe_fr = demodulateAmbe3600x2450(ambe_fr)         # demodulate C1
    ambe49 = eccAmbe3600x2450Data(ambe_fr)             # pick out the 49 bits of raw ambe
    return ambe49

def convert49BitTo72BitAMBE( ambe49 ):
    ambe_fr = convert49BitAmbeTo72BitFrames(ambe49)    # take raw ambe 49 + ecc and place it into C0-C3
    ambe_fr = demodulateAmbe3600x2450(ambe_fr)         # demodulate C1
    ambe72 = interleave(ambe_fr);                      # Re-interleave it, returning 72 bits
    return ambe72

def testit():
    ambe72 = BitArray('0xACAA40200044408080')    #silence frame
    print('ambe72=',ambe72)
    
    ambe49 = convert72BitTo49BitAMBE(ambe72)
    print('ambe49=',ahex(ambe49.tobytes()))

    ambe72 = convert49BitTo72BitAMBE(ambe49)
    print('ambe72=',ahex(ambe72))
    
#------------------------------------------------------------------------------
# Used to execute the module directly to run built-in tests
#------------------------------------------------------------------------------

if __name__ == '__main__':
    testit()
