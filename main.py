import os
from flask import Flask, render_template, request, redirect, url_for, flash
from exif import Image
import reverse_geocoder as rg
import pycountry
import utils

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/about", methods=["POST"])
def about():
    if request.method == "POST":
        file = request.files["image"]
        image = Image(file.stream.read())

        if not utils.check_if_exif(image):
            flash('No Exif data found', 'error')
            return redirect("/")

        return render_template("about.html", "")
    return redirect("/")


@app.route("/locate", methods=["POST"])
def locate():
    if request.method == "POST":

        file = request.files["image"]
        image = Image(file.stream.read())

        if not utils.check_if_exif(image):
            flash('No Exif data found', 'error')
            return redirect("/")

        if request.form["action"] == "locate":

            # print(f"Latitude (DMS): {format_dms_coordinates(image.gps_latitude)}{image.gps_latitude_ref}")
            # print(f"Longitude (DMS): {format_dms_coordinates(image.gps_longitude)}{image.gps_longitude_ref}\n")
            # google maps works with decimal degrees
            gps_latitude = image.get("gps_latitude")
            gps_latitude_ref = image.get("gps_latitude_ref")
            gps_longitude = image.get("gps_longitude")
            gps_longitude_ref = image.get("gps_longitude_ref")
            if not (gps_latitude or gps_latitude_ref or gps_longitude or gps_longitude_ref):
                flash('No geolocalisation data found', 'error')
                return redirect("/")

            decimal_latitude = utils.dms_coordinates_to_dd_coordinates(gps_latitude, gps_latitude_ref)
            print(f"Latitude (DD): {decimal_latitude}")
            decimal_longitude = utils.dms_coordinates_to_dd_coordinates(gps_longitude, gps_longitude_ref)
            print(f"Longitude (DD): {decimal_longitude}")
            # print(f"Location info")
            coordinates = (decimal_latitude, decimal_longitude)
            location_info = rg.search(coordinates)[0]
            location_info['country'] = pycountry.countries.get(alpha_2=location_info['cc'])
            print(f"{location_info}\n")
            # print(f"Final answer")
            print(f"You were in {location_info['name']}, {location_info['country'].name}!")
            answer = f"{location_info['name']}, {location_info['country'].name}"
            app.logger.info(f"Location: {answer}")
            return render_template("locate.html", answer=answer)
        elif request.form["action"] == "about":
            image_member_list = utils.display_details(image)
            return render_template("about.html", answer=image_member_list, model=image.model)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
