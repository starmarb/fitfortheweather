import sys
import sqlite3
from sqlite3 import connect
from contextlib import closing

def getseason(temperature):
    """associate each season with a temperature range"""
    if temperature <= 0:
        season = 'winter'
    elif temperature <= 15 and temperature > 0:
        season = 'fall'
    elif temperature <= 25 and temperature > 15:
        season = 'spring'
    elif temperature > 25:
        season = 'summer'
    return(season)

_DATABASE_URL = 'file:database.db?mode=ro'

def season_query(season, user_id):
    """Output clothing description & type if season matches the day's 'season' with special handling for outerwear and tops."""
    with connect(_DATABASE_URL, uri=True) as connection:
        with closing(connection.cursor()) as cursor:
            query_data = None
            additional_season = None

            if season == 'winter':
                query_data = "SELECT img, type FROM clothes WHERE winter = 1 AND user_id = ?"
                additional_season = 'fall'
            elif season == 'spring':
                query_data = "SELECT img, type FROM clothes WHERE spring = 1 AND user_id = ?"
                additional_season = 'winter'
            elif season == 'summer':
                query_data = "SELECT img, type FROM clothes WHERE summer = 1 AND user_id = ?"
            else:  # fall
                query_data = "SELECT img, type FROM clothes WHERE fall = 1 AND user_id = ?"
                additional_season = 'spring'

            clothing_dict = {}
            if query_data:
                cursor.execute(query_data, (user_id,))
                results = cursor.fetchall()
                for img, clothing_type in results:
                    clothing_dict[img] = clothing_type

                # Query for additional season outerwear
                if additional_season and season != 'summer':
                    additional_query = "SELECT img, type FROM clothes WHERE {0} = 1 AND user_id = ? AND type = 'outerwear'".format(additional_season)
                    cursor.execute(additional_query, (user_id,))
                    additional_results = cursor.fetchall()
                    for additional_img, _ in additional_results:
                        clothing_dict[additional_img] = 'outerwear'

            return clothing_dict

# def season_query(season, user_id):
#     """output clothing description & type if season matches the day's "season"""
#     with connect(_DATABASE_URL, uri=True) as connection:
#         with closing(connection.cursor()) as cursor:
#             query_data = None
#             if season == 'winter':
#                 query_data = "SELECT img, type FROM clothes WHERE winter = 1 AND user_id = ? ORDER BY type"
#             elif season == 'spring':
#                 query_data = "SELECT img, type FROM clothes WHERE spring = 1 AND user_id = ? ORDER BY type"
#             elif season == 'summer':
#                 query_data = "SELECT img, type FROM clothes WHERE summer = 1 AND user_id = ? ORDER BY type"
#             else:
#                 query_data = "SELECT img, type FROM clothes WHERE fall = 1 AND user_id = ? ORDER BY type"
#             if query_data:
#                 cursor.execute(query_data, (user_id,))
#                 results = cursor.fetchall()
#                 #Create a dictionary from the results
#                 # clothing_list = [(img, clothing_type) for img, clothing_type in results]
#                 clothing_dict = {img: type for img, type in results}
#                 return clothing_dict
#             else:
#                 return {}
            
            