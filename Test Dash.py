from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import numpy as np 

app = Dash()

df = pd.read_excel('velib-disponibilite-en-temps-reel (2).xlsx')

# Séparation de la colonne en deux colonnes distinctes
df[['Latitude', 'Longitude']] = df["Coordonnées géographiques"].str.split(",", expand=True)

# Conversion en type numérique
df['Latitude'] = df['Latitude'].astype(float)
df['Longitude'] = df['Longitude'].astype(float)

# Suppression de l'ancienne colonne
df.drop(columns=["Coordonnées géographiques"], inplace=True)

# Créer une carte avec Plotly Express
fig = px.scatter_mapbox(
    df,
    lat="Latitude",
    lon="Longitude",
    color="Nombre total vélos disponibles",
    text="Nom station",
    zoom=10,  # Augmenter le zoom
    center={"lat": 48.8566, "lon": 2.3522},  # Centrer sur Paris
    #mapbox_style="open-street-map"
    mapbox_style="carto-darkmatter"
)

# Définir la mise en page avec une carte plus grande
app.layout = html.Div([
    html.H1("Carte Interactive des Vélib' à Paris"),
    dcc.Graph(figure=fig, style={"height": "90vh"})  # Ajustement de la hauteur
])

if __name__ == '__main__':
    app.run(debug=True)

