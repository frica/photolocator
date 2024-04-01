import logging
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


# Not used anymore, I keep it for cli app
def draw_map_for_location(latitude, latitude_ref, longitude, longitude_ref):
    url = f"https://www.google.com/maps?q={latitude}{latitude_ref} {longitude}{longitude_ref}"
    # print(f"url is {url}")
    webbrowser.open_new_tab(url)


def check_if_exif(image):
    """ Check if image has exif tags """
    ret = True
    if image.has_exif:
        status = f"contains EXIF (version {image.get('exif_version')}) information."
    else:
        status = "does not contain any EXIF information."
        ret = False
    logging.debug(f"Image : {status}")
    return ret


# Not used anymore, I keep it for cli app
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
