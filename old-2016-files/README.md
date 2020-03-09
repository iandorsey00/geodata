# My old project from 2016

## `Place`
`Place` is a class that organizes organizes information regarding places in California into `namedtuple`
objects. The fields for the `Place` objects are as follows:

* `id` – Specifies a numeric ID for a geography.
* `key` – A unique string with no spaces that identifies a geography. The idea for `key` is to be able to
join data from sources other than the Census Bureau together using the name of the geography and as input
for a hashing function. For example, the `key` for what the Census specifies as Adelanto city, California is just `adelanto`.
* `county` – The county that the place is inside. (Source: U.S. Census Bureau.)
* `pop` – The geography's total population. (Source: U.S. Census Bureau.)
* `race_nhol_total` – The geography's total non-Hispanic or Latino population. (Source: U.S. Census Bureau.)
* `inc_pci` – The per capita income of the geography. (Source: U.S. Census Bureau.)
* `edu_ba_om` – The number of people in the geography with a Bachelor's degree or higher. (Source: U.S. Census Bureau.)
* `edu_gd_om` – The number of people in the geography with a graduate degree. (Source: U.S. Census Bureau.)
* `ucr_vcr` – The geography's violent crime rate. (Source: FBI Uniform Crime Reports.)
* `ucr_pcr` – The geography's property crime rate. (Source: FBI Uniform Crime Reports.)
* `vr_dem` – Percentage of a geography's registered voters who are registered as Democrats. (Source: California
Secretary of State.)
* `vr_rep` – Percentage of a geography's registered voters who are registered as Republicans. (Source: California
Secretary of State.)

Information for more fields will be added in the future.

## `PlaceVectors`

`PlaceVectors` use normalized data to model places as multi-dimensional vectors. The purpose is to be able to find similar
places by calculating the Euclidean distance between it and other `PlaceVector`s. It is a use of the [k-nearest neighbors
algorithm](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm). `PlaceVector`, `PlaceVectorFull` and `PlaceVectorApp`
differ in the amount of and what type of fields (represented as coordinates) are used to model the vectors.

### `PlaceVector`

The standard `PlaceVector` has nine dimensions. Its fields are `pop`, `pop_density`, `race_white`, `race_hispanic`,
`race_asian`, `race_black`, `inc_pci`, `edu_ba_om`, and `edu_gd_om`.

### `PlaceVectorFull`

This is a `PlaceVector` with more dimensions, namely 14 in total. They are `pop`, `pop_density`, `race_white`,
`race_hispanic`, `race_asian`, `race_black`, `inc_pci`, `edu_ba_om`, `edu_gd_om`, `ucr_vcr`, `ucr_pcr`, `vr_dem`, `vr_rep`,
and `vr_other`.

### `PlaceVectorApp`

A smaller `PlaceVector`; its primary goal is to model the *appearance* of a city, and so it contains mostly fields that
affect a geography's appearance. It is a three-dimensional vector, and theorectically can be modeled in 3D space. The fields
are `pop_density`, `inc_pci`, and `hs_mysb`.
			