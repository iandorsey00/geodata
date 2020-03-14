'''
loaddata package

Loads data for use by geodata.
'''

def help():
    print('Usage: geodata ld path')
    print('Usage: geodata loaddata path')
    print()
    print('Sets the path of the data used by geodata to path.')
    print()
    print('Example: geodata ld ~/data/')
    print('         Sets the data path to ~/data/')

def loaddata(path):
    return path
