from flask import Flask, render_template, send_file, make_response, url_for, Response, request
app = Flask(__name__)

import io
import os
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

quartieri = gpd.read_file("/workspace/flaskverificabus/NIL_WM.zip")
trasporti = gpd.read_file("/workspace/flaskverificabus/tpl_percorsi_shp.zip")

@app.route('/', methods = ["GET"])
def homepage():
    return render_template("homepage.html")

@app.route('/homepage2', methods = ["GET"])
def homepage2():
    if request.args["sel"] == "Linee con lunghezza compresa":
        return render_template("lineelung.html")
    if request.args["sel"] == "Lista linee quartiere":
        return render_template("listaquartiere.html")
    if request.args["sel"] == "Mappa linea città":
        return render_template("mappacitta.html")

@app.route('/listaquartiere', methods = ["GET"])
def mappaquartiere():
    value = request.args["value"]
    quartiere = quartieri[quartieri.NIL.str.contains(value)]
    lineequartiere = trasporti[trasporti.crosses(quartiere.geometry.squeeze())].sort_values(by = "linea", ascending = True)
    return lineequartiere.to_html()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3246, debug=True)