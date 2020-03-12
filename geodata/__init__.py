from Database import Database
import sys

print(sys.argv)

# d = Database()

# print()
# search_name = input("Enter the name of a place that you want to compare with others: ")
# filter_county = input("Would you like to filter by a county? If not, just press Enter: ")
# print()

# # Obtain the PlaceVector for which we entered a name.
# comparison_pv = \
#     list(filter(lambda x: x.name == search_name, d.placevectors))[0]

# print("The most demographically similar places are:")
# print()

# # Filter by county if a filter_county was specified.
# if filter_county != '':
#     filtered_pvs = list(filter(lambda x: x.county == filter_county,
#                         d.placevectors))

# # Get the closest PlaceVectors.
# # In other words, get the most demographically similar places.
# closest_pvs = sorted(filtered_pvs,
#     key=lambda x: comparison_pv.distance(x))[1:10]

# # Print these PlaceVectors
# for closest_pv in closest_pvs:
#     print(closest_pv)
