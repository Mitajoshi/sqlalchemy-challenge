# Import the dependencies.
from datetime import datetime, timedelta
from flask import Flask, jsonify
import numpy as np

# Python SQL toolkit and Object Relational Mapper
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# 1. Start at the homepage.
#  List all the available routes.@app.route("/")
@app.route("/")
def welcome():
    return (
        f"**************************************************************************<br/>"
        f"Welcome to the climate analysis of Honolulu, Hawaii for vacation planning!<br/>"
        f"**************************************************************************<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/:start<br/>" 
        f"<br/>"
        f"/api/v1.0/:start/:end<br/>"
        f"<br/>"
        f"/api/v1.0/mostactivestations<br/>"
        f"<br/>"
        f"**************************************************************************"
    )


# 2.  Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
#     to a dictionary using date as the key and prcp as the value.
#     Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prec_data():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = datetime.strptime(last_date.date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).filter(
        measurement.date >= one_year_ago,
        measurement.date <= last_date
        ).all()

    # Extract the dates and precipitation values from the query results
    dates = [result.date for result in results]
    precipitation = [result.prcp if result.prcp is not None else 0 for result in results]


    # Create a dictionary from the row data and append to a list of all_passengers
         
    data_dict = {date: prcp for date, prcp in zip(dates, precipitation)}
 
    # Return the JSON representation of the dictionary
    return jsonify(data_dict)


# 3. Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station_data():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(station.station).all()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(results))
    
    # Return the JSON representation of the dictionary
    return jsonify(station_list)


# 4. Query the dates and temperature observations of the most-active station for the previous year of data.
#    Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs_data():
    # Calculate the date one year ago from the last date in the database
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = datetime.strptime(last_date.date, '%Y-%m-%d')
    one_year_ago = last_date - timedelta(days=365)

    most_active_station_id = 'USC00519281'

    results = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == most_active_station_id,
        measurement.date >= one_year_ago,
        measurement.date <= last_date
    ).all()
    tobs_data = [result.tobs for result in results]
    
    # Return the JSON representation of the list
    return jsonify(tobs_data)


# 5. Return a JSON list of the minimum temperature, 
#    the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_statistics(start, end=None):
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.

    if not end:
        temp_stats=session.query(func.min(measurement.tobs), 
                       func.max(measurement.tobs),
                       func.avg(measurement.tobs)).filter(measurement.date > start).first()
    else:
        temp_stats=session.query(func.min(measurement.tobs), 
                       func.max(measurement.tobs),
                       func.avg(measurement.tobs)).filter(measurement.date > start, measurement.date < end ).first()

    temp_stat_dict = {"Lowest Temp": temp_stats[0], "Highest Temp": temp_stats[1], "Avg Temp": temp_stats[2]}

    # Return the JSON representation of the dictionary
    return jsonify(temp_stat_dict)


# EXTRA,PRACTICE FOR FUN 
# Design a query to find the most active stations (i.e. which stations have the most rows?)
# List the stations and their counts in descending order. 
@app.route("/api/v1.0/mostactivestations")
def most_active():
    most_active_stations = session.query(measurement.station, func.count(measurement.id)).group_by(measurement.station).\
                    order_by(func.count(measurement.id).desc()).all()

    most_active_station_list = [{"Station": station, "No. of Measurements": num} for station, num in most_active_stations]

    # Return the JSON representation of the list
    return jsonify(most_active_station_list)


if __name__ == "__main__":
    app.run(debug=True)
