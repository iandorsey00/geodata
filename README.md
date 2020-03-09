# geodata
A program for getting information about and comparing geographies

This project currently supports places in California.

## Grouping places within California by counties

States can be quite large, and sometimes it is difficult to group places inside
of them. California is divided up into 58 counties. Cities are not allowed to
cross state lines, but CDPs (unincorporated areas) can and do cross state lines.

Fortunately for California, situations in which place-level geographies cross
state lines are rare enough that `PlaceCounties` are used by default for that
state. This means that we can readily find out which county a place is in,
making it very easy to group geographies that are in close proximity to one
another.
