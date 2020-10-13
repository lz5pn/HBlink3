#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016-2018  Cortney T. Buffington, N0MJS <n0mjs@me.com>
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
from dmr_utils3 import bptc

# Does anybody read this stuff? There's a PEP somewhere that says I should do this.
__author__     = 'Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2016-2018 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__    = 'Jonathan Naylor, G4KLX; Ian Wraith'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'

def to_bits(_string):
    _bits = bitarray(endian='big')
    _bits.frombytes(_string)
    return _bits


def voice_head_term(_string):
    burst = to_bits(_string)
    info = burst[0:98] + burst[166:264]
    slot_type = burst[98:108] + burst[156:166]
    sync = burst[108:156]
    lc = bptc.decode_full_lc(info).tobytes()
    cc = to_bytes(slot_type[0:4])
    dtype = to_bytes(slot_type[4:8])
    return {'LC': lc, 'CC': cc, 'DTYPE': dtype, 'SYNC': sync}


def voice_sync(_string):
    burst = to_bits(_string)
    ambe = [0,0,0]
    ambe[0] = burst[0:72]
    ambe[1] = burst[72:108] + burst[156:192]
    ambe[2] = burst[192:264]
    sync = burst[108:156]
    return {'AMBE': ambe, 'SYNC': sync}
    
    
def voice(_string):
    burst = to_bits(_string)
    ambe = [0,0,0]
    ambe[0] = burst[0:72]
    ambe[1] = burst[72:108] + burst[156:192]
    ambe[2] = burst[192:264]
    emb = burst[108:116] + burst[148:156]
    embed = burst[116:148]
    cc = (to_bytes(emb[0:4]))
    lcss = (to_bytes(emb[5:7]))
    return {'AMBE': ambe, 'CC': cc, 'LCSS': lcss, 'EMBED': embed}


def to_bytes(_bits):
    add_bits = 8 - (len(_bits) % 8)
    if add_bits < 8:
        for bit in range(add_bits):
            _bits.insert(0,0)
    _string =  _bits.tobytes()
    return _string



#------------------------------------------------------------------------------
# Used to execute the module directly to run built-in tests
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    from binascii import b2a_hex as ahex
    from time import time
    
    # SAMPLE, KNOWN GOOD DMR BURSTS
    data_head  = b'\x2b\x60\x04\x10\x1f\x84\x2d\xd0\x0d\xf0\x7d\x41\x04\x6d\xff\x57\xd7\x5d\xf5\xde\x30\x15\x2e\x20\x70\xb2\x0f\x80\x3f\x88\xc6\x95\xe2'    
    voice_a    = b'\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6b\xb9\xe8\x81\x52\x67\x55\xfd\x7d\xf7\x5f\x71\x73\x00\x2a\x6b\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6a'
    voice_b    = b'\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6b\xb9\xe8\x81\x52\x61\x34\xe0\xf0\x60\x69\x11\x73\x00\x2a\x6b\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6a'
    voice_c    = b'\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6b\xb9\xe8\x81\x52\x61\x71\x71\x10\x04\x77\x41\x73\x00\x2a\x6b\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6a'
    voice_d    = b'\xb9\xe8\x81\x52\x61\x73\x00\x2a\x6b\x95\x4b\xe6\x50\x01\x70\xc0\x31\x81\xb7\x43\x10\xb0\x07\x77\xa6\xc6\xcb\x53\x73\x27\x89\x48\x3a'
    voice_e    = b'\x86\x5a\xe7\x61\x75\x55\xb5\x06\x01\xb7\x58\xe6\x65\x11\x51\x75\xa0\xf4\xe0\x71\x24\x81\x50\x01\xff\xf5\xa3\x37\x70\x61\x28\xa7\xca'
    voice_f    = b'\xee\xe7\x81\x75\x74\x61\x4d\xf2\xff\xcc\xf4\xa0\x55\x11\x10\x00\x00\x00\x0e\x24\x30\x59\xe7\xf9\xe9\x08\xa0\x75\x62\x02\xcc\xd6\x22'
    voice_term = b'\x2b\x0f\x04\xc4\x1f\x34\x2d\xa8\x0d\x80\x7d\xe1\x04\xad\xff\x57\xd7\x5d\xf5\xd9\x65\x01\x2d\x18\x77\xd2\x03\xc0\x37\x88\xdf\x95\xd1'
    
    embed_lc = bitarray()
    
    print('DMR PACKET DECODER VALIDATION\n')
    print('Header:')
    t0 = time()
    lc = voice_head_term(data_head)
    t1 = time()
    print('LC: OPT-{} SRC-{} DST-{}, SLOT TYPE: CC-{} DTYPE-{}'.format(ahex(lc['LC'][0:3]),ahex(lc['LC'][3:6]),ahex(lc['LC'][6:9]),ahex(lc['CC']),ahex(lc['DTYPE'])))
    print('Decode Time: {}\n'.format(t1-t0))
    
    print('Voice Burst A:')
    t0 = time()
    pkt = voice_sync(voice_a)
    t1 = time()
    print('VOICE SYNC: {}'.format(ahex(lc['SYNC'].tobytes())))
    print('AMBE 0: {}, {}'.format(pkt['AMBE'][0], len(pkt['AMBE'][0])))
    print('AMBE 1: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][1])))
    print('AMBE 2: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][2])))
    print(t1-t0, '\n')
    
    print('Voice Burst B:')
    t0 = time()
    pkt = voice(voice_b)
    embed_lc += pkt['EMBED']
    t1 = time()
    print('EMB: CC-{} LCSS-{}, EMBEDDED LC: {}'.format(ahex(pkt['CC']), ahex(pkt['LCSS']), ahex(pkt['EMBED'].tobytes())))
    print('AMBE 0: {}, {}'.format(pkt['AMBE'][0], len(pkt['AMBE'][0])))
    print('AMBE 1: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][1])))
    print('AMBE 2: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][2])))
    print(t1-t0, '\n')
    
    print('Voice Burst C:')
    t0 = time()
    pkt = voice(voice_c)
    embed_lc += pkt['EMBED']
    t1 = time()
    print('EMB: CC-{} LCSS-{}, EMBEDDED LC: {}'.format(ahex(pkt['CC']), ahex(pkt['LCSS']), ahex(pkt['EMBED'].tobytes())))
    print('AMBE 0: {}, {}'.format(pkt['AMBE'][0], len(pkt['AMBE'][0])))
    print('AMBE 1: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][1])))
    print('AMBE 2: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][2])))
    print(t1-t0, '\n')
    
    print('Voice Burst D:')
    t0 = time()
    pkt = voice(voice_d)
    embed_lc += pkt['EMBED']
    t1 = time()
    print('EMB: CC-{} LCSS-{}, EMBEDDED LC: {}'.format(ahex(pkt['CC']), ahex(pkt['LCSS']), ahex(pkt['EMBED'].tobytes())))
    print('AMBE 0: {}, {}'.format(pkt['AMBE'][0], len(pkt['AMBE'][0])))
    print('AMBE 1: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][1])))
    print('AMBE 2: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][2])))
    print(t1-t0, '\n')
    
    print('Voice Burst E:')
    t0 = time()
    pkt = voice(voice_e)
    embed_lc += pkt['EMBED']
    embed_lc = bptc.decode_emblc(embed_lc)
    t1 = time()
    print('EMB: CC-{} LCSS-{}, EMBEDDED LC: {}'.format(ahex(pkt['CC']), ahex(pkt['LCSS']), ahex(pkt['EMBED'].tobytes())))
    print('COMPLETE EMBEDDED LC: {}'.format(ahex(embed_lc)))
    print('AMBE 0: {}, {}'.format(pkt['AMBE'][0], len(pkt['AMBE'][0])))
    print('AMBE 1: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][1])))
    print('AMBE 2: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][2])))
    print(t1-t0, '\n')
    
    print('Voice Burst F:')
    t0 = time()
    pkt = voice(voice_f)
    t1 = time()
    print('EMB: CC-{} LCSS-{}, EMBEDDED LC: {}'.format(ahex(pkt['CC']), ahex(pkt['LCSS']), ahex(pkt['EMBED'].tobytes())))
    print('AMBE 0: {}, {}'.format(pkt['AMBE'][0], len(pkt['AMBE'][0])))
    print('AMBE 1: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][1])))
    print('AMBE 2: {}, {}'.format(pkt['AMBE'][1], len(pkt['AMBE'][2])))
    print(t1-t0, '\n')
    
    print('Terminator:')
    t0 = time()
    lc = voice_head_term(voice_term)
    t1 = time()
    print('LC: OPT-{} SRC-{} DST-{} SLOT TYPE: CC-{} DTYPE-{}'.format(ahex(lc['LC'][0:3]),ahex(lc['LC'][3:6]),ahex(lc['LC'][6:9]),ahex(lc['CC']),ahex(lc['DTYPE'])))
    print('Decode Time: {}\n'.format(t1-t0))