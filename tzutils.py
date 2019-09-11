"""Time zones from UTC offsets

Copyright (c) 2019 The University of Texas at Austin. All rights reserved.

Use and redistribution of this file is governed by the license terms in
the LICENSE file found in the project's top-level directory.
"""

import datetime

ZERO = datetime.timedelta(0)


class FixedOffsetTZInfo(datetime.tzinfo):
    """Time zone that is a fixed offset in minutes from UTC."""

    def __init__(self, offset_string):
        self.__offset = datetime.timedelta(
            hours=int(offset_string[0:3]),
            minutes=int(offset_string[0] + offset_string[3:5]))

    def __repr__(self):
        return 'FixedOffsetTZInfo(\'' + self.offsetstring() + '\')'

    def __str__(self):
        return self.offsetstring()

    def __getinitargs__(self):
        return (self.offsetstring(),)

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return None

    def dst(self, dt):
        return ZERO

    def offsetstring(self):
        offset_min = int(
            self.__offset.seconds / 60.0 + self.__offset.days * 24.0 * 60.0)
        offset_hr = int(offset_min / 60.0)
        offset_min = abs(offset_min) % 60
        return '{:+03}{:02}'.format(offset_hr, offset_min)


tz_cache = {}


def get_tz_for_offset(offset_string):
    """"Get a tzinfo for an offset, either a cached instance or new"""
    if offset_string in tz_cache:
        return tz_cache[offset_string]
    else:
        tz = FixedOffsetTZInfo(offset_string)
        tz_cache[offset_string] = tz
        return tz
