# geodata

geodata is a program that allows users to easily view and organized and
processed demographic data without the need to modify any data files.

Currently, this project supports places in the United States.

## Goals of this project

* Allow users to access demographic data without the need to modify any data
files.
* Allow users to access the data they need easily on their own system.
* Manage data from different summary levels easily (this is a future goal,
currently only places are supported.)
* Allow users to easily view both data available directly from Census files
(called "component data" in this program) and the data normally only available
by performing mathematical operations (called "compound data" in this program).
* Allow users to group data by counties (a future goal).

## Setup

This program doesn't include the required data files because they are too large.
In order to use geodata, the user has to download the required files and place
them in a directory of their choice, then generate the data products.

1. The 2018 ACS summary file for all summary levels except tracts and block
groups*, available
[here from the U.S. Census Bureau](https://www2.census.gov/programs-surveys/acs/summary_file/2018/data/5_year_entire_sf/All_Geographies_Not_Tracts_Block_Groups.zip)
(6.5 GB). After extracting all folders and subfolders, move all
the files from the subfolders to your data directory. If you are using Linux,
`cd` into the unzipped `All_Geographies_Not_Tracts_Block_Groups` directory
 and execute:

        find . -mindepth 2 -maxdepth 2 -type f -print -exec cp {} /path/to/your/data-dir/ \;

All files from all subfolders should now be in your data directory. These files
are geodata's primary source for data.

*geodata may work for ACS summary files for other years, but I have only tested
it with the 2018 ACS files.

2. Download the ACS 5-year sequence table number lookup file, available
[here from the U.S. Census Bureau](https://www2.census.gov/programs-surveys/acs/summary_file/2018/documentation/user_tools/ACS_5yr_Seq_Table_Number_Lookup.csv)
(1.6 MB). Place it in your data directory. This contains table metadata.

3. Download the 2019 National Places Gazetteer Files, available
[here from the U.S. Census Bureau](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2019_Gazetteer/2019_Gaz_place_national.zip)
(1.0 MB). This files contains geographic data, such as land area and geographic
coordinates.

4. This project depends on [pandas](https://pandas.pydata.org/) and
[SQLAlchemy](https://www.sqlalchemy.org/). Install these first. One way to do so
is by executing:

        $ pip3 install pandas sqlalchemy

5. You're now ready to checkout geodata with git. Execute, for example:

        $ git checkout git@github.com:iandorsey00/geodata

6. Now at the top level directory, execute

        $ python3 geodata createdb /path/to/data/dir

This will generate geodata's data products. On my system, generating the
database and the data products takes about one minute.

## Data products

Data products are available once they they have been saved by pickle to
`/bin/default.geodata`.

### `DemographicProfiles`

    usage: geodata view dp [-h] census_place_string

    View a DemographicProfile.

    positional arguments:
      census_place_string  the exact place name

    optional arguments:
      -h, --help           show this help message and exit

*Note: `view` above can be abbreviated as `v`*

View a standarized demographic profile for any place in the United States. For
example:

    $ python3 geodata v dp "San Francisco city, California"
    ---------------------------------------------------------------------
     San Francisco city, California                         
    ---------------------------------------------------------------------
     GEOGRAPHY                                              
     Land area                                                 46.9 sqmi 
     POPULATION                                             
     Total population                                            870,044 
     Population density                                    18,549.9/sqmi 
       Race                                                 
         White alone                             406,538           46.7% 
         Black alone                              45,402            5.2% 
         Asian alone                             297,667           34.2% 
         Other                                   120,437           13.8% 
       Hispanic or Latino (of any race)                     
         Hispanic or Latino                      132,651           15.2% 
     EDUCATION                                              
     Total population 25 years and older         689,551           79.3% 
       Bachelor's degree or higher               394,004           57.1% 
       Graduate degree or higher                 157,411           22.8% 
     INCOME                                                 
     Per capita income                                           $64,157 
     HOUSING                                                
     Median year unit built                                         1942 
     Median value                                             $1,009,500 
     Median rent                                                  $1,734 
    ---------------------------------------------------------------------

Note that `census_place_string` must be in quotes. The `census_place_string`
contains the name of the place, then a place type (most commonly "city," "town,"
"village," or "CDP"), then a comma, then the fully expanded state name. For
large cities, they most common place type will be "city;" for unincorporated
areas, it's generally "CDP." For example:

* New York city, New York
* Bethesda CDP, Maryland

### `PlaceVector`s and `PlaceVectorApp`s

    usage: geodata view pv [-h] [-c CONTEXT] census_place_string

    View PlaceVectors nearest to a PlaceVector.

    positional arguments:
      census_place_string   the exact place name

    optional arguments:
      -h, --help            show this help message and exit
      -c CONTEXT, --context CONTEXT
                            state to compare with