dmr_utils3
_________

**IMPORTANT UPDATE: This module is now available through pypi and may be installed just like any other globally available python module, i.e. "pip install dmr_utils" or "easy_install dmr_utils". It is HIGHLY recommended that users (not developers or those specifically working with me to test code) use that method.**

Utilities for working with Digital Moble Radio (DMR) in python. Includes routines for assembling and disasembling packets and encoding/removing FEC/ECC routines. The utilities are intended primarily for processing on the "network" side of DMR, not the air interface -- such as for building network linking tools, and as such, routines mostly remove FEC/ECC rather than apply repairs, which should be done at the air interface first.

**Files in this repository and what they do**

const.py
  A number of constant values that are handy for working with DMR. Just look through the file. Some are hex strings, some are bitarrays. Some are straight objects, and in cases where there are related data sets you'll find dictionaries.

utils.py
  There are currently two parts of utils.py. One part is about converting integer an hex values (usually radio and group IDs, etc.) back and forth. Radio IDs, etc. are always transmitted and recieved as hex strings, but that makes them hard to work with in other ways. The other part is about creating dictionaries that can be used to lookup subscriber, peer, and talkgroup IDs and turn them into friendly names.

- **hex_str_2(_int_id):** Returns a 2-byte (with leading zeros) hex string representation of a 2-byte *_int_id*.
- **hex_str_3(_int_id):** Returns a 3-byte (with leading zeros) hex string representation of a 3-byte *_int_id*.
- **hex_str_4(_int_id):** Returns a 4-byte (with leading zeros) hex string representation of a 4-byte *_int_id*.
- **int_id(_hex_string):** Returns an integer version of a supplied *_hex_string*.
- **try_download(_path, _file, _url, _stale):** Download a new *_file* from *_url* and save it at the right *_path* if the existing file isn't there or is older than *_stale* in seconds. It is expected that this is a .csv file downloaded from DMR-MARC.
- **mk_id_dict(_path, _file:** Make an ID dictionary from the *_file* located on the *_path*. Returns a dictionary.
- **get_info(_id, _dict):** Get the *_id* from the *_dict*, where *_id* is expected to be an integer. Returns an integer.
- **get_alias(_id, _dict):** Get the *_id* from the *_dict*, where *_id* is a hex string. Returns an integer.

encode.py
  There is nothing in this file yet.
  
decode.py
  some stuff
  
btpc.py
  Contains block product turbo code generators, extractors and related routines
  
- **decode_full_lc(_data):** Extracts the useful FULL LC data without checking for errors. Accepts one argument of type bitarray and returns one item of type bitarray.
- **interleave_19696(_data):** Accepts one argument of type bitarray and returns a bitarray interlieaved.
- **encode_19696(_data):** Accepts an LC as a 12-byte string (LC and RS1293 FEC) encodes it into a 196bit bitarray and builds the proper row and column structure with hamming codes and returns a type bitarray
- **encode_header_lc(_lc):** Accpets LC data as a bitarray, applies the header mask and appends RS1293 FEC, encodes BPTC19696, interleaves for transmition. Returns a type bitarray that is the full DMR LC header packet.
- **encode_terminator_ls(_lc):** Accepts LC data as a bitarray, applies the terminator mask and appends RS1293 FEC, encodes BPTC19696, interleaves for transmition. Returns a type bitarray that is the full DMR LC terminator packet.
- **decode_emblc(_elc):** Extracts the useful EMBEDDED LC data without checking for errors. Accepts a type bitarray and returns type string.
- **encode_emblc(_lc):** Accepts 12 byte LC as a string, adds 5-byte checksum, adds row hamming bits, column partiy bits and arranges the matrix for transmission. Returns a type dict with 4 key/value pairs. Keys 1-4 are DMR bursts b-e respectively, such that burst "B" is key 1's associated value and so on.
  
crc.py
  CRC calculator. So far, only one CRC calculation here.
  
- **csum5(_data):** Create a 5-bit CRC from the supplied *_data*, which is assumed to be an LC string. Returns a 5-bit bitarray.
  
rs129.py
  Reed Solomon 12,9,3 ECC FEC encoder/decoder. Some methods are not listed here if they are intended to be used only within the module.
  
- **encode(_msg):** Accepts *_msg*, a 9-byte hex string and returns a type list of 3 parity bytes.
- **lc_header_encode(_message):** Accepts a 9-byte LC message. Calculates and returns the 3 byte hex string Reed Solomon 12,9,3 ECC with the voice header mask applied.
- **lc_terminator_encode(_message):** Accepts a 9-byte LC message. Calculates and returns the 3 byte hex string Reed Solomon 12,9,3 ECC with the voice terminator mask applied.
  
golay.py
  Golay codes necessary for working with DMR. At least some of them, that is. These are generally used by other modules, not directly.
  
- **encode_2087(_data):** Accepts 1-byte integer and returns a Golay 20,8,7 encoded 2-byte hex string.
- **decode_2087(_data):** Accepts a 3-byte hex string and returns a one-byte Golay 20,8,7 decoded integer.
  
hamming.py
  Hamming codes necessary for working with DMR. At least some of them, that is. These ar generally used by other modules, not directly.
  
- **enc_15113(_data):** Accepts a type bitarray, *_data* and returns a bitarray of length 4 with the hamming 15,11,3 checksum.
- **enc_1393(_data):** Accepts a type bitarray, *_data* and returns a bitarray of length 4 with the hamming 13,9,3 checksum.
- **enc_16114(_data):** Accepts a type bitarray, *_data* and returns a bitarray of length 5 with the hamming 16,11,4 checksum.
  
qr.py
  Quadratic Residue FEC for use in generating EMB data. In reality, the EMB can be generated from a lookup table more effectively than calcuating the QR FEC and creating the EMB from scratch because in amateur radio use (as of today) only a limited number of EMBs will actually ever be used. Routines here have not been completed for this reason, but may be some day.
