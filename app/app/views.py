import pandas as pd
from arcgis import GIS
from bokeh.embed import file_html
from bokeh.plotting import figure, output_file, show
from bokeh.resources import CDN
from django.http import HttpResponse


def index(reqeuest):
    data_item = GIS().content.get('772f5cdbb99c4f6689ed1460c26f4b05')
    dataset = pd.read_csv(data_item.get_data(try_json=False))
    date_series = dataset['DateSpecCollect']
    date_series.drop(date_series.tail(1).index, inplace=True)
    # date_series = pd.to_datetime(date_series)
    case_count_series = dataset['Rancho Mission Viejo']
    case_count_series.drop(case_count_series.tail(1).index, inplace=True)
    plot = figure(y_range=date_series, plot_width=800, plot_height=len(date_series) * 18,
               title=f"RMV Case Count By Day: {case_count_series.sum()} total", x_axis_label="Cases Reported",
               tools="pan,box_select,zoom_in,zoom_out,save,reset",
               x_axis_location='above')
    plot.hbar(y=date_series, right=case_count_series, left=0, height=0.4, color="orange",
              fill_alpha=0.5)
    return HttpResponse(file_html(plot, CDN, 'RMV Daily Vid-19 Case'))
