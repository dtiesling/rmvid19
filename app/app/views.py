import os
from datetime import datetime

import pandas as pd
from arcgis import GIS
from bokeh.colors import RGB
from bokeh.embed import components
from bokeh.models import AdaptiveTicker
from bokeh.plotting import figure
from django.shortcuts import render, redirect


def root(request):
    return redirect('city-stats', 'rancho-mission-viejo')


def city_stats(request, city):
    city = city.replace('-', ' ').title()
    if city.lower() == 'coto de caza':
        city = 'Coto de Caza'
    data_item = GIS().content.get('772f5cdbb99c4f6689ed1460c26f4b05')
    dataset = pd.read_csv(data_item.get_data(try_json=False))
    all_cities = list(dataset.keys())
    bad_cities = ['DateSpecCollect', 'Unknown', 'Other', 'Total']
    for bad_city in bad_cities:
        if bad_city in all_cities:
            all_cities.remove(bad_city)
    date_series = dataset['DateSpecCollect']
    date_series.drop(date_series.tail(1).index, inplace=True)
    case_count_series = dataset[city]
    case_count_series.drop(case_count_series.tail(1).index, inplace=True)
    days_back = 60
    plot = figure(title=f'Positive cases by day over the last 60 days -- {case_count_series[days_back * -1:].sum()} total cases.',
                  y_range=date_series[days_back * -1:],
                  plot_width=700,
                  plot_height=days_back * 20,
                  tools="save",
                  x_axis_label="Positive Cases Reported",
                  x_axis_location='above',
                  x_minor_ticks=2)
    plot.hbar(y=date_series,
              right=case_count_series,
              left=0,
              height=0.4,
              color=RGB(79, 70, 229),
              fill_alpha=0.5,
              line_cap='round',
              hatch_alpha=0.0)
    hbar_script, hbar_div = components(plot)

    recent_line_plot = figure(x_range=date_series[-14:],
                       plot_width=500,
                       plot_height=300,
                       y_axis_label="Total case counts",
                       tools="save",
                       title=f'Total case counts over the last 14 days -- {case_count_series[-14:].sum()} new cases.')
    recent_line_plot.xaxis.major_label_orientation = 45
    recent_line_plot.line(x=date_series, y=case_count_series.cumsum())
    recent_line_script, recent_line_div = components(recent_line_plot)

    all_line_plot = figure(x_range=date_series,
                           plot_width=500,
                           plot_height=300,
                           y_axis_label="Total case counts",
                           tools="save",
                           title=f'Total case counts since beginning of pandemic.')
    all_line_plot.xaxis.visible = False
    all_line_plot.xaxis.ticker = AdaptiveTicker(desired_num_ticks=10)
    all_line_plot.line(x=date_series, y=case_count_series.cumsum())
    all_line_script, all_line_div = components(all_line_plot)

    context = {'city': city,
               'hbar_script': hbar_script,
               'hbar_div': hbar_div,
               'recent_line_script': recent_line_script,
               'recent_line_div': recent_line_div,
               'all_line_script': all_line_script,
               'all_line_div': all_line_div,
               'total_cases': case_count_series.sum(),
               'all_cities': all_cities,
               'last_updated': datetime.utcnow() - datetime.utcfromtimestamp(
                   data_item.modified / 1000)}
    return render(request, 'app/city_stats.html', context)

def city_chooser(request):
    context = {}
    return render(request, 'app/city_chooser.html', context)
