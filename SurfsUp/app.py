import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
measurement = Base.classes.measurement
station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Jsonify precipitation data for one year."""
    session = Session(engine)
    # most recent date
    last_date = session.query(func.max(measurement.date)).scalar()
    #  the date one year from the last date in data set.
    date_one_yr_ago_dt = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    query_date = date_one_yr_ago_dt.strftime('%Y-%m-%d')
    #  query to date and prcp  as the value
    last_year = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date >= query_date).all()
    results = []
    for date, prcp in last_year:
        result_dict = {}
        result_dict["date"] = date
        result_dict["prcp"] = prcp
        results.append(result_dict)
    # Close Session
    session.close()
    # Return the results as a JSON dictionary
    return jsonify(results)

@app.route('/api/v1.0/stations')
def stations():
    """Jsonify a list of the stations"""
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    station_list = [result[0] for result in results]
    station_dict = {i: station_list[i] for i in range(0, len(station_list))}

    return jsonify(station_dict)

@app.route('/api/v1.0/tobs')
def tobs():
    """ temperatures observation of the most active station. """
    session = Session(engine)

#Find the dates to query
    latest_string = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    latest_date_tob = dt.datetime.strptime(latest_string, '%Y-%m-%d')
    query_date_tob = dt.date(latest_date_tob.year -1, latest_date_tob.month, latest_date_tob.day)

    active_stations = session.query(measurement.station,func.count(measurement.id)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.id).desc()).first()
    most_active = active_stations[0]
    
#Set up query to get temperature
    query_result = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= query_date_tob).\
        filter(measurement.station == most_active).all()
    session.close()

    temp_results = []

    for date, tobs in query_result:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_results.append(temp_dict)
    return jsonify(temp_results)

@app.route('/api/v1.0/<start>')
def start(start):
    """Jsonify temperature data from a singular date."""
    session = Session(engine)
    
#Temp dictionaries and results to jsonify
    start_date_temp_results = []
    start_date_temp_dict = {}
    
# max temperature
    max_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    start_date_temp_dict['max temp'] = max_temp
    
#Find the min temperature
    min_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start).scalar()
    start_date_temp_dict['min temp'] = min_temp

#Find the avg temperature
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start).scalar() 
    start_date_temp_dict['avg temp'] = avg_temp
    start_date_temp_results.append(start_date_temp_dict)

    return jsonify(start_date_temp_results)

@app.route('/api/v1.0/<start>/<end>')
def start_and_end(start, end):
    """Jsonify temperature data for a between two date."""
    session = Session(engine)
    
#Temp dictionaries and results to jsonify
    start_date_end_date_temp_results = []
    start_date_end_date_temp_dict = {}
    
# the min temperature
    min_temp = session.query(func.min(measurement.tobs)).\
        filter(measurement.date >= start).\
         filter(measurement.date <= end).scalar()
    start_date_end_date_temp_dict['min temp'] = min_temp
    
# the avg temperature
    avg_temp = session.query(func.avg(measurement.tobs)).\
        filter(measurement.date >= start).\
         filter(measurement.date <= end).scalar()
    start_date_end_date_temp_dict['avg temp'] = avg_temp

    start_date_end_date_temp_results.append(start_date_end_date_temp_dict)
    return jsonify(start_date_end_date_temp_results)

#the max temperature
    max_temp = session.query(func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
         filter(measurement.date <= end).scalar()
    start_date_end_date_temp_dict['max temp'] = max_temp

if __name__ == "__main__":
    app.run(debug=True)