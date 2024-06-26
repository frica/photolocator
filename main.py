import datetime
from logging.config import dictConfig
import json
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

    gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref = utils.get_coordinates_tags(image)

    if not (gps_latitude or gps_latitude_ref or gps_longitude or gps_longitude_ref):
        flash('No geolocation data found', 'error')
        app.logger.warning("No geolocation data found")
        return redirect("/")

    coordinates_in_dd, decimal_latitude, decimal_longitude = (
        utils.convert_coordinates_in_decimal_degrees(gps_latitude,
                                                     gps_latitude_ref,
                                                     gps_longitude,
                                                     gps_longitude_ref))
    location = utils.get_location(coordinates_in_dd)
    app.logger.info(f"Location: {location}")
    return render_template("locate.html", answer=location,
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
    camera_model = utils.format_camera_model(image.model)
    return render_template("details.html", array=image_members, model=camera_model, image=image)


if __name__ == '__main__':
    app.run(debug=True)
