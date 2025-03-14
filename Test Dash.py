from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash()

# Charger les données
df = pd.read_excel(r'PGL-Project\velib-disponibilite-en-temps-reel.xlsx')

# Séparation de la colonne en deux colonnes distinctes
df[['Latitude', 'Longitude']] = df["Coordonnées géographiques"].str.split(",", expand=True)

# Conversion en type numérique
df['Latitude'] = df['Latitude'].astype(float)
df['Longitude'] = df['Longitude'].astype(float)

# Suppression de l'ancienne colonne
df.drop(columns=["Coordonnées géographiques"], inplace=True)

# Liste des communes pour le filtre, triée par ordre alphabétique
communes = sorted(df['Nom communes équipées'].unique())

# Définir la mise en page avec une carte plus grande
app.layout = html.Div([
    html.H1("Carte Interactive des Vélib' à Paris", style={'textAlign': 'center'}),

    html.Div([
        html.H3("Filtres", style={'margin-bottom': '10px'}),
        dcc.RadioItems(
            id='velo-type',
            options=[
                {'label': 'Tous les vélos', 'value': 'all'},
                {'label': 'Vélos électriques', 'value': 'electric'},
                {'label': 'Vélos mécaniques', 'value': 'mechanical'}
            ],
            value='all',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        ),
        dcc.Dropdown(
            id='commune-filter',
            options=[{'label': commune, 'value': commune} for commune in communes],
            placeholder="Sélectionnez une ou plusieurs communes",
            multi=True,  # Permettre la sélection multiple
            style={'margin-bottom': '10px'}
        ),
    ], style={'margin': '20px'}),

    html.Div([
        dcc.Graph(id='velib-map', style={"height": "80vh", "width": "200vh", "margin-bottom": "20px"})  # Ajustement de la hauteur
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'})
])

@app.callback(
    Output('velib-map', 'figure'),
    [Input('velo-type', 'value'),
     Input('commune-filter', 'value')]
)
def update_map(selected_type, selected_communes):
    filtered_df = df.copy()

    if selected_communes:
        filtered_df = filtered_df[filtered_df['Nom communes équipées'].isin(selected_communes)]

    if selected_type == 'electric':
        filtered_df = filtered_df[filtered_df['Vélos électriques disponibles'] > 0]
        size_col = 'Vélos électriques disponibles'
        color_col = 'Vélos électriques disponibles'
    elif selected_type == 'mechanical':
        filtered_df = filtered_df[filtered_df['Vélos mécaniques disponibles'] > 0]
        size_col = 'Vélos mécaniques disponibles'
        color_col = 'Vélos mécaniques disponibles'
    else:
        size_col = 'Nombre total vélos disponibles'
        color_col = 'Nombre total vélos disponibles'

    # Carte des stations
    map_fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        size=size_col,
        color=color_col,
        text="Nom station",
        zoom=10,
        center={"lat": 48.8566, "lon": 2.3522},
        mapbox_style="carto-darkmatter"
    )

    return map_fig

if __name__ == '__main__':
    app.run(debug=True)

