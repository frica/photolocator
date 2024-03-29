import webbrowser

# See https://auth0.com/blog/read-edit-exif-metadata-in-photos-with-python/


def format_dms_coordinates(coordinates):
    return f"{coordinates[0]}°{coordinates[1]}\'{coordinates[2]}\""


def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref):
    decimal_degrees = coordinates[0] + \
                      coordinates[1] / 60 + \
                      coordinates[2] / 3600

    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees

    return decimal_degrees


def draw_map_for_location(latitude, latitude_ref, longitude, longitude_ref):

    url = f"https://www.google.com/maps?q={latitude}{latitude_ref} {longitude}{longitude_ref}"
    # print(f"url is {url}")
    webbrowser.open_new_tab(url)


def draw_map_for_city(city):

    url = f"https://www.google.com/maps?q={city}"
    # print(f"url is {url}")
    webbrowser.open_new_tab(url)


def check_if_exif(image):
    ret = True
    if image.has_exif:
        status = f"contains EXIF (version {image.get('exif_version')}) information."
    else:
        status = "does not contain any EXIF information."
        ret = False
    print(f"Image : {status}")
    return ret


# def check_if_exif():
#     ret = True
#     if image.has_exif:
#         status = f"contains EXIF (version {image.exif_version}) information."
#     else:
#         status = "does not contain any EXIF information."
#         ret = False
#     print(f"Image : {status}")
#     return ret


def display_details(image):
    image_members = [dir(image)]
    image_member_list = enumerate(image_members)
    nb_exif_tags = image_member_list.__sizeof__()
    print(f"Image contains {nb_exif_tags} members:")
    print(f"{image_members}\n")
    print("Device information")
    print("----------------------------")
    print(f"Make: {image.get('make')}")
    print(f"Model: {image.model}\n")
    print("Date/time taken")
    print("-------------------------")
    print(f"{image.datetime_original}.{image.subsec_time_original} {image.get('offset_time', '')}\n")
    return image_member_list


# if __name__ == '__main__':
#
#     photo_file = open("images/gent.jpg", "rb")
#     image = Image(photo_file)
#
#     if not check_if_exif():
#         exit()
#
#     display_details(image)
#
#     print(f"Coordinates - Image ")
#     print("---------------------")
#     # Latitude (Degrees, Minutes (1/60th of a degree)
#     #     Seconds (1/60th of a minute, or 1/3600th of a degree))
#     # _ref is the direction
#     print(f"Latitude (DMS): {format_dms_coordinates(image.gps_latitude)}{image.gps_latitude_ref}")
#     print(f"Longitude (DMS): {format_dms_coordinates(image.gps_longitude)}{image.gps_longitude_ref}\n")
#
#     # google maps works with decimal degrees
#     decimal_latitude = dms_coordinates_to_dd_coordinates(image.gps_latitude, image.gps_latitude_ref)
#     print(f"Latitude (DD): {decimal_latitude}")
#     decimal_longitude = dms_coordinates_to_dd_coordinates(image.gps_longitude, image.gps_longitude_ref)
#     print(f"Longitude (DD): {decimal_longitude}")
#     print(f"Location info")
#     print("-----------------------")
#     coordinates = (decimal_latitude, decimal_longitude)
#     location_info = rg.search(coordinates)[0]
#     location_info['country'] = pycountry.countries.get(alpha_2=location_info['cc'])
#     print(f"{location_info}\n")
#     print(f"Final answer")
#     print("-----------------------")
#     print(f"You were in {location_info['name']}, {location_info['country'].name}!")
#
#     draw_map_for_location(decimal_latitude, image.gps_latitude_ref,
#                           decimal_longitude, image.gps_longitude_ref)
#
#
#
