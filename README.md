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

    All files from all subfolders should now be in your data directory. These
    filesare geodata's primary source for data.

    *geodata may work for ACS summary files for other years, but I have only
    tested it with the 2018 ACS files.

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

#### `PlaceVector`s and `PlaceVectorApp`s

Usage for `PlaceVector`s:

    usage: geodata view pv [-h] [-c CONTEXT] census_place_string

    View PlaceVectors nearest to a PlaceVector.

    positional arguments:
      census_place_string   the exact place name

    optional arguments:
      -h, --help            show this help message and exit
      -c CONTEXT, --context CONTEXT
                            state to compare with

Usage for `PlaceVectorApp`s:

    usage: geodata view pva [-h] [-c CONTEXT] census_place_string

    View PlaceVectorApps nearest to a PlaceVectorApp

    positional arguments:
      census_place_string   the exact place name

    optional arguments:
      -h, --help            show this help message and exit
      -c CONTEXT, --context CONTEXT
                            state to compare with

*Note: `view` above can be abbreviated as `v`*

See `DemographicProfiles` for information regarding `census_place_string`s. At
this point in development, the option for the optional argument `CONTEXT` is a
lowercase state abbreviation (such as `ca`). When a `CONTEXT` is specified,
the `PlaceVector` that `census_place_string` represents will only be compared
to other `PlaceVector`s in the context (the same goes for `PlaceVectorApp`s).
Some examples of usage:

    $ python3 geodata v pv "Cupertino city, California" -c ny
    The most demographically similar places are:

    PlaceVector(Manhasset Hills CDP, New York
    s:('population_density', 100), ('per_capita_income', 100), ('white_alone', 27), ('black_alone', 52), ('asian_alone', 100), ('hispanic_or_latino', 54), ('bachelors_degree_or_higher', 83), ('graduate_degree_or_higher', 98))
    Distance: 5.482928049865327
    PlaceVector(Hartsdale CDP, New York
    s:('population_density', 100), ('per_capita_income', 100), ('white_alone', 37), ('black_alone', 56), ('asian_alone', 89), ('hispanic_or_latino', 58), ('bachelors_degree_or_higher', 88), ('graduate_degree_or_higher', 100))
    Distance: 6.73609679265374
    PlaceVector(Thomaston village, New York
    s:('population_density', 100), ('per_capita_income', 100), ('white_alone', 40), ('black_alone', 51), ('asian_alone', 100), ('hispanic_or_latino', 42), ('bachelors_degree_or_higher', 85), ('graduate_degree_or_higher', 100))
    Distance: 7.232738070744716
    PlaceVector(University Gardens CDP, New York
    s:('population_density', 100), ('per_capita_income', 100), ('white_alone', 32), ('black_alone', 50), ('asian_alone', 100), ('hispanic_or_latino', 54), ('bachelors_degree_or_higher', 81), ('graduate_degree_or_higher', 90))
    Distance: 8.5
    PlaceVector(Roslyn Heights CDP, New York
    s:('population_density', 100), ('per_capita_income', 100), ('white_alone', 38), ('black_alone', 58), ('asian_alone', 97), ('hispanic_or_latino', 58), ('bachelors_degree_or_higher', 80), ('graduate_degree_or_higher', 91))
    Distance: 9.75
    PlaceVector(Merritt Park CDP, New York
    s:('population_density', 95), ('per_capita_income', 94), ('white_alone', 32), ('black_alone', 59), ('asian_alone', 100), ('hispanic_or_latino', 53), ('bachelors_degree_or_higher', 83), ('graduate_degree_or_higher', 97))
    Distance: 10.253048327204938

    $ python3 geodata v pva "Sunnyvale city, California"
    The most demographically similar places are:

    PlaceVectorApp(Campbell city, California
    s:('population_density', 100), ('per_capita_income', 100), ('median_year_structure_built', 50))
    Distance: 0.0
    PlaceVectorApp(Cupertino city, California
    s:('population_density', 100), ('per_capita_income', 100), ('median_year_structure_built', 50))
    Distance: 0.0
    PlaceVectorApp(Dana Point city, California
    s:('population_density', 100), ('per_capita_income', 100), ('median_year_structure_built', 50))
    Distance: 0.0
    PlaceVectorApp(Foster City city, California
    s:('population_density', 100), ('per_capita_income', 100), ('median_year_structure_built', 50))
    Distance: 0.0
    PlaceVectorApp(Marina del Rey CDP, California
    s:('population_density', 100), ('per_capita_income', 100), ('median_year_structure_built', 50))
    Distance: 0.0
    PlaceVectorApp(Mountain View city, California
    s:('population_density', 100), ('per_capita_income', 100), ('median_year_structure_built', 50))
    Distance: 0.0

`PlaceVector`s and `PlaceVectorApp`s model places as multidimensional vectors
with their components being scores of 0 to 100. Each component represents a
demographic characteristic of a place, and the conversion of each component's
raw information to its score involves the median and standard deviation for that
component. Most often, 0 is scored as 0, the median value for that component
is scored as 50, and two standard deviations above the median is scored as
100.

#### The `PlaceVector` score calculation method in detail

The calculation method for `PlaceVector` scores for each subcomponent is usually
as follows:

* If the raw data is equal to zero, the score is zero.
* If the raw data is between zero and the median, it is equal to its proportion
  with the median times 50. In simple terms, we are giving the score a
  proportional value between 0 and 50, with 0 representing 0 and 50 representing
  the median.
* If the raw data is at the median, the score will be 50.
* If the raw data is between the median and two standard deviations above the
  median, its score will be 50 plus the proportion above the median with two
  standard deviations times 50. In simple terms, we are give the score a
  proportional value between 50 and 100, with 50 representing the median and
  100 representing two standard deviations above the median.
* If the raw data is at or above two standard deviations above the median,
  the score will be 100.

#### `PlaceVector`s

The aim of a standard `PlaceVector` is to calculate the general demographic
similarity of two areas. `PlaceVector`s are made up of the following
components:

* The population density component,
* The income component,
* The race component, which is made up of four subcomponents:
  * The proportion of the population which is White alone (25%),
  * The proportion of the population which is Black alone (25%),
  * The proportion of the population which is Asian alone (25%),
  * The proportion of the population which is Hispanic or Latino alone (25%),
    and
* The education component, which is made up of two subcomponents:
  * The proportion of those 25 years and older who have a Bachelor's degree or
    higher (50%), and
  * The proportion of those 25 years and older who have a graduate degree or
    higher (50%).

#### `PlaceVectorApp`s

The aim of a `PlaceVectorApp` is to calculate how similar two areas appear.
`PlaceVectorApp`s are made up of the following
components:

* The population density component,
* The income component, and
* The median year structure built component. This is the year for which the
  median house was built in the place. For this component, 1939 is treated as
  0 because the U.S. Census Bureau doesn't record median year structure built
  values before 1939.

## Other features

### Superlatives and antisuperlatives

Usage for superlatives:

    usage: geodata view sl [-h] [-p POP_FILTER] [-c CONTEXT] comp_name data_type

    View places that rank highest with regard to a certain characteristic.

    positional arguments:
      comp_name             the comp that you want to rank
      data_type             whether comp is a component or a compound

    optional arguments:
      -h, --help            show this help message and exit
      -p POP_FILTER, --pop_filter POP_FILTER
                            filter by population
      -c CONTEXT, --context CONTEXT
                            use geographies within state

Usage for antisuperlatives:

    usage: geodata view asl [-h] [-p POP_FILTER] [-c CONTEXT] comp_name data_type

    View places that rank lowest with regard to a certain characteristic.

    positional arguments:
      comp_name             the comp that you want to rank
      data_type             whether comp is a component or a compound

    optional arguments:
      -h, --help            show this help message and exit
      -p POP_FILTER, --pop_filter POP_FILTER
                            filter by population
      -c CONTEXT, --context CONTEXT
                            use geographies within state

*Note: `view` above can be abbreviated as `v`*

Superlatives and antisuperlatives allow you to get the geographies with the
highest or lowest values of a certain demographic characteristic. For example:

    $ python3 geodata v sl per_capita_income c -p 50000
    -----------------------------------------------------------------------------------------
     Place                                             Total population    Per capita income
    -----------------------------------------------------------------------------------------
     Bethesda CDP, Maryland                                      62,448              $95,165
     Newport Beach city, California                              86,280              $90,042
     Palo Alto city, California                                  67,019              $89,205
     Hoboken city, New Jersey                                    53,211              $86,413
     Mountain View city, California                              80,993              $73,924
     Santa Monica city, California                               92,078              $72,280
     Edina city, Minnesota                                       51,136              $71,090
     Newton city, Massachusetts                                  88,660              $69,859
     Arlington CDP, Virginia                                    231,803              $69,051
     Brookline CDP, Massachusetts                                59,234              $68,025
     Cupertino city, California                                  60,614              $67,888
     Sammamish city, Washington                                  64,049              $66,076
     Pleasanton city, California                                 80,847              $64,504
     San Francisco city, California                             870,044              $64,157
     Bellevue city, Washington                                  142,242              $63,115
     Reston CDP, Virginia                                        60,335              $63,027
     Sunnyvale city, California                                 152,323              $62,891
     The Woodlands CDP, Texas                                   109,843              $62,672
     Encinitas city, California                                  62,713              $62,251
     Catalina Foothills CDP, Arizona                             50,426              $61,998
     North Bethesda CDP, Maryland                                50,262              $61,905
     Coral Gables city, Florida                                  50,931              $61,668
     Walnut Creek city, California                               69,007              $61,026
     Redmond city, Washington                                    63,197              $60,465
     San Ramon city, California                                  75,384              $60,326
     Scottsdale city, Arizona                                   246,026              $59,953
     Carmel city, Indiana                                        90,163              $59,541
     Alexandria city, Virginia                                  156,505              $59,239
     Kirkland city, Washington                                   88,079              $59,224
     Boca Raton city, Florida                                    95,745              $59,193
    -----------------------------------------------------------------------------------------

Use the `comp_name` argument to specify the demographic component or compound
you want to rank. *Components* are pulled straight from census data files and
are generally numbers. `median_year_structure_built`, for example, is only
available as a component. *Compounds* are not available straight from the
census data files; they are the results of mathematical operations. For example,
the census doesn't provide information for `population_density`; the only way to
get it is to divide the population from the data files by the land area in the
gazetteer file.

Specify whether to rank by a component or compound with the `data_type`
argument; some data are available as both components and compounds, and others
are only available as one or the other.

A list of valid `comp_name`s and their `data_type`s are below:

* `population_density` – Population density: `cc` only
* `land_area` – Land area (in square miles): `c` only
* `white_alone` – White alone: `c` or `cc`
* `black_alone` – Black alone: `c` or `cc`
* `asian_alone` – Asian alone: `c` or `cc`
* `other_race` – Other race: `c` or `cc`
* `hispanic_or_latino` – Hispanic or Latino: `c` or `cc`
* `population_25_years_and_older` – Total population 25 years and older: `c` or
  `cc`
* `bachelors_degree_or_higher` – Bachelor's degree or higher: `c` or `cc`
* `graduate_degree_or_higher` – Graduate degree or higher: `c` or `cc`
* `per_capita_income` – Per capita income: `c` only
* `median_year_structure_built` – Median year housing unit built: `c` only
* `median_value` –  Median value of housing units: `c` only
* `median_rent` – Median rent of housing units: `c` only

In simple terms, for each item on the list, specify `c` for the `data_type` if
you just want a raw number, such as the number of people with a bachelor's
degree or higher. If you want a ratio or percentage (such as the *percent* of
people over age 25 with a bachelor's degree or higher), specify `cc` for the
`data_type`.

Sometimes, we're only interested in places with a population over a certain
threshold, say 50,000. To filter for places with population of 50,000 or more,
specify that with optional `-p` or `--pop_filter` arguments. Don't include
commas or other formatting when specifying a `pop_filter`.

Use the optional `-c` or `--context` arguments to limit the display to display
of geographies to those inside a single state. For example, if you are looking
for geographies with the newest housing units in the state of New York, specify
`-c ny` as below:

    $ python3 geodata view sl median_year_structure_built c -c ny
    -----------------------------------------------------------------------------------------
     Place in ny                                       Total population Median year unit built
    -----------------------------------------------------------------------------------------
     Merritt Park CDP, New York                                   1,776                 2006
     Livonia Center CDP, New York                                   330                 2002
     Northville CDP, New York                                     1,455                 2002
     Fort Drum CDP, New York                                     13,109                 2000
     Kiryas Joel village, New York                               23,536                 1998
     New Square village, New York                                 8,133                 1997
     Calcium CDP, New York                                        3,841                 1996
     Kaser village, New York                                      5,179                 1996
     Monsey CDP, New York                                        22,073                 1994
     University at Buffalo CDP, New York                          6,173                 1994
     Manorville CDP, New York                                    14,405                 1992
     Milton CDP (Saratoga County), New York                       3,111                 1991
     Gordon Heights CDP, New York                                 3,667                 1990
     Plattsburgh West CDP, New York                               1,370                 1990
     West Hampton Dunes village, New York                            69                 1989
     Moriches CDP, New York                                       3,277                 1988
     Rapids CDP, New York                                         1,198                 1988
     Armonk CDP, New York                                         4,381                 1987
     Davenport Center CDP, New York                                 222                 1987
     Freedom Plains CDP, New York                                   336                 1987
     Calverton CDP, New York                                      7,154                 1986
     Napeague CDP, New York                                         112                 1986
     North Hills village, New York                                5,639                 1986
     West Glens Falls CDP, New York                               7,005                 1986
     Baiting Hollow CDP, New York                                 1,654                 1985
     Heritage Hills CDP, New York                                 4,176                 1985
     South Lockport CDP, New York                                 7,315                 1985
     Clarence Center CDP, New York                                3,125                 1984
     Hannawa Falls CDP, New York                                    882                 1984
     Washingtonville village, New York                            5,748                 1984
    -----------------------------------------------------------------------------------------

## Information about data from the U.S. Census Bureau

At this point in geodata's development, all data the program uses comes from the
[U.S. Census Bureau](https://www.census.gov/).

### Geographies

The U.S. Census Bureau differentiates geographies types like the entire country,
states, counties, and places by classifying them as summary levels. There are
many more summary levels than those just mentioned. A partial list of summary
levels can be found [here](https://factfinder.census.gov/help/en/summary_level_code_list.htm).
You might notice some odd summary level names like "State-County-County
Subdivision-Place/Remainder-Census Tract-Block Group-Block." The reason summary
levels like these exist is the place hierarchy is very complicated in the U.S.
All places belong to a single state, for example, but places can and do cross
county lines. This makes answering the questions "What county is this place
in" or "What X is in Y" more complicated.

When geodata only supported places in California, it relied on the rather
uncommon summary level `155` (State-Place-County) to represent the places.
State-Place-Counties include county identifiers but split cities that cross
county lines into parts fully contained within counties. Using this summary
level seemed feasable because only a few places in California cross county lines
(cities [never do](https://www.latimes.com/archives/la-xpm-1985-11-06-me-4679-story.html)).
Once national data became supported, however, I was forced to switch to summary
level `160` (State-Places) because many cities in the U.S. cross county lines
– Dallas, Texas, for examples, has parts of five counties within its city limits
and therefore maps to five different State-Place-Counties.

Mapping places to their counties remains a goal for this project.

### Summary files

A summary file is the collection data of data released by the census for a
certain year. There used to be only decennial census that occured once every
ten years, but there are now American Community Surveys that take place every
year. All summary files have data files and geography files.

For American Community Surveys, data files are organized into estimate files and
margin of error files. If you moved all 2018 ACS to your data directory, the
files that start with `e` are estimate files; the files that start with `m` are
margin of error files (currently, geodata doesn't scan margin of error files).

Data files don't have geographic information in them; there is no column in the
data files for the name of the geography. Data files only have `LOGRECNO`
(logical record number) columns that points to a particular row in the
geography files.

Geography files do have columns for the names of the geography, and a `LOGRECNO`
that makes it possible to join geography files to data files.

Unfortunately, the Census Bureau has so much data that it cannot include it all
in single data files. For this reason, it is forced to break up data files once
by state, then again by what it calls a sequence number. This also requires a
seperate file to map the tables and their line numbers to sequence numbers.

#### More about data file organization

geodata currently scans over 200 data files when constructing its database.
(That database is then used to create the data products, then it is discarded.)
To obtain certain data, we need to know the `table_id`, then the line number
of the table. `table_id` and line number combinations (which geodata calls
`data_identifers`) are specified in `database.Database`. From there, geodata
uses `ACS_5yr_Seq_Table_Number_Lookup.csv` to determine the sequence number and
and positions (the index of the column inside the data file for that sequence).
Each sequence maps to one data file. Each table is wholly contained inside
one sequence and data file. geodata uses all this information to determine
where to obtain data for a certain `data_identifier`. More documentation
regarding the technical aspects of geodata will be written in the future.

## Next steps for development

* Map places to counties.
* Have `context`s support counties in addition to states.
* Support other types of geographies other than places (state, counties, etc.).
* Write more technical documentation.
