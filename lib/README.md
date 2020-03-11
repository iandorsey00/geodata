# `/lib`

## Geography keys and the ID problem

As stated in the README for the top-level directory, places can have different
representations in different sources, for example "Adelanto, California" and
"Adelanto, CA." This makes joining data from multiple sources difficult.

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

## `main.py`

Currently, this inserts `PlaceCounties` in California into the SQLite3 database
and runs a query on the database to display the information.