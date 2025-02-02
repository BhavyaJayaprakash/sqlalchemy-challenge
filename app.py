# Importing the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
from flask import Flask, jsonify
import datetime as dt
#################################################
# Database Setup
#################################################

# Creating engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declaring a Base using `automap_base()`
Base = automap_base()
# Reflecting the database tables using the base class
Base.prepare(autoload_with = engine)

# Assigning the classes `measurement` and `station` to a variable called `Measurement`
# and `Station` respectively
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creating a session
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# route for the home page 
"""Note for the user and List all available api routes."""
@app.route("/")
def welcome():
    return (
        f"Module 10 homework<br/>"
        f"================================<br/>"
        f"Available Routes:<br/>"
        f"-----------------<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"-----------------<br/>"
        f"Date format is YYYY-MM-DD<br/>"
        f"For the 4th address add a start date at the end of the route /. <br/>"
        f"For the 5th address add start date after the first / and end date at the end of the route /.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prep():
  
     # query to retrieve the last 12 months of precipitation data. (2017, 8, 23) is the recent dat in the hawaii file in resources
    query_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # extracting the date and precipitation value from the past year
    year_prcp=(session.query(Measurement.date, Measurement.prcp).
            filter(Measurement.date >= query_year).all())

    # Close session
    session.close()

 # Return json 
    all_precipitation = []
    for date,prcp in year_prcp:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_precipitation.append(prcp_dict)
    
   
    return jsonify(all_precipitation)


# Define stations route
@app.route('/api/v1.0/stations')

def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # total_session = session.query(Station.station).all()
    total_session = session.query(Station.id,Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    # all_stations = list(np.ravel(total_session))
    all_station=[]
    for id,station,name,latitude,longitude,elevation in total_session:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_dict['latitude']=latitude
        station_dict['longitude']=longitude
        station_dict['elevation']=elevation
        all_station.append(station_dict)
    return jsonify(all_station)

# # Define temperature route
@app.route('/api/v1.0/tobs')

def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_count=session.query(Station.name).count()

    query_year2 = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   
    active_station = (session.query(Measurement.date, Measurement.tobs)
                        .filter(Measurement.station == 'USC00519281')
                        .filter(Measurement.date >= query_year2).all())

        
    session.close()

    all_tobs= []
    for tobs,date in active_station:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        all_tobs.append(tobs_dict)
       
    return jsonify(all_tobs)

# Define statistics route
# return the min, avg, and max temperatures for date range
@app.route('/api/v1.0/<start>') 
def start(start):
    # Input validation for start date
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please enter YYYY-MM-DD format."}), 400
        
    # Create route session
    session = Session(engine)

    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    Stats_start = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
               .filter(Measurement.date >= start_date).all())
    # Close route session
    session.close()
    
    # Covert results into a dictionary for JSON response
    stats_data = {}
    stats_data["start_date"] = start_date
    stats_data["min_temp"] = Stats_start[0][0]
    stats_data["avg_temp"] = Stats_start[0][1]
    stats_data["max_temp"] = Stats_start[0][2]
   
    return jsonify(stats_data)

# For a specified start and end date, calculate the min, avg, and max temperatures for date range
@app.route("/api/v1.0/<start>/<end>")  
def start_end(start, end):
    # Input validation for start and end date
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD format."}), 400
    
    # Create route session
    session = Session(engine)
    # For a specified start and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date
    startend_sats = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
               .filter(Measurement.date >= start_date)
               .filter(Measurement.date <= end_date).all())
    # Close route session
    session.close()
    
    # Covert results into a dictionary for JSON response
    stats_dict2 = {}
    stats_dict2["start_date"] = start_date
    stats_dict2["end_date"] = end_date
    stats_dict2["min"] = startend_sats[0][0]
    stats_dict2["avg"] = startend_sats[0][1]
    stats_dict2["max"] = startend_sats[0][2]
    
    # Return JSON response
    return jsonify(stats_dict2)
    

if __name__ == '__main__':
    app.run(debug=True)        