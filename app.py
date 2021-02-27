import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"Hawaii Precipitation Data Home Page<br/>"
        f"/api/v1.0/precipitation - Precipitation within the last year<br/>"
        f"/api/v1.0/stations - All Hawaii precipitation stations<br/>"
        f"/api/v1.0/tobs - Temperature data for the past year for the most active station<br/>"
        f"/api/v1.0/temp/start - Min, max, and avg temperature for all dates on and before start date (format: YYYY-MM-DD)<br/>"
        f"/api/v1.0/temp/start/end - Min, max, and avg temperature for all dates between entered dates (format: YYYY-MM-DD)"
    )   
   
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Precipitation within the last year"""
    precip_results = session.query(Measurement.date, Measurement.prcp).\
                     filter(Measurement.date >= "2016-08-24").filter(Measurement.date <= "2017-08-23").\
                     filter(Measurement.station == "USC00516128").order_by(Measurement.date).all()
    precip_dict = {date: prcp for date, prcp in precip_results}
    session.commit()
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """All Hawaii Precipitation Stations"""
    stations = pd.read_sql(session.query(Station.name, Station.station).statement, session.query(Station.name, Station.station).session.bind)
    session.commit()
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    """Temperature Data for the Past Year for Station USC00519281"""
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
                   filter(Measurement.date >= "2016-08-24").filter(Measurement.date <= "2017-08-23").\
                   order_by(Measurement.date).all()
    tobs_dict = {date: tobs for date, tobs in tobs_results}
    session.commit()
    return jsonify(tobs_dict)

@app.route("/api/v1.0/temp/<start>")
def start(start):
    one_day_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                      filter(Measurement.date >= start).all()
    session.commit()
    return jsonify(one_day_results)

@app.route("/api/v1.0/temp/<start>/<end>")
def startend(start,end):
    multi_day_results = session.query(*(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs))).\
                        filter(Measurement.date >= start).filter(Measurement.date <= end).\
                        order_by(Measurement.date).all()
    session.commit()
    return jsonify (multi_day_results)


if __name__ == "__main__":
    app.run(debug=True)