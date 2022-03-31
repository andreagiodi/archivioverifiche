from flask import Flask, render_template, send_file, make_response, url_for, Response, request
app = Flask(__name__)

import io
import os
import geopandas as gpd
import contextily as ctx
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


stazioni = pd.read_csv("/workspace/archivioverifiche/coordfix_ripetitori_radiofonici_milano_160120_loc_final.csv", sep=";")

quartieri = gpd.read_file("/workspace/archivioverifiche/ds964_nil_wm.zip")

stazioni = gpd.GeoDataFrame(stazioni, geometry=gpd.points_from_xy(stazioni['LONG._decimal'], stazioni['LAT._decimal']))

stazioni.crs = "EPSG:4326"
stazioni.to_crs(epsg=32632)
stazioni = stazioni.drop(columns=['LAT._decimal', 'LONG._decimal','Location'])


@app.route('/', methods=['GET'])
def home():
    
    return render_template('home.html')


@app.route('/numero', methods=['GET'])
def numero():
    #numero stazioni per ogni municipio
    
    risultato = stazioni.groupby('MUNICIPIO')['OPERATORE'].count().reset_index()
    

    return render_template('elenco.html' ,risultato= risultato.to_html())


@app.route('/input', methods=['GET'])
def homeinput():
    
    return render_template('homeinput.html')


@app.route('/rispinput', methods=['GET'])
def input():
    value = request.args['value']
    risp = quartieri[quartieri.NIL.str.contains(value)]
    stazquar = stazioni[stazioni.within(risp.geometry.squeeze())]
    return render_template('input.html',a=stazquar.to_html())

@app.route('/dropdown', methods=['GET'])
def homedropdown():
    
    return render_template('input.html',a=stazquar.to_html())










if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3246, debug=True)