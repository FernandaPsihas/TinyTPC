import h5py
import math
# import cmocean
import matplotlib as mpl
import matplotlib.ticker as ticker
from h5py import File
from matplotlib import pyplot as plt
import numpy as np
# import os
# import cmocean as cmo
from datetime import datetime
import plotly
import plotly.graph_objs as go

# f = h5py.File('self_trigger_tpc12_run2-binary-2022_12_01_02_45_CET.h5')
# print(f.keys())

#length =
#width =
#dictionary

# chp_coord = {12:(-1, 1), 22:(0,1), 32:(1,1),
#              13:(0,-1), 23:(0,0), 33:(0,1),
#              14:(-1,-1), 24:(0,-1), 34:(1,-1)
#             }

# We initially set the coordinates of the chips in terms of their positions on
# the pixel board. We consider the position of the chip in the center as (0,0).
# We then set the rest of the chips' coordinates with respect to the chip in
# the center of the pixel board.
# The chip ids are the keys in our dictionary and their respective x & y coordinates
# are the values. We use a list to store the x and y coordinate information of the
# chips.

#call it chp_yz
chp_coord = {12:[-1, 1], 22:[0,1], 32:[1,1],
             13:[-1,0], 23:[0,0], 33:[1,0],
             14:[-1,-1], 24:[0,-1], 34:[1,-1]
            }
# print(chp_coord[12][0])
#
# chnl_coord = {3:[0,0], 2:[0,1], 1:[0,2], 63:[0,3], 62:[0,4], 61:[0,5], 60:[0,6],
#               10:[1,0], 5:[1,1], 4:[1,2], 0:[1,3], 59:[1,4], 58:[1,5], 52:[1,6],
#               13:[2,0], 12:[2,1], 11:[2,2], 49:[2,3], 50:[2,4], 51:[2,5], 53:[2,6],
#               17:[3,0], 16:[3,1], 15:[3,2], 14:[3,3], 46:[3,4], 47:[3,5], 48:[3,6],
#               20:[4,0], 21:[4,1], 18:[4,2], 42:[4,3], 43:[4,4], 44:[4,5], 45:[4,6],
#               19:[5,0], 26:[5,1], 27:[5,2], 32:[5,3], 36:[5,4], 37:[5,5], 41:[5,6],
#               28:[6,0], 29:[6,1], 30:[6,2], 31:[6,3], 33:[6,4], 34:[6,5], 35:[6,6]
#             }


# We then set the coordinates of the channels in terms of their positions within
# each chip. The order of the channel ids are identical across all the chips of the pixel board.
# We consider the position of the channel in the center of the center most chip as (0,0).
# We then set the rest of the channels' coordinates with respect to the center most channel.
# The channel ids are the keys in our dictionary and their respective x & y coordinates
# are the values. We use a list to store the x and y coordinate information of the
# channels.

# name it chnl_yz
chnl_coord = {3:[-3,3], 2:[-3,3], 1:[-3,3], 63:[0,3], 62:[1,3], 61:[2,3], 60:[3,3],
              10:[-3, 2], 5:[-3, 2], 4:[-3, 2], 0:[0, 2], 59:[1, 2], 58:[2, 2], 52:[3, 2],
              13:[-3, 1], 12:[-2, 1], 11:[-1, 1], 49:[0, 1], 50:[1, 1], 51:[2, 1], 53:[3, 1],
              17: [-3, 0], 16: [-2, 0], 15: [-1, 0], 14: [0, 0], 46: [1, 0], 47: [2, 0], 48: [3, 0],
              20: [-3, -1], 21: [-2, -1], 18: [-1, -1], 42: [0, -1], 43: [1, -1], 44: [2, -1], 45: [3, -1],
              19: [-3, -2], 26: [-2, -2], 27: [-1, -2], 32: [0, -2], 36: [1, -2], 37: [2, -2], 41: [3, -2],
              28: [-3, -3], 29: [-2, -2], 30: [-1, -1], 31: [0, 0], 33: [1, 1], 34: [2, 2], 35: [3, 3]
            }


# def chk_chnl_coord(id, pos):
#     if id != chnl_coord[id] or pos != chnl_coord[id][pos]:
#         print("Please provide new id and/or position information.")

# print(chnl_coord[2][2])

# Checking if the chip id and the position provided exists in the chip dictionary.
# -20 is currently not physical
def chk_chp_coord(id, pos):
    if id not in chp_coord:
        print("Please provide correct chip id information. This chip id does not exist")
        return -20
    elif pos not in chp_coord[id]:
        print("Please provide correct position information.")
        return -20
    return
    # else:
    #     print(chp_coord[id][pos])


chk_chp_coord(11,2)

# Checking if the channel id and the position provided exists in the channel dictionary.
def chk_chnl_coord(id, pos):
    if id not in chnl_coord:
        print("Please provide correct channel id information. This channel id does not exist")
    elif pos not in chnl_coord[id]:
        print("Please provide correct position information.")
    return
    # else:
    #     print(chnl_coord[id][pos])


# chk_chnl_coord(9,3)
# chk_chp_coord(12, 3)

# print(r1_chnl[2])


# Find the actual coordinates of the channels of each chips on the pixel board.
# name it pixel_yz
def spatial(width, length, chp_id, chnl_id):
    # print(chp_coord[chp_id])
    # print(chnl_coord[chnl_id])
    x = 0
    y = 0

    if chp_id not in chp_coord:
        print("Please provide correct chip id information. This chip id does not exist")
        x = -20
    # elif pos not in chp_coord[id]:
    #     print("Please provide correct position information.")
        y = -20
    if chnl_id not in chnl_coord:
        print("Please provide correct channel id information. This channel id does not exist")
        x = -20
    # elif pos not in chnl_coord[id]:
    #     print("Please provide correct position information.")
        y = -20
    # chk_chp_coord(chp_id, chp_coord[chp_id][0])
    # chk_chp_coord(chp_id, chp_coord[chp_id][1])
    # chk_chnl_coord(chnl_id, chnl_coord[chnl_id][0])
    # chk_chnl_coord(chnl_id, chnl_coord[chnl_id][1])
    # chk_chnl_coord(chnl_id, 0)
    # chk_chnl_coord(chnl_id, 1)
    # chk_chp_coord(chp_id, 0)
    # chk_chp_coord(chp_id, 1)
    if x > -20 or y > -20:
        # print(x, y)
        x = width*chp_coord[chp_id][0] + chnl_coord[chnl_id][0]
        y = length*chp_coord[chp_id][1] + chnl_coord[chnl_id][1]
    return x, y

a, b = spatial(7, 7, 12, 62)
print(a,b)
# print(spatial(7, 7, 11, 62))
# print(spatial(1,1,23,15))


# print(chnl_coord[2][2])
#All the channels in a chip
# chp ={"r1": r1_chnl, "r2" : r2_chnl, "r3":r3_chnl, "r4" : r4_chnl, "r5" : r5_chnl, "r6" :r6_chnl , "r7" :r7_chnl }
# print(chp["r1"])
# chp ={"r1": r1_chnl, "r2": r2_chnl, "r3": r3_chnl, "r4": r4_chnl, "r5": r5_chnl, "r6": r6_chnl, "r7": r7_chnl}
# print(chp["r1"])
# print(chp["r1"][2])
# print(chp["r1"])
# print(chp["r2"])
# print(chp["r3"])
# print(chp["r4"])
# print(chp["r5"])
# print(chp["r6"])
# print(chp["r7"])

#The pixel board

# pix = {12:chp, 22:chp}
#
# print(pix)


# spatial(3, 3,  )
#possibly import the function
