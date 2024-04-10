import webbrowser
import pycountry
import reverse_geocoder as rg
from flask import current_app


# See https://study.com/skill/learn/how-to-convert-degrees-minutes-seconds-to-decimal-degrees-explanation.html
MINUTE_FRACTION_OF_A_DEGREE = 60
SECOND_FRACTION_OF_A_DEGREE = 3600

# See https://en.wikipedia.org/wiki/Geographic_coordinate_system
SOUTH_OF_EQUATOR = "S"
WEST_OF_GREENWICH_MERIDIAN = "W"


def dms_coordinates_to_dd_coordinates(coordinates, coordinates_ref) -> float:
    """ Convert coordinates from Degrees Minutes Seconds (DMS) to Decimal Degrees (DD)
    (Most geolocation tools use DD) """
    decimal_degrees = (coordinates[0] + 
                       coordinates[1] / MINUTE_FRACTION_OF_A_DEGREE + 
                       coordinates[2] / SECOND_FRACTION_OF_A_DEGREE)
    if coordinates_ref == SOUTH_OF_EQUATOR or coordinates_ref == WEST_OF_GREENWICH_MERIDIAN:
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
    current_app.logger.debug(f"Image : {status}")
    return ret


def format_camera_model(image) -> str:
    """ Capitalize camera model for cleaner output """
    return image.model.capitalize()


def filter_out_tags(image) -> list:
    """ Remove tags with bytes values (like _interoperability_ifd_Pointer) """
    ignore_prefixes = ['_', 'get', 'delete', 'list_all']
    return [tag for tag in dir(image) if not any(tag.startswith(prefix) for prefix in ignore_prefixes)]


def get_location(coordinates) -> str:
    location_info = rg.search(coordinates, verbose=False)[0]
    location_info['country'] = pycountry.countries.get(alpha_2=location_info['cc'])
    loc = f"{location_info['name']}, {location_info['country'].name}"
    return loc


def get_coordinates_tags(image):
    gps_latitude = image.get("gps_latitude")
    gps_latitude_ref = image.get("gps_latitude_ref")
    gps_longitude = image.get("gps_longitude")
    gps_longitude_ref = image.get("gps_longitude_ref")
    return gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref


def convert_coordinates_in_decimal_degrees(gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref):
    decimal_latitude = dms_coordinates_to_dd_coordinates(gps_latitude, gps_latitude_ref)
    decimal_longitude = dms_coordinates_to_dd_coordinates(gps_longitude, gps_longitude_ref)
    coordinates = (decimal_latitude, decimal_longitude)
    current_app.logger.debug(f"Latitude, Longitude (DD): {coordinates}")
    return coordinates, decimal_latitude, decimal_longitude


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
