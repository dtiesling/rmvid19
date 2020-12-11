from datetime import datetime

import pandas as pd
from arcgis import GIS
from bokeh.colors import RGB
from bokeh.embed import components
from bokeh.models import AdaptiveTicker
from bokeh.plotting import figure
from django.shortcuts import render

total_population = 3176000
population = {'Aliso Viejo': 51783,
              'Anaheim': 352005,
              'Brea': 43601,
              'Buena Park': 82421,
              'Costa Mesa': 113615,
              'Coto de Caza': 14931,
              'Cypress': 48958,
              'Dana Point': 33730,
              'Fountain Valley': 55814,
              'Fullerton': 139640,
              'Garden Grove': 172646,
              'Huntington Beach': 200641,
              'Irvine': 282572,
              'La Habra': 62183,
              'La Palma': 15568,
              'Ladera Ranch': 30288,
              'Laguna Beach': 22991,
              'Laguna Hills': 31024,
              'Laguna Niguel': 66266,
              'Laguna Woods': 16046,
              'Lake Forest': 85623,
              'Los Alamitos': 11529,
              'Midway City': 8374,
              'Mission Viejo': 95202,
              'Newport Beach': 85326,
              'Orange': 139484,
              'Placentia': 51671,
              'Rancho Mission Viejo': 36686,
              'Rancho Santa Margarita': 48325,
              'Rossmoor': 11160,
              'San Clemente': 64857,
              'San Juan Capistrano': 36013,
              'Santa Ana': 332725,
              'Seal Beach': 24119,
              'Silverado': 2154,
              'Stanton': 38234,
              'Trabuco Canyon': 21041,
              'Tustin': 79795,
              'Villa Park': 5839,
              'Westminster': 90938,
              'Yorba Linda': 67787}


def _get_covid_info():
    """Fetches covid case count info from the OC Open Data Portal."""
    data_item = GIS().content.get('772f5cdbb99c4f6689ed1460c26f4b05')
    dataset = pd.read_csv(data_item.get_data(try_json=False))
    all_cities = list(dataset.keys())
    bad_cities = ['DateSpecCollect', 'Unknown', 'Other', 'Total']
    for bad_city in bad_cities:
        if bad_city in all_cities:
            all_cities.remove(bad_city)
    return all_cities, data_item, dataset


def city_chooser(request):
    """Landing page that renders a list of links to all OC cities."""
    all_cities, data_item, dataset = _get_covid_info()
    context = {'all_cities': all_cities}
    return render(request, 'app/city_chooser.html', context)


def city_stats(request, city):
    """View that renders graphs for case counts in a specific city."""
    city = city.replace('-', ' ').title()
    if city.lower() == 'coto de caza':
        city = 'Coto de Caza'
    all_cities, data_item, dataset = _get_covid_info()
    date_series = dataset['DateSpecCollect']
    date_series.drop(date_series.tail(1).index, inplace=True)
    case_count_series = dataset[city]
    case_count_series.drop(case_count_series.tail(1).index, inplace=True)
    total_series = dataset['Total']

    # Create a bokeh graph for positive cases by day over the past 2 months.
    days_back = 60
    counts_by_day_plot = figure(title=f'Positive cases by day over the last 60 days -- {case_count_series[days_back * -1:].sum()} total cases.',
                  y_range=date_series[days_back * -1:],
                  plot_width=700,
                  plot_height=days_back * 20,
                  tools="save",
                  x_axis_label="Positive Cases Reported",
                  x_axis_location='above',
                  x_minor_ticks=2)
    counts_by_day_plot.hbar(y=date_series,
              right=case_count_series,
              left=0,
              height=0.4,
              color=RGB(79, 70, 229),
              fill_alpha=0.5,
              line_cap='round',
              hatch_alpha=0.0)
    hbar_script, hbar_div = components(counts_by_day_plot)

    # Create a bokeh line graph plotting total case counts over the past 2 weeks.
    total_past_2_weeks_plot = figure(x_range=date_series[-14:],
                       plot_width=500,
                       plot_height=300,
                       y_axis_label="Total case counts",
                       tools="save",
                       title=f'Total case counts over the last 14 days -- {case_count_series[-14:].sum()} new cases.')
    total_past_2_weeks_plot.xaxis.major_label_orientation = 45
    total_past_2_weeks_plot.line(x=date_series, y=case_count_series.cumsum())
    recent_line_script, recent_line_div = components(total_past_2_weeks_plot)

    # Create bokeh line graph showing total case counts since the start of pandemic.
    total_all_time_plot = figure(x_range=date_series,
                           plot_width=500,
                           plot_height=300,
                           y_axis_label="Total case counts",
                           tools="save",
                           title=f'Total case counts since beginning of pandemic.')
    total_all_time_plot.xaxis.visible = False
    total_all_time_plot.xaxis.ticker = AdaptiveTicker(desired_num_ticks=10)
    total_all_time_plot.line(x=date_series, y=case_count_series.cumsum())
    all_line_script, all_line_div = components(total_all_time_plot)

    # Create a bokeh bar graph showing the percentage of total case by day.
    days_back = 14
    percentage_series = (dataset[city]/dataset['Total']) * 100
    percentage_total_plot = figure(title=f'Percentage of new cases reported in OC attributed to {city}.',
                                   x_range=date_series[-14:],
                                   plot_width=500,
                                   plot_height=500,
                                   y_axis_label='% of new cases reported in the county',
                                   x_axis_label=f'* {city} is an estimated {round(population[city] / total_population * 100, 2)}% of total OC population.',
                                   tools='save')
    percentage_total_plot.vbar(x=date_series[-14:],
                               top=percentage_series[-14:],
                               bottom=0,
                               width=0.4,
                               color=RGB(79, 70, 229),
                               fill_alpha=0.5,
                               line_cap='round',
                               hatch_alpha=0.0)
    percentage_total_plot.xaxis.major_label_orientation = 45
    percentage_total_script, percentage_total_div = components(percentage_total_plot)

    context = {'city': city,
               'hbar_script': hbar_script,
               'hbar_div': hbar_div,
               'recent_line_script': recent_line_script,
               'recent_line_div': recent_line_div,
               'all_line_script': all_line_script,
               'all_line_div': all_line_div,
               'percentage_total_script': percentage_total_script,
               'percentage_total_div': percentage_total_div,
               'total_cases': case_count_series.sum(),
               'all_cities': all_cities,
               'last_updated': datetime.utcnow() - datetime.utcfromtimestamp(
                   data_item.modified / 1000)}
    return render(request, 'app/city_stats.html', context)
