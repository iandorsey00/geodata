#
# geodata_typecast.py
#
# Aggressive, error-tolerant typecasting to clean up dirty data and suit the
# needs of geodata.
#

import string
import pandas as pd
import numpy

# Shorten the function name so that it can be used better when doing complex
# calculations
def gdt(input_str, dtype='default', verbose=False, no_digits=numpy.nan):
    # Remove everything except digits and decimals.
    # fs = filtered_string
    fs = ''.join(filter(lambda x: x.isdigit() or x == '.', list(input_str)))

    # Remove every decimal except the first.
    if '.' in fs:
        split_fs = fs.split('.')
        after_first_dec = ''.join(split_fs[1:])
        after_first_dec = after_first_dec.replace('.', '')
        fs = ''.join([split_fs[0], '.', after_first_dec])

    # If verbose is set to True, print information about what chars were
    # removed.
    if verbose:
        not_fs = ''.join(
            filter(lambda x: not(x.isdigit() or x == '.'), list(input_str)))
        print("gdt: Removed chars '%s' from '%s'" % (not_fs, input_str))

    # If fs has only decimals, change it to an empty string.
    if ''.join(set(fs)) == '.':
        fs = ''

    # If there were no digits in the input, return value specified by the
    # no_digits argument.
    if fs == '':
        return no_digits
    # Return value specified by dtype.
    elif dtype == 'default':
        if '.' in input_str:
            return float(fs)
        else:
            return int(fs)
    elif dtype == 'int':
        fs = ''.join(fs.split('.')[0])
        return int(fs)
    elif dtype == 'float':
        return float(fs)
