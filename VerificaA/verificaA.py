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

stazioni = pd.read_csv("/workspace/archivioverifiche/coordfix_ripetitori_radiofonici_milano_160120_loc_final.csv", sep=";")
stazionigeo = gpd.read_file("https://dati.comune.milano.it/dataset/7fae4996-02e1-4a80-8794-9ec22454041b/resource/eec5e0ef-2622-443e-a2e4-8b066af2e093/download/ds710_coordfix_ripetitori_radiofonici_milano_160120_loc_final.geojson")
quartieri = gpd.read_file("/workspace/archivioverifiche/ds964_nil_wm.zip")


@app.route("/", methods=["GET"])
def home():
    return render_template("home1.html")

@app.route("/numero", methods=["GET"])
def numero():
    global risultato
    #numero stazioni per ogni municipio
    risultato = stazioni.groupby("MUNICIPIO")["OPERATORE"].count().reset_index()
    return render_template("link1.html", risultato = risultato.to_html())

@app.route("/grafico", methods=["GET"])
def grafico():
    #costruzione del grafico
    fig, ax = plt.subplots(figsize = (6,4))

    x = risultato.MUNICIPIO
    y = risultato.OPERATORE

    ax.bar(x, y)

    #visualizzazione del grafico
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/selezione", methods=["GET"])
def selezione():
    scelta = request.args["scelta"]
    if scelta == "es1":
        return redirect(url_for("numero"))
    elif scelta == "es2":
        return redirect(url_for("input"))
    else:
        return redirect(url_for("dropdown"))

@app.route("/input", methods=["GET"])
def input():
    return render_template("input.html")

@app.route("/ricerca", methods=["GET"])
def ricerca():
    global quartiere, stazioni_quartiere
    nome_quartiere = request.args["quartiere"]
    quartiere = quartieri[quartieri["NIL"].str.contains(nome_quartiere)]
    stazioni_quartiere = stazionigeo[stazionigeo.within(quartiere.geometry.squeeze())]
    return render_template("elenco1.html", risultato = stazioni_quartiere.to_html())

@app.route("/mappa", methods=["GET"])
def mappa():
    fig, ax = plt.subplots(figsize = (12,8))

    stazioni_quartiere.to_crs(epsg=3857).plot(ax=ax, facecolor="k")
    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor="k")
    contextily.add_basemap(ax=ax)   

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/dropdown", methods=["GET"])
def dropdown():
    nomi_stazioni = stazioni.OPERATORE.to_list()
    nomi_stazioni = list(set(nomi_stazioni))
    nomi_stazioni.sort()
    return render_template("dropdown.html", stazioni = nomi_stazioni)

@app.route("/sceltastazioni", methods=["GET"])
def sceltastazioni():
    global quartiere1, stazione_utente
    stazione = request.args["stazione"]
    stazione_utente = stazionigeo[stazionigeo.OPERATORE == stazione]
    quartiere1 = quartieri[quartieri.contains(stazione_utente.geometry.squeeze())]
    return render_template("vistastazioni.html", quartiere = quartiere1.NIL)

@app.route("/mappaquart", methods=["GET"])
def mappaquart():
    fig, ax = plt.subplots(figsize = (12,8))

    stazione_utente.to_crs(epsg=3857).plot(ax=ax, facecolor="k")
    quartiere1.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor="k")
    contextily.add_basemap(ax=ax)   

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)