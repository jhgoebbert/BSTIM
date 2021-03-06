import pandas as pd
import numpy as np
import json
import csv
import argparse
import re

from collections import OrderedDict


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Converts Covid-19 Data \
                          Tabels provided by the RKI to a simpler format \
                          to fit the model")
    parser.add_argument(
        "--source",
        nargs=1,
        dest="input_csv",
        default="../data/raw/COVID19.csv",
        help="provide the source csv table")
    parser.add_argument(
        "--destination",
        nargs=1,
        dest="output_csv",
        default="../data/diseases/covid19.csv",
        help="provide the destination file")

    args = parser.parse_args()

    counties = OrderedDict()
    with open("../data/raw/germany_county_shapes.json", "r") as data_file:
        shape_data = json.load(data_file)

    for idx, val in enumerate(shape_data["features"]):
        id_current = val["properties"]["RKI_ID"]
        name_current = val["properties"]["RKI_NameDE"]

        counties[name_current] = id_current

    covid19_data = pd.read_csv(args.input_csv, sep=',')

    # this complicated procedure removes timezone information.
    regex = re.compile(r"([0-9]+)-([0-9]+)-([0-9]+)T.*")
    start_year, start_month, start_day = regex.search(
        covid19_data['Meldedatum'].min()).groups()
    end_year, end_month, end_day = regex.search(
        covid19_data['Meldedatum'].max()).groups()
    start_date = pd.Timestamp(
        int(start_year), int(start_month), int(start_day))
    end_date = pd.Timestamp(int(end_year), int(end_month), int(end_day))

    dates = [day for day in pd.date_range(start_date, end_date)]
    df = pd.DataFrame(index=dates)
    for county_name in counties:
        series = np.zeros(len(df), dtype=np.int32)
        lk_data = covid19_data[covid19_data['Landkreis'] == county_name]
        for (d_id, day) in enumerate(dates):
            day_string = "{:04d}-{:02d}-{:02d}T00:00:00.000Z".format(
                day.year, day.month, day.day)
            cases = np.sum(lk_data[lk_data['Meldedatum']
                                   == day_string]['AnzahlFall'])
            if cases > 0:
                series[d_id] = cases
        df.insert(len(df.columns), counties[county_name], series)

    df.to_csv(args.output_csv, sep=",")
