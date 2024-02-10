# Import the dependencies.
import numpy as np
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
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement

station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# define variables
recent_date = session.query(func.max(measurement.date)).scalar()
year_before = dt.date.fromisoformat(recent_date) - dt.timedelta(days=365)
    
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# start at the homepage, list all the available routes
@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# convert query results from precipitation analysis to dictionary with date as key and prcp as value, return json representation
@app.route("/api/v1.0/precipitation")
def prcp_results():
    """get query of precipitation data"""
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date>=year_before).order_by(measurement.date).all()
    
    """create dictionary from data."""
    dates = []
    precipitation = []
    for date, prcp in results:
        dates.append(date)
        precipitation.append(prcp)
    results_dict = {"date":dates, "precipitation":precipitation}
    return jsonify(results_dict)        

# return json list of stations from dataset
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.name).all()
    station_names = list(np.ravel(results))
    return jsonify(station_names)

# query dates and temperature observations of the most active station for previous year of data, return json lists of temp observations
@app.route("/api/v1.0/tobs")
def active_station():
    results = session.query(measurement.date, measurement.tobs).filter(measurement.date>=year_before, measurement.station == 'USC00519281')\
    .order_by(measurement.date).all()
    dates = []
    temperature = []
    for date, temp in results:
        dates.append(date)
        temperature.append(temp)
    temp_results_dict = {"date":dates, "temperature":temperature}
    return jsonify(temp_results_dict)

# start and end dynamic, return json list of min temp, avg temp, max temp for specified range
@app.route("/api/v1.0/<start>")
def get_start(start_date):
    reformat_date = dt.datetime.strptime(start_date, '%Y%m%d')
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
    .filter(measurement.date>=reformat_date).all()
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def get_range(start_date, end_date):
    reformat_start = dt.datetime.strptime(start_date, '%Y%m%d')
    reformat_end = dt.datetime.strptime(end_date, '%Y%m%d')
    
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
    .filter(measurement.date>=reformat_start, measurement.date<=reformat_end).all()
    return jsonify(results)

# end session engine
session.close()

# set up app to run
if __name__ == '__main__':
    app.run(debug=True)
