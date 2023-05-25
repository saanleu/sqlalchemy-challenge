# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def percipitation():
    """Query results from precipitation analysis last 12 months of data only"""
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_before = dt.date(2017,8,23) - dt.timedelta(days=365)
    #load query results into panda df, set col names
    #sort df values by date, plot results by df plot method
    the_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_before, Measurement.prcp != None).all()

    return jsonify(dict(the_data))

@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(Station.station, Station.name).all()
    #Return a JSON list of stations from the dataset.
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most-active station 
    #for the previous year of data.
    year_before = dt.date(2017,8,23) - dt.timedelta(days=365)
    temp_list = session.query(Measurement.tobs).filter(Measurement.date >= year_before, Measurement.station).all()
    tobs_list = []
    for temp in temp_list:
        tlist = {}
        tlist["tobs"] = temp.tobs
        tobs_list.append(tlist)
    #Return a JSON list of temperature observations for the previous year.
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start")
def start(start_point):
    start_date = dt.datetime.strptime(start_point, '%Y-%m-%d')
    year_before = dt.timedelta(days=365)

    #For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater 
    # than or equal to the start date.
    start_point = start_date-year_before
    end_point = dt.date(2017,8,23)
    yearound_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= start_point).all()
    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
    # for a specified start or start-end range.
    return jsonify(yearound_data)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    #For a specified start date and end date, calculate TMIN, TAVG, and TMAX 
    # for the dates from the start date to the end date, inclusive.
    inclusive_dates = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature 
    # for a specified start or start-end range.
    return jsonify(inclusive_dates)

if __name__ == "__main__":
    app.run(debug=True)
