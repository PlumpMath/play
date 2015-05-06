# configuration for color space

# red, green, blue. can vary 2 or 3
# list where first index is what varies with x,
# second index varies with y,
# if there is a third index, it varies with both x and y
colors = ['b', 'g']
# I suppose could eventually want to make this different for all
# colors that are varying.
variance = [0.2, 0.7]
# if there is a color that does not vary,
# this is its value
static = 0.1

resolution = [1024, 768]