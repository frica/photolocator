import pycountry
import reverse_geocoder as rg
from exif import Image
from flask import Flask, render_template, request, redirect, flash

import utils

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def hello():
    return render_template("index.html")


@app.route("/details", methods=["POST"])
def details():
    if request.method == "POST":
        file = request.files["image"]
        image = Image(file.stream.read())

        if not utils.check_if_exif(image):
            flash('No Exif data found', 'error')
            return redirect("/")

        return render_template("details.html")
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
            # google maps works with decimal degrees, not dms
            gps_latitude = image.get("gps_latitude")
            gps_latitude_ref = image.get("gps_latitude_ref")
            gps_longitude = image.get("gps_longitude")
            gps_longitude_ref = image.get("gps_longitude_ref")
            if not (gps_latitude or gps_latitude_ref or gps_longitude or gps_longitude_ref):
                flash('No geolocation data found', 'error')
                return redirect("/")

            decimal_latitude = utils.dms_coordinates_to_dd_coordinates(gps_latitude, gps_latitude_ref)
            print(f"Latitude (DD): {decimal_latitude}")
            decimal_longitude = utils.dms_coordinates_to_dd_coordinates(gps_longitude, gps_longitude_ref)
            print(f"Longitude (DD): {decimal_longitude}")
            coordinates = (decimal_latitude, decimal_longitude)
            location_info = rg.search(coordinates)[0]
            location_info['country'] = pycountry.countries.get(alpha_2=location_info['cc'])
            print(f"{location_info}\n")
            print(f"You were in {location_info['name']}, {location_info['country'].name}!")
            answer = f"{location_info['name']}, {location_info['country'].name}"
            app.logger.info(f"Location: {answer}")
            return render_template("locate.html", answer=answer,
                                   lat=decimal_latitude, lon=decimal_longitude)
        elif request.form["action"] == "details":
            image_members = dir(image)

            # remove from the list tags with bytes values like _interoperability_ifd_Pointer
            image_members[:] = (tags for tags in image_members if
                                (not tags.startswith("_")) and
                                (not tags.startswith("get")) and
                                (not tags.startswith("delete")) and
                                (not tags.startswith("list_all")))
            print(image_members)

            # just to get a cleaner output if not capitalized
            model = image.model.capitalize()

            return render_template("details.html", array=image_members, model=model, image=image)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
