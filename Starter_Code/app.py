import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import timedelta

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/precipitation<br/>"
        f"/stations<br/>"
        f"/tobs<br/>"
        f"/start/    ###date format = yyyy-mm-dd <br/>"
        f"/start/end/  ###date format = yyyy-mm-dd  <br/>"
    )


@app.route("/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Precipitation Route that returns json with the date as the key and value as the precipitation
    
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from data
    all_precip = []
    for date, prcp in results:
        passenger_dict = {}
        passenger_dict["date"] = date
        passenger_dict["prcp"] = prcp
        all_precip.append(passenger_dict)

    return jsonify(all_precip)



#Return a JSON list of stations from the dataset.
@app.route("/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Measurement.id, Measurement.station).all()

    session.close()

    all_stations = []
    for id,station in results:        
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["station"] = station
        all_stations.append(stations_dict)
    return jsonify(all_stations)

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.

@app.route("/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query most active
    station_counts = session.query(Measurement.station,func.count(Measurement.id )).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.id ).desc()).first()
    session.close()
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    precip_12months = session.query(Measurement.date ,Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station.in_(station_counts)).all()

    most_active = []
    for date,tobs in precip_12months:        
        most_active_dict = {}
        most_active_dict["date"] = date
        most_active_dict["tobs"] = tobs
        most_active.append(most_active_dict)
    return jsonify(most_active)

    session.close()


#A start route that: Accepts the start date as a parameter from the URL, Returns the min, max, and average temperatures 
# calculated from the given start date to the end of the dataset (4 points)

@app.route('/start/<sampledate>')
def start(sampledate):

    session = Session(engine)    
    sample_date = sampledate
    format = '%Y-%m-%d'
    date = dt.datetime.strptime(sample_date, format)

    station_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date>= date.date()).all()
    session.close()

    summary_of_station = []
    for row in station_summary:        
        summary_of_station_dict = {}
        summary_of_station_dict["min"] = row[0]
        summary_of_station_dict["max"] = row[1]
        summary_of_station_dict["avg"] = row[2]
        summary_of_station.append(summary_of_station_dict)


    return jsonify(summary_of_station)


# Accepts the start and end dates as parameters from the URL (3 points)
# Returns the min, max, and average temperatures calculated from the given start date to the given end date (6 points)

@app.route('/start/<sampledate>/end/<sampleenddate>')
def starttoend(sampledate,sampleenddate):

    session = Session(engine)    
    sample_date_start = sampledate
    sample_date_end = sampleenddate
    format = '%Y-%m-%d'
    date_start = dt.datetime.strptime(sample_date_start, format)
    date_end = dt.datetime.strptime(sample_date_end, format)

    station_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date>= date_start.date()).\
    filter(Measurement.date<= date_end).all()
    session.close()

    summary_of_station = []
    for row in station_summary:        
        summary_of_station_dict = {}
        summary_of_station_dict["min"] = row[0]
        summary_of_station_dict["max"] = row[1]
        summary_of_station_dict["avg"] = row[2]
        summary_of_station.append(summary_of_station_dict)


    return jsonify(summary_of_station)  

    session.close()

if __name__ == '__main__':
    app.run(debug=True)
