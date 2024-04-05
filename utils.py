import logging
import webbrowser


def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref) -> float:
    """ Convert coordinates from Degrees Minutes Seconds (DMS) to Decimal Degrees (DD)
    (Most geolocation tools use DD) """
    decimal_degrees = coordinates[0] + coordinates[1] / 60 + coordinates[2] / 3600
    if coordinates_ref == "S" or coordinates_ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def check_if_exif(image) -> bool:
    """ Check if image has exif tags and log it """
    ret = True
    if image.has_exif:
        status = f"contains EXIF (version {image.get('exif_version')}) information."
    else:
        status = "does not contain any EXIF information."
        ret = False
    logging.debug(f"Image : {status}")
    return ret


def format_camera_model(image) -> str:
    """ Capitalize camera model for cleaner output """
    return image.model.capitalize()


def filter_out_tags(image) -> list:
    """ Remove tags with bytes values (like _interoperability_ifd_Pointer) """
    ignore_prefixes = ['_', 'get', 'delete', 'list_all']
    return [tag for tag in dir(image) if not any(tag.startswith(prefix) for prefix in ignore_prefixes)]


# Below are methods I used in the beginning for a CLI version of the app


def format_dms_coordinates(coordinates) -> str:
    """ Format the DSM coordinates with the proper symbols """
    return f"{coordinates[0]}°{coordinates[1]}\'{coordinates[2]}\""


def draw_map_for_location(latitude, latitude_ref, longitude, longitude_ref) -> None:
    """ Open a browser window showing location with Google Maps """
    url = f"https://www.google.com/maps?q={latitude}{latitude_ref} {longitude}{longitude_ref}"
    webbrowser.open_new_tab(url)


def display_basic_picture_information(image):
    """ Output basic exif information """
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
