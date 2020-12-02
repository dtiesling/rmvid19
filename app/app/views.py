from datetime import datetime

import pandas as pd
import time
from arcgis import GIS
from bokeh.core.enums import LineCap
from bokeh.embed import components
from bokeh.plotting import figure
from django.shortcuts import render


def index(request):
    data_item = GIS().content.get('772f5cdbb99c4f6689ed1460c26f4b05')
    dataset = pd.read_csv(data_item.get_data(try_json=False))
    date_series = dataset['DateSpecCollect']
    date_series.drop(date_series.tail(1).index, inplace=True)
    case_count_series = dataset['Rancho Mission Viejo']
    case_count_series.drop(case_count_series.tail(1).index, inplace=True)
    plot = figure(y_range=date_series,
                  plot_width=800,
                  plot_height=len(date_series) * 18,
                  tools="save",
                  x_axis_label="Positive Cases Reported",
                  x_axis_location='above',
                  x_minor_ticks=2,
                  )
    plot.hbar(y=date_series,
              right=case_count_series,
              left=0,
              height=0.4,
              color="blue",
              fill_alpha=0.5,
              line_cap='round',
              hatch_alpha=0.0)

    script, div = components(plot)
    context = {'bokeh_script': script,
               'bokeh_div': div,
               'total_cases': case_count_series.sum(),
               'last_updated': datetime.utcnow() - datetime.utcfromtimestamp(data_item.modified/1000)}
    return render(request, 'app/index.html', context)
