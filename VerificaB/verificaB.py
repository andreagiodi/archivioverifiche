from flask import Flask, render_template, request, Response, redirect, url_for
app = Flask(__name__)

import io
import pandas as pd
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

stazioni = gpd.read_file("https://dati.comune.milano.it/dataset/7fae4996-02e1-4a80-8794-9ec22454041b/resource/eec5e0ef-2622-443e-a2e4-8b066af2e093/download/ds710_coordfix_ripetitori_radiofonici_milano_160120_loc_final.geojson")
quartieri = gpd.read_file("/workspace/Flask/appEs6/static/files/ds964_nil_wm.zip")


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/scelta", methods=["GET"])
def scelta():
    quartieri_scelta = quartieri.NIL.sort_values()
    return render_template("scelta.html", quartieri = quartieri_scelta)

@app.route("/elenco", methods=["GET"])
def elenco():
    quartiereUtente = request.args["quartiere"]
    quartiere = quartieri[quartieri["NIL"] == quartiereUtente]
    stazioni_quartiere = stazioni[stazioni.within(quartiere.geometry.squeeze())]
    return render_template("elenco.html", tabella = stazioni_quartiere.to_html())

@app.route("/ricerca", methods=["GET"])
def ricerca():
    return render_template("ricerca.html")

@app.route("/mappa", methods=["GET"])
def mappa():
    global quartiere_ricerca, stazioni_ricerca
    quartiereUtente = request.args["quartiere"]
    quartiere_ricerca = quartieri[quartieri["NIL"].str.contains(quartiereUtente)]
    stazioni_ricerca = stazioni[stazioni.within(quartiere_ricerca.geometry.squeeze())]
    return render_template("mappa.html", quartiere = quartiere_ricerca.NIL)

@app.route("/mappa.png", methods=["GET"])
def mappapng():
    fig, ax = plt.subplots(figsize = (12,8))

    quartiere_ricerca.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
    stazioni_ricerca.to_crs(epsg=3857).plot(ax=ax, facecolor="k")
    contextily.add_basemap(ax=ax)   

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/grafico", methods=["GET"])
def grafico():
    global stazioni_municipio
    stazioni_municipio = stazioni.groupby("MUNICIPIO")["OPERATORE"].count().reset_index().sort_values("MUNICIPIO")
    return render_template("grafico.html", tabella = stazioni_municipio.to_html())

@app.route("/grafico.png", methods=["GET"])
def graficopng():
    fig, ax = plt.subplots(figsize = (12,8))

    ax.bar(stazioni_municipio.MUNICIPIO,stazioni_municipio.OPERATORE)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)