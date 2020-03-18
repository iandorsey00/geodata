import string
import pandas as pd
import numpy

def gdt(input_val, dtype='default', verbose=False, not_num=numpy.nan, allow_negs=True):
    '''Aggressive, error-tolerant typecasting to clean up dirty data.'''
    # Handle values that are already numbers
    if isinstance(input_val, int) or isinstance(input_val, float):
        if verbose:
            print('gdt: {} is already already a number.'.format(input_val))
        return input_val

    # Handle anything else that's not a string.
    if not isinstance(input_val, str):
        if verbose:
            print('gdt: {} is not a number or string.'.format(input_val))
        return not_num

    negative = False

    # Check to see if the input is negative.
    if input_val[0] == '-':
        negative = True

    # Remove everything except digits and decimals, and negatives signs.
    # fs = filtered_string
    fs = ''.join(filter(lambda x: x.isdigit() or x == '.', list(input_val)))

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
            filter(lambda x: not(x.isdigit() or x == '.'), list(input_val)))
        print("gdt: Removed chars '%s' from '%s'" % (not_fs, input_val))

    # If fs has only decimals, change it to an empty string.
    if ''.join(set(fs)) == '.':
        fs = ''

    # If there were no digits in the input_val, return value specified by the
    # not_num argument.
    if fs == '':
        return not_num
    
    # If the input was negatives and negatives are allowed, prepend '-'
    if negative and allow_negs:
        fs = '-' + fs

    # By default, return an int if there is a decimal and a float otherwise.
    if dtype == 'default':
        if '.' in input_val:
            return float(fs)
        else:
            return int(fs)
    # If dype is int, remove everything before the decimal
    # (if there is one, then return.)
    elif dtype == 'int':
        fs = ''.join(fs.split('.')[0])
        return int(fs)
    # Otherwise, return a float.
    elif dtype == 'float':
        return float(fs)

def gdti(input_val, verbose=False, not_num=numpy.nan, allow_negs=True):
    '''A wrapper function that only returns ints.'''
    return gdt(input_val, dtype='int', verbose=False, not_num=numpy.nan)

def gdtf(input_val, verbose=False, not_num=numpy.nan, allow_negs=True):
    '''A wrapper function that only returns floats.'''
    return gdt(input_val, dtype='float', verbose=False, not_num=numpy.nan)
