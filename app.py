import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s==%(funcName)s==%(message)s')

life_exp_df = pd.read_csv('data/country_data_master.csv',
                          usecols=['country', 'lat', 'lon', 'median_age_total',
                                   'median_age_male', 'median_age_female', 'map_ref',
                                   'life_exp_total', 'life_exp_male', 'life_exp_female'])
life_exp_df = life_exp_df.sort_values(['life_exp_total'])
map_ref = ['Africa', 'Arctic Region', 'Asia', 'Central America and the Caribbean',
           'Europe', 'Middle East', 'North America', 'South America', 'Southeast Asia']

app = dash.Dash()
server = app.server
app.title = 'Life Expectancy at Birth by Country Dashboard - 2017 (CIA World Factbook)'

app.layout = html.Div([
    dcc.Graph(id='life_exp_scatter',
              config={'displayModeBar': False}),
    html.Div([
            html.Div([
            dcc.Dropdown(id='countries',
                         placeholder='Countries',
                         multi=True,
                         value=tuple(),
                         options=[{'label': c, 'value': c}
                                  for c in sorted(life_exp_df['country'])]),
            ], style={'width': '35%', 'display': 'inline-block', 'background-color': '#eeeeee'}),
            html.Div([
                    dcc.Dropdown(id='region',
                                 placeholder='Region',
                                 value='',
                                 options=[{'label': r, 'value': r}
                                          for r in map_ref]),
            ], style={'width': '35%', 'display': 'inline-block', 'background-color': '#eeeeee'}),


    ], style={'margin-left': '25%', 'background-color': '#eeeeee'}),
    
    dcc.Graph(id='bubble_chart',
              config={'displayModeBar': False},
              figure={
                  'data': [go.Scattergeo(lon=life_exp_df['lon'],
                                         lat=life_exp_df['lat'],
                                         mode='markers',
                                         hoverinfo='text',
                                         text='<b>' + life_exp_df['country'].astype(str) + '</b>' + '<br>' + 
                                              'Life Expectancy at Birth' + '<br>' +
                                              'Total: ' + life_exp_df['life_exp_total'].astype(str) + '<br>' +
                                              'Male: ' + life_exp_df['life_exp_male'].astype(str) + '<br>' +
                                              'Female: ' + life_exp_df['life_exp_female'].astype(str),
                                         marker={'size': 27, 'color': life_exp_df['life_exp_total'],
                                                 'line': {'color': '#000000', 'width': 0.2},
                                                 'colorscale': 'Cividis',
                                                 'colorbar': {'outlinewidth': 0},
                                                 'showscale': True})],
                  'layout': go.Layout(title='Life Expectancy at Birth - 2017',
                                      font={'family': 'Palatino'},
                                      titlefont={'size': 22},
                                      paper_bgcolor='#eeeeee',
                                      width=1420,
                                      height=750,
                                      geo={'showland': True,
                                           'landcolor': '#eeeeee',
                                           'showland': True,
                                           'countrycolor': '#cccccc',
                                           'showcountries': True,
                                           'showocean': True,
                                           'oceancolor': '#eeeeee',
                                           'showcoastlines': True,
                                           'showframe': False,
                                           'coastlinecolor': '#cccccc'})
              }),
    html.A('@eliasdabbas', href='https://www.twitter.com/eliasdabbas'), 
    html.P(),
    html.Content('Data: CIA World Factobook  '),
    html.A('Life Expectancy at Birth in Years - 2017', href='https://www.cia.gov/library/publications/the-world-factbook/fields/2102.html'),
    html.Br(),
    html.Content('  Code: '),
    html.A('github.com/eliasdabbas/life_expectancy', href='https://github.com/eliasdabbas/life_expectancy'), html.Br(), html.Br(),
    html.Content('This entry contains the average number of years to be lived by a group of people born in the same year, '
                 'if mortality at each age remains constant in the future. Life expectancy at birth is also a measure of '
                 'overall quality of life in a country and summarizes the mortality at all ages. It can also be thought of '
                 'as indicating the potential return on investment in human capital and is necessary for the calculation of '
                 'various actuarial measures.')
        
], style={'background-color': '#eeeeee'})

@app.callback(Output('life_exp_scatter', 'figure'),
             [Input('countries', 'value'), Input('region', 'value')])
def color_countries_and_region(countries, region):
    logging.info(msg=locals())
    df = life_exp_df[life_exp_df['country'].isin(countries)]
    df_region = life_exp_df[life_exp_df['map_ref'] == region]
    return {'data': [go.Scatter(x=life_exp_df['country'],
                                y=life_exp_df[col],
                                mode='markers',
                                showlegend=True,
                                name=col.replace('_', ' ').title())
                     for col in ['life_exp_total', 'life_exp_male', 'life_exp_female']] +

                    [go.Scatter(x=df_region['country'],
                                y=df_region[col],
                                mode='markers',
                                showlegend=False,
                                hoverinfo='x+text',
                                hovertext=df_region['country'],
                                marker={'color': '#000000', 'size': 10},
                                )
                     for col in ['life_exp_total', 'life_exp_male', 'life_exp_female']] +

                    [go.Scatter(x=[df[df['country'] == country]['country'].iloc[0] for i in range(3)],
                                y=df[df['country'] == country][['life_exp_total', 'life_exp_male', 'life_exp_female']].iloc[0],
                                mode='markers',
                                name=country,
                                marker={'size': 11, 'line': {'color': '#000000', 'width': 1}})
                     for country in countries],

           'layout': go.Layout(title=('Life Expectancy at Birth 2017 ' + ', '.join(countries)) +
                                     ('' if not region else '  (' + ',  '.join([region]) + ' Countries Highlighted)'),
                               height=650,
                               margin={'r': 0, 't': 70, 'b': 70, 'l': 40},
                               titlefont={'size': 22},
                               font={'family': 'Palatino'},
                               legend={'orientation': 'h', 'font': {'size': 18}, 'xanchor': 'center', 'x': 0.5},
                               xaxis={'showticklabels': False},
                               plot_bgcolor='#eeeeee',
                               paper_bgcolor='#eeeeee')}

if __name__ == '__main__':
    app.run_server()