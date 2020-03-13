# geodata
A program for getting information about and comparing geographies

At this point in development, this project currently only supports places in
California.

## Dependencies

* `pandas`
* `sqlalchemy`

## Goals of the project

* Make it easier to access census data from the U.S. (and perhaps other
countries in the future).
* Provide an easy way to compare the demographic similarity of geographies with
`PlaceVector`s and `PlaceVectorApp`s (see below).

## Usage

If you checked out this repository, add `python` or `python3` before `geodata`
when running the program, i.e. `python3 geodata ...` while in the top level
directory of the source code.

    Basic usage:       geodata option
    Options:
    
      -h|--help                              Display this information.
      -c|--create-database                   Create a new database.
    
    PlaceVector usage: geodata -p|-a pv_query
    PlaceVector usage: geodata --placevectors=pv_query
    PlaceVector usage: geodata --placevectorapps=pv_query
    
    Options:
    
      -p pv_query|--placevectors=pv_query    Compare PlaceVectors.
      -a pv_query|--placevectorapps=pv_query Compare PlaceVectorApps.
    
    pv_query: PlaceVector queries
    
        "place[|county]"
    
    Compare the PlaceVector associated with place (required) with
    PlaceVectors in county (optional). If county is not specified,
    Compare the PlaceVector with all others in the state.
    
    In each case, the closest PlaceVectors will be printed.
    
    Example: geodata -p "Los Angeles city, California"
             Get the closest PlaceVectors to Los Angeles, CA.
    
    Example: geodata -a "San Diego city, California|Los Angeles County"
             Get the closest PlaceVectors to San Diego, CA in Los
             Angeles County, CA.

## Current project status

It's now possible to query `PlaceVectors` and `PlaceVectorApps` in California
and compare them with others.

## Next steps

* Support for the following will be added:
  * Looking up data profiles for a geography
* Searching through geographies (not requiring the place string to be
  entered exactly)
* Improve documentation

## Comparing demographic similarity: Types of PlaceVectors

`PlaceVector`s model all places in California as a multidimensional vector
with components differing by the type of `PlaceVector`. Currently there are two
types, which are listed below. Demographic characteristics of a place are
modeled by the vector's components.

To create a PlaceVector, raw data corresponding to its components are first
collected; this is referred to as raw subcomponent data. Using the median values
and standard deviation for such data (see below for the calculation method),
these are assigned scores with:

* 0 representing 0,
* 50 representing the median value, and
* 100 represeting a value two standard deviations above the median.

With these standarized scores, it's possible to calculate the Euclidean distance
between vectors by squaring the differences of each component, adding them
together, then taking the square of that sum.

Not all subcomponents must have the same weight. The effect that each
subcomponent has on the vector's value can be controlled by proportionally
reducing the amount of the subcomponent. This way, it will not affect the
position of the overall vector as much.

### `PlaceVector` score calculation method

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

### `PlaceVector`s (standard)

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

### `PlaceVectorApp`s

The aim of a `PlaceVectorApp` is to calculate how similar two areas appear.
`PlaceVectorApp`s are made up of the following
components:

* The population density component,
* The income component, and
* The median year structure built component. This is the year for which the
  median house was built in the place. For this component, 1939 is treated as
  0 because the U.S. Census Bureau doesn't record median year structure built
  values before 1939.

## Grouping places within California by counties

States can be quite large, and sometimes it is difficult to group places inside
of them. California is divided up into 58 counties. Cities are not allowed to
cross state lines, but CDPs (unincorporated areas) can and do cross state lines.

Fortunately for California, situations in which place-level geographies cross
state lines are rare enough that `PlaceCounties` are used by default for that
state. This means that we can readily find out which county a place is in,
making it very easy to group geographies that are in close proximity to one
another.

## Geography keys and the ID problem

Places can have different representations in different sources, for example
"Adelanto, California" and "Adelanto, CA." This makes joining data from multiple
sources difficult.

To make matters worse, places in some states can and often do cross county
lines. We want to be able to group geographies together inside a county,
but having places that cross county lines makes this complicated. There is no
way to query Census data to determine what county a regular place a county
is in.

### The Census and different summary levels

In order to solve this problem, (and other similar problems of places inside)
bigger geographies, there is not just one type of place as far as the Census
is concerned. The most common type of place is known as a State-Place. In this
app, we're also interested in what counties the places are inside of, so we
will be using State-Place-Counties whenever possible.

(The way the Census tells different types of geographies like states and
counties apart is by giving each record a *summary level code.* For example,
the summary level for the whole United States is `010` and the summary level
for states is `040`. The summary level for a State-Place (commonly just called a
*place* is `160`, and the summary level for a State-Place-County is `155`. See
[this page](https://factfinder.census.gov/help/en/summary_level_code_list.htm)
for a list of summary levels.)

### The ID problem

Unfortunately, State-Places and State-Place-Counties have different `GEO_ID`s,
which means we can have different IDs for essentially the same geography.

### This app's solution – A key hash

Representing a place with number has so many problems that this app will attempt
to get rid of that concept entirely. Instead, places will be represented by a
key hash, which will be the same for the strings "Any Town, ST", "AnyTown, ST",
"Any Town, State", and "Anytown, State."

## Key hashes

Key hashes in `geodata` must be unique and have the following format

    country_code:soad_code:name[/option1[/option2[/...]]]

All letters in the hash must be lowercase. For example

    us:ca:losangeles

### Mandatory items

`country_code` – A two digit code representing the name of the country the place
is in, e.g. `us` for the United States.
`soad_code` – The code for the second order administrative division, usually the
state or province, e.g. `ca` for California.
`name` – The name of the place without spaces or other characters that may or
may not appear, like dashes.

### Options

Unfortunately, after removing spaces and other characters from `name`,
duplicates can still appear. In order for duplicates to be eliminated, we might
need to append an option to the hash string, such as `/cdp` for unincorporated
areas in California. (`cdp` stands for census designated place.) Options should
be used as little as possible and only as necessary to avoid duplicate hashes
within second-order administrative divisions.

## key_hash.py

Contains the current function used to convert name strings to a hash. See above
for more information.

## `Place`

The model used to represent places. Because this lacks county information,
`PlaceCounties` should be used instead whenever possible.
