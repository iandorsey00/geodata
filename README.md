# geodata
A program for getting information about and comparing geographies

This project currently supports places in California.

## Current project status

Upon executing

    python3 __init__.py

in the `geodata` directory, we're able to query the SQLite database for all
places in California. Find demographically similar places in California by
entering the exact Census name for the city at the prompt, e.g. San Francisco
city, California.

## Next steps

* Prompt improvements are needed.
* Support for the following will be added:
  * Looking up data profiles for a geography
  * Appearance place vectors (`PlaceVectorApp`s)

## Grouping places within California by counties

States can be quite large, and sometimes it is difficult to group places inside
of them. California is divided up into 58 counties. Cities are not allowed to
cross state lines, but CDPs (unincorporated areas) can and do cross state lines.

Fortunately for California, situations in which place-level geographies cross
state lines are rare enough that `PlaceCounties` are used by default for that
state. This means that we can readily find out which county a place is in,
making it very easy to group geographies that are in close proximity to one
another.
