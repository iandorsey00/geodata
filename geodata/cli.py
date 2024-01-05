import argparse
from engine import Engine

class GeodataCLI:
    def __init__(self):
        self.engine = Engine()

        self.ct = self.engine.ct
        self.st = self.engine.st
        self.kt = self.engine.kt
        self.slt = self.engine.slt

        #######################################################################
        # Argument parsing with argparse

        # Create the top-level argument parser
        parser = argparse.ArgumentParser(
            description='Displays information for geographies in the U.S.',
            prog='geodata')
        # Create top-level subparsers
        subparsers = parser.add_subparsers(
            help='enter geodata <subcommand> -h for more information.')

        # Top-level subparser
        # Create the parsor for the "createdb" command
        createdb_parser = subparsers.add_parser('createdb', aliases=['c'])
        createdb_parser.add_argument('path', help='path to data files')
        createdb_parser.set_defaults(func=self.create_data_products)

        # Create the parser for the "view" command
        view_parsers = subparsers.add_parser('view', aliases=['v'])
        # Create subparsers for the "view" command
        view_subparsers = view_parsers.add_subparsers(
            help='enter geodata view <subcommand> -h for more information.')

        # Create the parser for the "search" command
        search_parser = subparsers.add_parser('search', aliases=['s'],
            description='Search for a display label (place name)')
        search_parser.add_argument('query', help='search query')
        search_parser.add_argument('-n', type=int, default=15, help='number of results to display')
        search_parser.set_defaults(func=self.display_label_search)

        # Create the parser for the "tocsv" command
        tocsv_parser = subparsers.add_parser('tocsv', aliases=['t'],
            description='Output data in CSV format')
        tocsv_subparsers = tocsv_parser.add_subparsers(
            help='enter geodata tocsv <subcommand> -h for more information.')

        # View subparser
        # Create parsors for the view command
        # DemographicProfiles #################################################
        dp_parsor = view_subparsers.add_parser('dp',
            description='View a DemographicProfile.')
        dp_parsor.add_argument('display_label', help='the exact place name')
        dp_parsor.set_defaults(func=self.get_dp)

        # GeoVectors [standard mode] ##########################################
        gv_parsor = view_subparsers.add_parser('gv',
            description='View GeoVectors nearest to a GeoVector.')
        gv_parsor.add_argument('display_label', help='the exact place name')
        gv_parsor.add_argument('-c', '--context', help='geographies to compare with')
        gv_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
        gv_parsor.set_defaults(func=self.compare_geovectors)

        # GeoVectors [appearance mode] ########################################
        gva_parsor = view_subparsers.add_parser('gva',
            description='View GeoVectors nearest to a GeoVector [appearance mode]')
        gva_parsor.add_argument('display_label', help='the exact place name')
        gva_parsor.add_argument('-c', '--context', help='geographies to compare with')
        gva_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
        gva_parsor.set_defaults(func=self.compare_geovectors_app)

        # Highest values ######################################################
        hv_parsor = view_subparsers.add_parser('hv',
            description='View geographies that rank highest with regard to comp')
        hv_parsor.add_argument('comp', help='the comp that you want to rank')
        hv_parsor.add_argument('-d', '--data_type', help='c: component; cc: compound')
        hv_parsor.add_argument('-f', '--geofilter', help='filter by criteria')
        hv_parsor.add_argument('-c', '--context', help='group of geographies to display')
        hv_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
        hv_parsor.set_defaults(func=self.extreme_values)

        # Lowest values #######################################################
        lv_parsor = view_subparsers.add_parser('lv',
            description='View geographies that rank lowest with regard to comp')
        lv_parsor.add_argument('comp', help='the comp that you want to rank')
        lv_parsor.add_argument('-d', '--data_type', help='c: component; cc: compound')
        lv_parsor.add_argument('-f', '--geofilter', help='filter by criteria')
        lv_parsor.add_argument('-c', '--context', help='group of geographies to display')
        lv_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
        lv_parsor.set_defaults(func=self.lowest_values)

        # Closest geographies #################################################
        cg_parsor = view_subparsers.add_parser('cg',
            description='View geographies that are closest to the one specified by display_label')
        cg_parsor.add_argument('display_label', help='the exact place name')
        cg_parsor.add_argument('-f', '--geofilter', help='filter by criteria')
        cg_parsor.add_argument('-c', '--context', help='group of geographies to display')
        cg_parsor.add_argument('-n', type=int, default=15, help='number of rows to display')
        cg_parsor.set_defaults(func=self.closest_geographies)

        # Distance ############################################################
        d_parsor = view_subparsers.add_parser('d',
            description='Get the distance between two places')
        d_parsor.add_argument('display_label_1', help='Get the distance between this display label and...')
        d_parsor.add_argument('display_label_2', help='...this one.')
        d_parsor.add_argument('-k', '--kilometers', action='store_true', help='Display result in kilometers.')
        d_parsor.set_defaults(func=self.distance)

        # tocsv subparsers
        # Create parsors for the tocsv command
        # Rows ################################################################
        rows_parsor = tocsv_subparsers.add_parser('rows',
            description='Output data rows in CSV format')
        rows_parsor.add_argument('comps', help='components or compounds to output')
        rows_parsor.add_argument('-f', '--geofilter', help='filter by criteria')
        rows_parsor.add_argument('-c', '--context', help='group of geographies')
        rows_parsor.add_argument('-n', type=int, default=0, help='number of rows to display')
        rows_parsor.set_defaults(func=self.rows)

        # DemographicProfile ##################################################
        csv_dp_parsor = tocsv_subparsers.add_parser('dp',
            description='Output a DemographicProfile in CSV format')
        csv_dp_parsor.add_argument('display_label', help='the exact place name')
        csv_dp_parsor.set_defaults(func=self.get_csv_dp)

        # Parse arguments
        args = parser.parse_args()

        # try/except is necessary here due to a bug in argparse -- an
        # AttributeError may be invoked if the program is run with too few
        # arguments.
        try:
            args.func(args)
        except AttributeError:
            parser.error("Too few arguments")

    def create_data_products(self, args):
        self.engine.create_data_products(args.path)

    def display_label_search(self, args):
        search_results = self.engine.display_label_search(**vars(args))

        def print_search_divider():
            return '-' * 68

        def print_search_result(dpi):
            '''Print a row for search results.'''
            iam = ' '

            out_str = iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
                        + getattr(dpi, 'fc')['population'].rjust(20)
            return out_str

        print(print_search_divider())

        iam = ' '
        
        print(iam + 'Search results'.ljust(45)[:45] + iam + \
            'Total population'.rjust(20))

        print(print_search_divider())

        for dpi_instance in search_results[:args.n]:
            print(print_search_result(dpi_instance))

        print(print_search_divider())

    def get_dp(self, args):
        dp_list = self.engine.get_dp(**vars(args))
        print(dp_list[0])

    def compare_geovectors(self, args, mode='std'):
        closest_gvs = self.engine.compare_geovectors(**vars(args), mode=mode)
        comparison_gv = closest_gvs[0]

        if len(closest_gvs) == 0:
            print("Sorry, no GeoVectors match your criteria.")
        else:
            if mode == 'std':
                width = 105
            elif mode == 'app':
                width = 85

            print("The most demographically similar geographies are:")
            print()
            print('-' * width)
            if mode == 'std':
                print(' Geography'.ljust(41), 'County'.ljust(20), 'PDN', 'PCI', 'WHT', 'BLK', 'ASN', 'HPL', 'BDH', 'GDH', ' Distance')
            elif mode == 'app':
                print(' Geography'.ljust(41), 'County'.ljust(20), 'PDN', 'PCI', 'MYS', ' Distance')
            print('-' * width)

            # Print these GeoVectors
            for closest_pv in closest_gvs:
                print('', closest_pv.display_row(mode),
                    round(comparison_gv.distance(closest_pv, mode=mode), 2))

            print('-' * width)

    def compare_geovectors_app(self, args):
        self.compare_geovectors(args, mode='app')

    def extreme_values(self, args, lowest=False):
        evs = self.engine.extreme_values(**vars(args), lowest=lowest)
        fetch_one = evs[0]

        sort_by, print_ = self.engine.get_data_types(args.comp, args.data_type, fetch_one)

        # helper methods for printing [hl]v rows ##############################

        # The inter-area margin to divide display sections
        iam = ' '

        def divider(dpi):
            '''Print a divider for DemographicProfiles'''
            if args.comp == 'population':
                return '-' * 68
            else:
                return '-' * 89

        def ev_print_headers(comp, universe_sl, group_sl, group):
            '''Helper method to DRY up sl_print_headers'''

            # Set the name of the universe
            if universe_sl:
                if universe_sl == '040':
                    universe = 'State'
                elif universe_sl == '050':
                    universe = 'County'
                elif universe_sl == '160':
                    universe = 'Place'
                elif universe_sl == '310':
                    universe = 'Metro/micro area'
                elif universe_sl == '400':
                    universe = 'Urban area'
                elif universe_sl == '860':
                    universe = 'ZCTA'
            else:
                universe = 'Geography'

            if group:
                group_name = ''

                if group_sl == '040':
                    group_name = self.st.get_name(group)
                elif group_sl == '050':
                    key = 'us:' + group + '/county'
                    group_name = self.kt.key_to_county_name[key]
                elif group_sl == '860':
                    group_name = group
                
                # Output '<UNIVERSE GEOGRAPHY> in <GROUP NAME>'
                out_str = iam + (universe + ' in ' \
                    + group_name).ljust(45)[:45] + iam \
                    + getattr(dpi, 'rh')['population'].rjust(20)
            else:
                out_str = iam + universe.ljust(45)[:45] + iam \
                    + getattr(dpi, 'rh')['population'].rjust(20)

            # Print another column if the comp isn't population
            if args.comp != 'population':
                out_str += iam + getattr(dpi, 'rh')[args.comp].rjust(20)[:20]

            return out_str

        # dpi = demographicprofile_instance
        def ev_print_row(dpi):
            '''Print a data row for DemographicProfiles'''
            out_str = iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
                    + getattr(dpi, 'fc')['population'].rjust(20)
            if args.comp != 'population':
                out_str += iam + getattr(dpi, print_)[args.comp].rjust(20)[:20]
            return out_str

        # Printing ############################################################

        universe_sl, group_sl, group = self.slt.unpack_context(args.context)

        if len(evs) == 0:
            print("Sorry, no geographies match your criteria.")
        else:
            # Print the header and places with their information.
            dpi = self.engine.d['demographicprofiles'][0]
            print(divider(dpi))
            print(ev_print_headers(args.comp, universe_sl, group_sl, group))
            print(divider(dpi))
            for ev in evs[:args.n]:
                print(ev_print_row(ev))
            print(divider(dpi))
    
    def lowest_values(self, args):
        self.extreme_values(args, lowest=True)

    def closest_geographies(self, args):
        cgs = self.engine.closest_geographies(**vars(args))

        # Helper methods for printing cg rows #################################

        # The inter-area margin to divide display sections
        iam = ' '

        def divider():
            '''Print a divider for DemographicProfiles'''
            return '-' * 68

        def cg_print_headers(universe_sl, group_sl, group):
            '''Helper method to DRY up sl_print_headers'''

            # Set the name of the universe
            if universe_sl:
                if universe_sl == '040':
                    universe = 'State'
                elif universe_sl == '050':
                    universe = 'County'
                elif universe_sl == '160':
                    universe = 'Place'
                elif universe_sl == '310':
                    universe = 'Metro/micro area'
                elif universe_sl == '400':
                    universe = 'Urban area'
                elif universe_sl == '860':
                    universe = 'ZCTA'
            else:
                universe = 'Geography'

            if group:
                group_name = ''

                if group_sl == '040':
                    group_name = self.st.get_name(group)
                elif group_sl == '050':
                    key = 'us:' + group + '/county'
                    group_name = self.kt.key_to_county_name[key]
                elif group_sl == '860':
                    group_name = group
                
                # Output '<UNIVERSE GEOGRAPHY> in <GROUP NAME>'
                out_str = iam + (universe + ' in ' \
                    + group_name).ljust(45)[:45] + iam \
                    + 'Distance (mi)'.rjust(20)
            else:
                out_str = iam + universe.ljust(45)[:45] + iam \
                    + 'Distance (mi)'.rjust(20)

            return out_str

        # dpi = demographicprofile_instance
        def cg_print_row(dpi, distance):
            '''Print a data row for DemographicProfiles'''
            out_str = iam + getattr(dpi, 'name').ljust(45)[:45] + iam \
                    + str(round(distance, 1)).rjust(20)
            return out_str

        # Printing ############################################################

        universe_sl, group_sl, group = self.slt.unpack_context(args.context)

        if len(cgs) == 0:
            print("Sorry, no geographies match your criteria.")
        else:
            # Print the header and places with their information.
            print(divider())
            print(cg_print_headers(universe_sl, group_sl, group))
            print(divider())
            for cg in cgs[:args.n]:
                print(cg_print_row(*cg))
            print(divider())

    def distance(self, args):
        print(self.engine.distance(**vars(args)))

    def rows(self, args):
        self.engine.rows(**vars(args))

    def get_csv_dp(self, args):
        self.engine.get_csv_dp(**vars(args))

gcli = GeodataCLI()
