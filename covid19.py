import numpy as np
import json
import pandas as pd
import plotly.graph_objs as go
import urllib.request

def read_geojson(url):
    with urllib.request.urlopen(url) as url:
        jdata = json.loads(url.read().decode())
    if   'id'  not in jdata['features'][0].keys():
        if 'properties' in jdata['features'][0].keys():
            if 'id' in jdata['features'][0]['properties']  and \
                jdata['features'][0]['properties']['id'] is not None:
                for k, feat in enumerate(jdata['features']):
                    jdata['features'][k]['id'] = \
                        feat['properties']['id']
            else:
                for k in range(len(jdata['features'])):
                    jdata['features'][k]['id'] = k
    return jdata                

def choropleth_coronavirus(csv_file):
    europe_url = 'https://raw.githubusercontent.com/leakyMirror/'+\
    'map-of-europe/master/GeoJSON/europe.geojson'
    jdata = read_geojson(europe_url)              
    jdata['features'][26]['properties']['NAME'] = 'Macedonia'
    ids = [feat['id'] for feat in jdata['features']]
    names = [feat['properties']['NAME'] for feat in jdata['features']]
    d = dict(zip(names, ids))
    df = pd.read_csv(csv_file)
    countries = list(df['European Region'])
    cids = [d[country]  for country in countries]

    df['cids'] = cids
    dfs = df.sort_values(by=['cids'])
    jdata['features'][26]['properties']['NAME'] = 'Macedonia'
    #my mapbox_access_token
    mapboxt = open(".mapbox_token").read().rstrip()
    locations = dfs['cids'].tolist()
    z = [np.log (cf+0.001) for   cf in dfs['total confirmed']]
    
    fig = go.Figure(go.Choroplethmapbox(
                                z=z,
                                locations=locations,
                                coloraxis='coloraxis',
                                geojson=jdata,
                                marker_line_width=0.75, 
                                marker_line_color='#eeeeee',
                                marker_opacity=0.85))
                            
                            
    fig.update_layout(width=1000, height=800,
                      font_family='Balto',
                      coloraxis=dict(colorscale='Reds',
                                     showscale=False),
                  
                      mapbox = dict(center= dict(lat= 55.499998,  
                                                 lon=17.3833318),
                                    accesstoken= mapboxt,
                                    zoom=2.55,
                                    style='basic'
                               ))

    fig.data[0].customdata = np.stack((dfs['European Region'],
                                       dfs['total confirmed'], 
                                       dfs['total deaths'], 
                                       dfs['transmission']), axis=-1)
    fig.data[0].hovertemplate = \
         "<b>%{customdata[0]}</b>"+\
         "<br><b>Total confirmed cases</b>: %{customdata[1]}"+\
         "<br><b>Total deaths </b>: %{customdata[2]}"+\
         "<br><b>Transmission </b>: %{customdata[3]}<extra></extra>"
    return fig
    
def bars_total(my_df, bar_width=1, mm_dd=f'7 March', name='total confirmed', color='RoyalBlue'):
    # my_df: pd.DataFrame read from a csv file set up from    data provided  by   World Health Org
    # name: string; the name of the dataframe column to be passed to go.Bar
    # returns an instance of the class go.Bar
    return go.Bar(name=f'{name}<br>{mm_dd}', 
                  x=my_df['European Region'], y=my_df[name],
           #width=bar_width,
           marker_color=color,         
           customdata=np.stack(([f'{name}']*len(my_df),
                                 [mm_dd]*len(my_df), 
                                 my_df['European Region'], 
                                 my_df[f'{name}']), axis=-1), 
           hovertemplate='<b>%{customdata[1]}</b><br><b>%{customdata[2]}</b>'+\
                         '<br><b>%{customdata[0]}</b>: %{customdata[3]}<extra></extra>')  

    
