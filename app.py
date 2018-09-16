import numpy as np
import pandas as pd

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

#Flask App
app = Flask(__name__)

# Database Setup
engine = create_engine("sqlite:///db/belly_button_biodiversity.sqlite", echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)
Sample = Base.classes.samples
OTU = Base.classes.otu
Metadata = Base.classes.samples_metadata

session = Session(engine)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/names')
def names():
    samples = session.query(Sample).statement
    samples_df = pd.read_sql_query(samples, session.bind)
    samples_df.set_index('otu_id', inplace=True)
    return jsonify(list(samples_df.columns))

@app.route('/otu')
def otu():
    all_otus = session.query(OTU).statement
    all_otus_df = pd.read_sql_query(all_otus, session.bind)
    all_otus_df.set_index('otu_id', inplace=True)
    return jsonify(list(all_otus_df["lowest_taxonomic_unit_found"]))

@app.route('/metadata/<sample>')
def metadata(sample):
    samples_metadata = session.query(Metadata).statement
    samples_metadata_df = pd.read_sql_query(samples_metadata, session.bind)
    sample_num = int(sample.split("_")[1])
    selected_sample = samples_metadata_df.loc[samples_metadata_df["SAMPLEID"] == sample_num, :]
    json_selected_sample = selected_sample.to_json(orient='records')
    return json_selected_sample

@app.route('/wfreq/<sample>')
def wfreq(sample):
    samples_metadata = session.query(Metadata).statement
    samples_metadata_df = pd.read_sql_query(samples_metadata, session.bind)
    sample_num = int(sample.split("_")[1])
    selected_sample = samples_metadata_df.loc[samples_metadata_df["SAMPLEID"] == sample_num, :]
    wfreq = selected_sample["WFREQ"].values[0]
    return f"{wfreq}"

@app.route('/samples/<sample>')
def samples(sample):
    all_otus = session.query(OTU).statement
    all_otus_df = pd.read_sql_query(all_otus, session.bind)
    all_otus_df.set_index('otu_id', inplace=True)

    samples = session.query(Sample).statement
    samples_df = pd.read_sql_query(samples, session.bind)
    selected_sample = samples_df[sample]
    otu_ids = samples_df['otu_id']
    selection_df = pd.DataFrame({
        "otu_ids":otu_ids,
        "samples":selected_sample
    })
    sortedSelect_df = selection_df.sort_values(by=['samples'], ascending=False)
    sorted_otu = {"otu_ids": list(sortedSelect_df['otu_ids'].values)}
    sorted_samples = {"sample_values": list(sortedSelect_df['samples'].values)}
    for i in range(len(sorted_otu["otu_ids"])):
        sorted_otu["otu_ids"][i] = int(sorted_otu["otu_ids"][i])
    for i in range(len(sorted_samples["sample_values"])):
        sorted_samples["sample_values"][i] = int(sorted_samples["sample_values"][i])
    results = [sorted_otu, sorted_samples, list(all_otus_df["lowest_taxonomic_unit_found"])]
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
