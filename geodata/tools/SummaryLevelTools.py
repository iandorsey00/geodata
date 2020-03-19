class SummaryLevelTools:
    '''Tools to convert summary levels into their codes and vice-versa.'''
    def __init__(self):
        self.keyword_to_code = {
            'zctas': '860',
            'z': '860',
            'places': '160',
            'p': '160',
            'counties': '050',
            'c': '050',
            'states': '040',
            's': '040',
        }

        self.code_to_keyword = {
            '860': 'zctas',
            '160': 'places',
            '050': 'counties',
            '040': 'states',
        }

    def iskeyword(self, input_str):
        '''Determines whether input_str is a summary level keyword'''
        if input_str in self.keyword_to_code.keys():
            return True
        else:
            return False

    def iscode(self, input_str):
        '''Determines whether input_str is a summary level code'''
        if input_str in self.code_to_keyword.keys():
            return True
        else:
            return False

    def unpack_context(self, context):
        '''Get the universe summary level, group summary level, and group.'''
        ac_split = []
        universe_sl = None
        group_sl = None
        group = None

        # If there is a plus in the context:
        if '+' in context:
            # Get the part before the plus
            ac_split = context.split('+')
            universe_sl = ac_split[0]
            group = ac_split[1]

            # If the part before the plus is a valid keyword:
            if self.iskeyword(universe_sl):
                # Set the keyword to the corresponding code.
                universe_sl = self.keyword_to_code[universe_sl]
            # Otherwise, if the part before the plus is a valid code...
            elif self.iscode(universe_sl):
                # The universe_sl has been entered directly. Do nothing.
                pass
            else:
                # Otherwise, there has been an error.
                raise ValueError('The context summary level is not valid.')
        else:
            group = context
        
        # If there is something after the plus...
        if group != '':
            # If there is a colon, there is grouping by county
            if ':' in context:
                group_sl = '050'
            # Otherwise, there is grouping by state.
            else:
                group_sl = '040'

        # Suggested usage:
        # from tools.SummaryLevelTools import SummaryLevelTools
        # slt = SummaryLevelTools()
        # universe_sl, group_sl, group = slt.unpack_context(args.context)
        return (universe_sl, group_sl, group)

