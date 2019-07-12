# Copyright (c) Alex Ellis 2017. All rights reserved.
# Copyright (c) OpenFaaS Author(s) 2018. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import sys
from function import handler

def get_stdin():
    buf = bytearray()
    while(True):
        line = bytearray(sys.stdin.buffer.readline())
        buf.extend(line)
        if line == b'':
            break
    return buf

if __name__ == "__main__":
    st = get_stdin()
    ret = handler.handle(st)
    print(ret)
