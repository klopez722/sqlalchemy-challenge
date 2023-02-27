import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify 

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")

def welcome():
    """available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():

    session = Session(engine)
    previous_year = dt.date(2017,8,23) - dt.timedelta(days = 365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()
    values = {date: prcp for date, prcp in results}
    
    session.close()
    
    return jsonify(values)

@app.route("/api/v1.0/stations")

def stations():
    session = Session(engine)
    station_count = session.query(Station.station).count()
    station_list = list(np.ravel(station_count))
    
    session.close()
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)
    prev_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    prev_date = dt.datetime.strptime(prev_date, "%Y-%M-%D")
    date_query = dt.date(prev_date.year - 1, prev_date.month, prev_date.day)
    
    tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= date_query).all()


    temp = []
    for date, tobs in prev_date:
        d_t = {}
        d_t["date"] = date
        d_t["tobs"] = tobs

        temp.append(d_t)
    
        session.close()
        
    return jsonify(temp)


@app.route("/api/v1.0/<start>")

def start_date(start):
    session = Session(engine)
    tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)). \
        filter(Measurement.date >= start).all()
    
    session.close()
    
    start_tobs_values = []
    for min, avg, max in tobs_results:
        start_tobs_dict = {}
        start_tobs_dict["min"] = min
        start_tobs_dict["average"] = avg
        start_tobs_dict["max"] = max
        start_tobs_values.append(start_tobs_dict)
    
    return jsonify(start_tobs_values)


@app.route("/api/v1.0/<start>/<end>")

def Start_end_date(start, end):
    session = Session(engine)
    
    start_end_date_tobs_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    start_end_tobs_values = []
    for min, avg, max in start_end_date_tobs_results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min_temp"] = min
        start_end_tobs_dict["avg_temp"] = avg
        start_end_tobs_dict["max_temp"] = max
        start_end_tobs_values.append(start_end_tobs_dict)
    
    return jsonify(start_end_tobs_values)


if __name__ == '__main__':
    app.run(debug=True)



