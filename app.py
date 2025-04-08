import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import os
import imageio
import shutil
import math
from datetime import datetime

# Chargement des données
station_info = pd.read_excel("Informations stations.xlsx")
station_info['Identifiant station'] = station_info['Identifiant station'].astype(int)

data = {}

folder_path = r"Datas"
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path) and filename.endswith(".xlsx"):
        filename_without_extension = os.path.splitext(filename)[0]
        data[filename_without_extension] = pd.read_excel(file_path)

# Paramètres globaux
communes = sorted(station_info['Nom communes équipées'].unique())
dates = sorted(data.keys())
min_date, max_date = dates[0], dates[-1]
# Extraire les dates journalières au format "YYYY-MM-DD"
daily_dates = sorted(set(d[:10] for d in dates))

max_velos = 70

# Initialisation de l'app
app = dash.Dash(suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.H1("Carte Interactive des Vélib' à Paris", style={'textAlign': 'center', 'padding': '20px', 'color': 'white'}),
    dcc.Tabs(id='tabs', value='map-tab', children=[
        dcc.Tab(label='Carte', value='map-tab',
                style={'backgroundColor': '#333', 'color': 'white'},
                selected_style={'backgroundColor': '#555', 'color': 'white'}),
        dcc.Tab(label='Animation', value='animation-tab',
                style={'backgroundColor': '#333', 'color': 'white'},
                selected_style={'backgroundColor': '#555', 'color': 'white'}),
        dcc.Tab(label='Graph', value='graph-tab',
                style={'backgroundColor': '#333', 'color': 'white'},
                selected_style={'backgroundColor': '#555', 'color': 'white'}),
        dcc.Tab(label='Rapport', value='report-tab',
                style={'backgroundColor': '#333', 'color': 'white'},
                selected_style={'backgroundColor': '#555', 'color': 'white'}),
        dcc.Tab(label='À propos', value='about-tab',
                style={'backgroundColor': '#333', 'color': 'white'},
                selected_style={'backgroundColor': '#555', 'color': 'white'}),
    ]),
    html.Div(id='tabs-content', style={'padding': '20px', 'backgroundColor': '#1e1e1e', 'color': 'white'})
], style={'backgroundColor': '#1e1e1e', 'fontFamily': 'Arial', 'height': '100vh', 'margin': 0})

@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'map-tab':
        return html.Div([
            html.Div([
                html.Div([
                    html.H3("Filtres de la carte"),
                    html.H4("Type de Vélo"),
                    dcc.RadioItems(id='velo-type',
                                   options=[
                                       {'label': 'Tous les vélos', 'value': 'all'},
                                       {'label': 'Vélos électriques', 'value': 'electric'},
                                       {'label': 'Vélos mécaniques', 'value': 'mechanical'}
                                   ],
                                   value='all',
                                   labelStyle={'display': 'block'}),

                    html.H4("Communes"),
                    dcc.Dropdown(id='commune-filter',
                                 options=[{'label': c, 'value': c} for c in communes],
                                 multi=True,
                                 placeholder="Choisissez des communes",
                                 style={'color': '#000', 'backgroundColor': '#333'}),

                    html.H4("Date"),
                    dcc.Slider(
                    id='date-slider',
                    min=0,
                    max=len(dates)-1,
                    step=1,
                    value=0,
                    marks={i: date.split('-', maxsplit=1)[1] for i, date in enumerate(dates)},
                    tooltip={'always_visible': False, 'placement': 'bottom', 'template': "{value}"}),

                    html.Div(id='tooltip-content'),

                    html.H4("Vélos disponibles"),
                    dcc.RangeSlider(id='velo-range-slider',
                                    min=0, max=70, step=1,
                                    value=[0, 70],
                                    marks={i: str(i) for i in range(0, 71, 5)})
                ], style={'width': '25%', 'padding': '20px', 'backgroundColor': '#2c2c2c'}),

                html.Div([
                    dcc.Graph(id='velib-map', style={"height": "80vh"})
                ], style={'width': '75%', 'padding': '20px'})
            ], style={'display': 'flex'}),
        ])

    elif tab == 'graph-tab':
        return html.Div([
            html.H3("Évolution de la Disponibilité par Station", style={'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.H4("Choisir une commune"),
                    dcc.Dropdown(
                        id='commune-dropdown',
                        options=[{'label': c, 'value': c} for c in communes],
                        placeholder="Choisissez une commune",
                        style={'color': '#000', 'backgroundColor': '#333'}
                    ),
                    html.H4("Choisir des stations"),
                    dcc.Dropdown(
                        id='station-selector',
                        multi=True,
                        placeholder="Choisissez des stations",
                        style={'color': '#000', 'backgroundColor': '#333'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'backgroundColor': '#2c2c2c', 'padding': '20px'}),
                html.Div([
                    dcc.Graph(id='station-timeseries', style={'backgroundColor': '#1e1e1e'})
                ], style={'width': '70%', 'display': 'inline-block'})
            ])
        ])

    elif tab == 'animation-tab':
        return html.Div([
            html.H3("Évolution Temporelle des Vélibs", style={'textAlign': 'center'}),
            html.Div([
                html.Button('▶️ Play', id='play-btn', n_clicks=0,
                            style={'backgroundColor': '#5a5a5a', 'color': 'white', 'padding': '10px 20px'}),
                html.Button('⏸ Pause', id='pause-btn', n_clicks=0,
                            style={'backgroundColor': '#5a5a5a', 'color': 'white', 'padding': '10px 20px'}),
            ], style={'textAlign': 'center'}),

            dcc.Slider(id='animation-slider',
                       min=0, max=len(dates)-1, step=1,
                       value=0,
                       marks={i: dates[i] for i in range(len(dates))},
                       tooltip={"placement": "bottom"}),

            html.Div(id='current-date-display', style={'textAlign': 'center', 'marginTop': '10px'}),

            dcc.Interval(id='animation-interval', interval=1000, n_intervals=0, disabled=True),
            dcc.Graph(id='animation-map', style={'height': '80vh'})
        ])

    elif tab == 'report-tab':
        return html.Div([
            html.H3("Générer un Rapport GIF", style={'textAlign': 'center'}),
            html.Div([
                html.H4("Choisissez une date"),
                dcc.DatePickerSingle(
                    id='gif-date-picker',
                    min_date_allowed=datetime.strptime(min(daily_dates), '%Y-%m-%d'),
                    max_date_allowed=datetime.strptime(max(daily_dates), '%Y-%m-%d'),
                    initial_visible_month=datetime.strptime(max(daily_dates), '%Y-%m-%d'),
                    display_format='YYYY-MM-DD',
                    style={'textAlign': 'center'}
                )
            ], style={'marginBottom': '30px', 'textAlign': 'center'}),

            html.Button('🎞 Générer GIF', id='generate-gif-btn', n_clicks=0,
                        style={'backgroundColor': '#5a5a5a', 'color': 'white', 'padding': '10px 20px'}),

            dcc.Download(id='download-gif'),
            html.P("Le GIF peut mettre jusqu'à une minute pour se générer"),
            html.Div(id='gif-status', style={'textAlign': 'center', 'marginTop': '20px'})
        ])

    elif tab == 'about-tab':
        return html.Div([
            html.H3("À propos"),
            html.P("Cette application permet de visualiser les stations Vélib' à Paris avec différents filtres.")
        ])

@app.callback(
    Output('tooltip-content', 'children'),
    Input('date-slider', 'value')
)
def update_tooltip(value):
    return f"Date: {dates[value]}"

@app.callback(
    Output('station-selector', 'options'),
    [Input('commune-dropdown', 'value')]
)
def update_station_options(selected_commune):
    if selected_commune:
        filtered = station_info[station_info['Nom communes équipées'] == selected_commune]
        return [{'label': s, 'value': s} for s in sorted(filtered['Nom station'].unique())]
    return []

@app.callback(
    Output('station-timeseries', 'figure'),
    [Input('station-selector', 'value')]
)
def update_timeseries(selected_stations):
    if not selected_stations:
        # Crée une figure vide avec un message d'information
        return {
            "data": [],
            "layout": go.Layout(
                title="Veuillez sélectionner une commune et des stations",
                plot_bgcolor='#1e1e1e',
                paper_bgcolor='#1e1e1e',
                font=dict(color='white'),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False),
                annotations=[
                    dict(
                        text="Aucune donnée sélectionnée",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5,
                        showarrow=False,
                        font=dict(size=16, color="white")
                    )
                ]
            )
        }

    # Crée la figure du graphique lorsque des stations sont sélectionnées
    fig = go.Figure()
    for station in sorted(selected_stations):
        values = []
        for date in dates:
            df = pd.merge(data[date], station_info, on='Identifiant station')
            match = df[df['Nom station'] == station]
            if not match.empty:
                values.append(match['Nombre total vélos disponibles'].values[0])
            else:
                values.append(None)
        fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name=station))

    fig.update_layout(title='Évolution de la disponibilité des vélos',
                      xaxis_title='Date',
                      yaxis_title='Vélos disponibles',
                      plot_bgcolor='#1e1e1e',
                      paper_bgcolor='#1e1e1e',
                      font=dict(color='white'))

    return fig

@app.callback(
    Output('velib-map', 'figure'),
    [Input('velo-type', 'value'),
     Input('commune-filter', 'value'),
     Input('date-slider', 'value'),
     Input('velo-range-slider', 'value')]
)
def update_map(selected_type, selected_communes, selected_date_index, velo_range):
    selected_date = dates[selected_date_index]
    df = pd.merge(data[selected_date], station_info, on='Identifiant station')
    filtered_df = df.copy()

    if selected_communes:
        filtered_df = filtered_df[filtered_df['Nom communes équipées'].isin(selected_communes)]

    if selected_type == 'electric':
        filtered_df = filtered_df[filtered_df['Vélos électriques disponibles'] > 0]
        size_col = 'Vélos électriques disponibles'
    elif selected_type == 'mechanical':
        filtered_df = filtered_df[filtered_df['Vélos mécaniques disponibles'] > 0]
        size_col = 'Vélos mécaniques disponibles'
    else:
        size_col = 'Nombre total vélos disponibles'

    filtered_df = filtered_df[(filtered_df[size_col] >= velo_range[0]) & (filtered_df[size_col] <= velo_range[1])]

    return go.Figure(go.Scattermapbox(
        lat=filtered_df['Latitude'],
        lon=filtered_df['Longitude'],
        mode='markers',
        marker=dict(size=filtered_df[size_col],
                    color=filtered_df[size_col],
                    colorscale='Viridis',
                    cmin=0,
                    cmax=max_velos,
                    showscale=True,
                    colorbar=dict(
                        title="Vélos disponibles",
                        title_font_color="white",
                        bgcolor="#333",
                        tickfont=dict(color="white")
                    )),
        text=filtered_df['Nom station']
    )).update_layout(
        mapbox_style="carto-darkmatter",
        mapbox_center={"lat": 48.8566, "lon": 2.3522},
        mapbox_zoom=11,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

@app.callback(
    Output('animation-interval', 'disabled'),
    [Input('play-btn', 'n_clicks'),
     Input('pause-btn', 'n_clicks')],
    [State('animation-interval', 'disabled')]
)
def control_animation(play_clicks, pause_clicks, is_disabled):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    return False if triggered_id == 'play-btn' else True

@app.callback(
    Output('animation-slider', 'value'),
    [Input('animation-interval', 'n_intervals')],
    [State('animation-slider', 'value')]
)
def update_slider_on_interval(n_intervals, current_value):
    return 0 if current_value + 1 >= len(dates) else current_value + 1

@app.callback(
    [Output('animation-map', 'figure'),
     Output('current-date-display', 'children')],
    [Input('animation-slider', 'value')]
)
def update_map_on_slider(index):
    selected_date = dates[index]
    df = pd.merge(data[selected_date], station_info, on='Identifiant station')

    fig = go.Figure(go.Scattermapbox(
        lat=df['Latitude'],
        lon=df['Longitude'],
        mode='markers',
        marker=dict(size=10,
                    color=df['Nombre total vélos disponibles'],
                    colorscale='Viridis',
                    cmin=0,
                    cmax=max_velos,
                    showscale=True,
                    colorbar=dict(
                        title="Vélos disponibles",
                        title_font_color="white",
                        bgcolor="#333",
                        tickfont=dict(color="white")
                    )),
        text=df['Nom station']
    ))

    fig.update_layout(
        mapbox_style="carto-darkmatter",
        mapbox_center={"lat": 48.8566, "lon": 2.3522},
        mapbox_zoom=11,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig, f"📅 Date affichée : {selected_date}"

@app.callback(
    [Output('download-gif', 'data'),
     Output('gif-status', 'children')],
    [Input('generate-gif-btn', 'n_clicks')],
    [State('gif-date-picker', 'date')]
)
def generate_daily_gif(n_clicks, selected_date):
    if n_clicks > 0 and selected_date:
        selected_date = selected_date[:10]  # 'YYYY-MM-DD'

        temp_img_dir = "temp_images"
        gif_output_dir = "generated_gifs"
        os.makedirs(temp_img_dir, exist_ok=True)
        os.makedirs(gif_output_dir, exist_ok=True)

        selected_snapshots = sorted([d for d in dates if d.startswith(selected_date)])
        if not selected_snapshots:
            return None, f"⚠️ Aucune donnée trouvée pour le {selected_date}"

        images = []
        for i, date in enumerate(selected_snapshots):
            df = pd.merge(data[date], station_info, on='Identifiant station')
            fig = go.Figure(go.Scattermapbox(
                lat=df['Latitude'],
                lon=df['Longitude'],
                mode='markers',
                marker=dict(size=8,
                            color=df['Nombre total vélos disponibles'],
                            colorscale='Viridis',
                            cmin=0,
                            cmax=max_velos,
                            showscale=True,
                            colorbar=dict(
                                title="Vélos disponibles",
                                title_font_color="white",
                                bgcolor="#333",
                                tickfont=dict(color="white")
                            )),
                text=df['Nom station']
            ))
            fig.update_layout(mapbox_style="carto-darkmatter",
                              mapbox_center={"lat": 48.8566, "lon": 2.3522},
                              mapbox_zoom=10,
                              margin={"r": 0, "t": 0, "l": 0, "b": 0})

            # Extraire l'heure et les minutes du format 'YYYY-MM-DD-HH-MM'
            date_parts = date.split('-')
            hour = int(date_parts[3])
            minute = int(date_parts[4])

            # Dessiner le cadran de l'horloge
            fig.add_shape(
                type="circle",
                xref="paper", yref="paper",
                x0=0.85, y0=0.85, x1=0.95, y1=0.95,
                line_color="white",
            )

            # Dessiner les aiguilles de l'horloge
            fig.add_shape(
                type="line",
                xref="paper", yref="paper",
                x0=0.9, y0=0.9,
                x1=0.9 + 0.04 * math.sin(math.radians(360 * (hour % 12) / 12 + minute / 60)),
                y1=0.9 + 0.04 * math.cos(math.radians(360 * (hour % 12) / 12 + minute / 60)),
                line=dict(color="white", width=2),
            )

            fig.add_shape(
                type="line",
                xref="paper", yref="paper",
                x0=0.9, y0=0.9,
                x1=0.9 + 0.06 * math.sin(math.radians(360 * minute / 60)),
                y1=0.9 + 0.06 * math.cos(math.radians(360 * minute / 60)),
                line=dict(color="white", width=1),
            )

            # Ajouter une annotation de texte pour la date et l'heure
            fig.add_annotation(
                text=f"Date: {date}",
                xref="paper", yref="paper",
                x=0.05, y=0.95,
                showarrow=False,
                font=dict(size=12, color="white"),
                bgcolor="black"
            )

            img_path = os.path.join(temp_img_dir, f"{i:03d}.png")
            fig.write_image(img_path)
            images.append(imageio.imread(img_path))

        gif_filename = f"velib_{selected_date}.gif"
        gif_path = os.path.join(gif_output_dir, gif_filename)
        imageio.mimsave(gif_path, images, format='GIF', duration=12, loop=0)

        shutil.rmtree(temp_img_dir)
        return dcc.send_file(gif_path), f"✅ GIF généré : {gif_filename}"

    return None, ""

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=False)
