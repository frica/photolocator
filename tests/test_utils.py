import unittest
from exif import Image
import utils
from main import app


class TestUtilsMethods(unittest.TestCase):

    def test_format_camera_model(self):
        camera_model = utils.format_camera_model("motorola Edge 20")
        self.assertTrue(camera_model[0].isupper(), "The first letter is not capitalized!")

    def test_format_camera_model_if_leading_whitespace(self):
        camera_model = utils.format_camera_model(" motorola Edge 20")
        self.assertTrue(camera_model[0].isupper())

    def test_dms_coordinates_to_dd_coordinates_random_value(self):
        coordinates = (72, 24, 36)
        ref = "N"
        coordinates_dd = utils.dms_coordinates_to_dd_coordinates(coordinates, ref)
        self.assertEqual(str(round(coordinates_dd, 2)), "72.41")

    def test_convert_coordinates_latitude_Auckland(self):
        coordinates = (36, 50, 54)
        ref = "S"
        coordinates_dd = utils.dms_coordinates_to_dd_coordinates(coordinates, ref)
        self.assertEqual(str(round(coordinates_dd, 2)), "-36.85")

    def test_convert_coordinates_longitude_Auckland(self):
        coordinates = (174, 45, 48)
        ref = "E"
        coordinates_dd = utils.dms_coordinates_to_dd_coordinates(coordinates, ref)
        self.assertEqual(str(round(coordinates_dd, 2)), "174.76")

    def test_image_has_exif(self):
        image = Image('exif.jpg')
        with app.app_context(): # otherwise pb with logger, see https://flask.palletsprojects.com/en/3.0.x/testing/
            self.assertTrue(utils.check_if_exif(image))
            
    def test_image_has_no_exif(self):
        image = Image('noexif.jpg')
        with app.app_context():
            self.assertFalse(utils.check_if_exif(image))


if __name__ == '__main__':
    unittest.main()
