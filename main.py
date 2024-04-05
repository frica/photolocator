import datetime
from logging.config import dictConfig
import json
import pycountry
import reverse_geocoder as rg
from exif import Image
from flask import Flask, render_template, request, redirect, flash, jsonify
import config
import utils

# Settings to get similar output as Flask werkzeug logs
# See https://flask.palletsprojects.com/en/3.0.x/logging/
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

# TODO save the secret key somewhere else 
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/version", methods=["GET"], strict_slashes=False)
def version():
    """ returns the server version stored in config.py for easier debugging """
    response_body = {
        "success": 1,
    }
    return jsonify(response_body)


@app.after_request
def after_request(response):
    """ adds time and server version to every request call """
    if response and response.get_json():
        data = response.get_json()

        # isoformat to be able to serialize with json
        data["time_request"] = datetime.datetime.now(datetime.UTC).isoformat()
        data["version"] = config.VERSION

        response.set_data(json.dumps(data))

    return response


@app.route("/locate", methods=["POST"])
def locate():
    file = request.files["image"]
    image = Image(file.stream.read())

    if not utils.check_if_exif(image):
        flash('No EXIF data found', 'error')
        app.logger.warning("No EXIF data found")
        return redirect("/")

    gps_latitude = image.get("gps_latitude")
    gps_latitude_ref = image.get("gps_latitude_ref")
    gps_longitude = image.get("gps_longitude")
    gps_longitude_ref = image.get("gps_longitude_ref")

    if not (gps_latitude or gps_latitude_ref or gps_longitude or gps_longitude_ref):
        flash('No geolocation data found', 'error')
        app.logger.warning("No geolocation data found")
        return redirect("/")

    decimal_latitude = utils.dms_coordinates_to_dd_coordinates(gps_latitude, gps_latitude_ref)
    app.logger.debug(f"Latitude (DD): {decimal_latitude}")
    decimal_longitude = utils.dms_coordinates_to_dd_coordinates(gps_longitude, gps_longitude_ref)
    app.logger.debug(f"Longitude (DD): {decimal_longitude}")
    coordinates = (decimal_latitude, decimal_longitude)
    location_info = rg.search(coordinates, verbose=False)[0]
    location_info['country'] = pycountry.countries.get(alpha_2=location_info['cc'])
    answer = f"{location_info['name']}, {location_info['country'].name}"
    app.logger.info(f"You were in {answer}!")
    return render_template("locate.html", answer=answer,
                           lat=decimal_latitude, lon=decimal_longitude)


@app.route("/details", methods=["POST"])
def details():
    file = request.files["image"]
    image = Image(file.stream.read())

    if not utils.check_if_exif(image):
        flash('No EXIF data found', 'error')
        app.logger.warning("No EXIF data found")
        return redirect("/")

    image_members = utils.filter_out_tags(image)
    camera_model = utils.format_camera_model(image)
    return render_template("details.html", array=image_members, model=camera_model, image=image)


if __name__ == '__main__':
    app.run(debug=True)
