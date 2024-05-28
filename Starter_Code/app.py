# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    "Convert the query results to a dictionary by using date as the key and prcp as the value."
    results = session.query(Measurement.date, Measurement.prcp).all()
    precipitation_dict = {}
    for date, prcp in results:
        precipitation_dict[date] = prcp
    return jsonify(precipitation_dict)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Measurement.station).distinct().all()
    stations = [row[0] for row in results] 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    "Query temperature observations of the most-active station for the previous year of data."
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    prev_year_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').all()

    tobs_data = []
    for date, tobs in prev_year_data:
        tobs_data.append({"date": date, "tobs": tobs})

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    temp_stats = session.query(func.min(Measurement.tobs),
                               func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    (min_temp, avg_temp, max_temp) = temp_stats[0]

    temp_dict = {"Minimum Temperature": min_temp,
                 "Average Temperature": avg_temp,
                 "Maximum Temperature": max_temp}

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    temp_stats = session.query(func.min(Measurement.tobs),
                               func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    (min_temp, avg_temp, max_temp) = temp_stats[0]

    temp_dict = {"Minimum Temperature": min_temp,
                 "Average Temperature": avg_temp,
                 "Maximum Temperature": max_temp}

    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True)