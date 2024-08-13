import pandas as pd
from flask import Flask, request, jsonify
import flask
import re
import time
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io 
from io import BytesIO
import os

#data came from spotify csvs online, recording artists, songs, and streams

app = Flask(__name__)
df = pd.read_csv("main.csv")
total_visited = 0
a_visited = 0
b_visited = 0
dictIP = {}

num_subscribed = 0
def count_subscribers():
    global num_subscribed
    num_subscribed += 1

@app.route('/')
def home():
    global total_visited
    global a_visited
    global b_visited
    total_visited += 1
    version = "A"
    if total_visited % 2 == 1 and total_visited < 11:
        version = "B"
    if total_visited >= 11:
        version = "A" if a_visited > b_visited else "B"
        
    with open("index.html") as f:
        html = f.read()
        if version == "A":
            html = html.replace("REPLACE", """<a style="color:red;" href="donate.html?from=A">donate</a>""")
        else:
            html = html.replace("REPLACE", """<a href="donate.html?from=B">donation link</a>""")
    return html
 
@app.route('/browse.html')
def browse_handler():
    return """<html><body><h1>Browse<h1/><body/><html/>""" + df.to_html()

@app.route('/browse.json')
def browseJSON():
    global dictIP
    ipAddress = flask.request.remote_addr
    if ipAddress in dictIP.keys():
        if time.time() - dictIP[ipAddress] > 60:
            dictIP[ipAddress] = time.time()
            return jsonify(df.to_dict())
        else:
            return flask.Response("<b>go away</b>",
                                  status=429,
                                  headers={"Retry-After": "60"})
    else:
        dictIP[ipAddress] = time.time()
        return jsonify(df.to_dict())
    
@app.route('/visitors.json')
def visitors_handler():
    global dictIP
    return dictIP

@app.route('/donate.html')
def donate_handler():
    global a_visited
    global b_visited
    if str(flask.request.args.get("from")) == "A":
        a_visited += 1
    else:
        b_visited += 1
    return """<html><body><h1>Donate<h1/><body/><html/>""" + "PLEASE DONATE NOW"

@app.route('/dashboard1.svg')
def dashboard1():    
    fig, ax = plt.subplots(figsize=(6, 4))
    pd.Series(df["Total Streams"]*(1e-6)).plot.hist(ax=ax, bins=50)
    ax.set_xlabel("Total Streams (in milions)")
    ax.set_ylabel("Number of Songs")
    plt.tight_layout()
    f = BytesIO() 
    fig.savefig(f, format="svg")
    fig.savefig("dashboard1.svg", format="svg")
    plt.close()
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route('/dashboard2.svg')
def dashboard2():    
    fig, ax = plt.subplots(figsize=(6, 4))
    if flask.request.args.get("type") == "streams":
        newDF = pd.pivot_table(df, index=['Artist Name'],values=['Total Streams'],aggfunc='sum')
        newDF["Total Streams"] *= (1e-6)
        top_10 = newDF.nlargest(10, 'Total Streams')
        top_10.plot.bar(ax=ax, title = "Cumulative Stream Count: Top 100 (Top 10 Artists)")
        ax.set_xlabel("Artists")
        ax.set_ylabel("Cumulative Stream Count (millions)")
        fig.savefig("dashboard1-query.svg", format="svg")
    else:
        top_10 = (df['Artist Name'].value_counts())[:10]
        top_10.plot.bar(ax=ax, x = "Artist Name", title = "Cumulative Song Count: Top 100 (Top 10 Artists)")
        ax.set_xlabel("Artists")
        ax.set_ylabel("Cumulative Song Count")
    plt.tight_layout()
    f = BytesIO() 
    fig.savefig(f, format="svg")
    fig.savefig("dashboard2.svg", format="svg")
    plt.close()
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$", email)) > 0:
        with open("emails.txt", "a") as f: 
            f.write(email + "\n") # 2
        count_subscribers()
        return jsonify(f"Thanks, here is your subscriber number: {num_subscribed}!")
    return jsonify("Please insert a valid email")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False)