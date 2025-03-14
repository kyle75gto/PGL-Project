import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Charger vos données
df = pd.read_excel(r'C:\Users\jqygn\Documents\ESILV\A4\S8\0.Adv. Python, Git, Linux for Bl\Project Git\PGL-Project\velib-disponibilite-en-temps-reel.xlsx')

# Compter le nombre de stations à Paris et dans les autres communes
paris_count = df[df['Nom communes équipées'] == 'Paris'].shape[0]
others_count = df[df['Nom communes équipées'] != 'Paris'].shape[0]

# Compter le nombre de stations par arrondissement à Paris
paris_df = df[df['Nom communes équipées'] == 'Paris']
paris_df['Arrondissement'] = paris_df['Code INSEE communes équipées'].astype(str).str[:2]
paris_arrondissement_counts = paris_df['Arrondissement'].value_counts().reset_index()
paris_arrondissement_counts.columns = ['Arrondissement', 'Nombre de stations']

# Compter le nombre de stations par commune hors Paris
other_communes_counts = df[df['Nom communes équipées'] != 'Paris']['Nom communes équipées'].value_counts().reset_index()
other_communes_counts.columns = ['Commune', 'Nombre de stations']

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Préparer les données pour le graphique initial
initial_data = pd.DataFrame({
    'Category': ['Paris', 'Autres'],
    'Nombre de stations': [paris_count, others_count]
})

# Définir la mise en page de l'application
app.layout = html.Div(children=[
    html.H1(children='Répartition des stations Vélib en Île-de-France'),
    dcc.Graph(
        id='main-pie-chart',
        figure=px.pie(initial_data, values='Nombre de stations', names='Category', title='Paris vs Autres Communes')
    )
])

# Callback pour mettre à jour le graphique lorsqu'on clique sur un secteur
@app.callback(
    Output('main-pie-chart', 'figure'),
    Input('main-pie-chart', 'clickData')
)
def update_pie_chart(clickData):
    if not clickData:
        # Retourner le graphique initial si aucun secteur n'est cliqué
        return px.pie(initial_data, values='Nombre de stations', names='Category', title='Paris vs Autres Communes')

    # Extraire la catégorie cliquée
    clicked_category = clickData['points'][0]['label']

    if clicked_category == 'Autres':
        # Afficher la répartition des stations dans les autres communes
        return px.pie(other_communes_counts, values='Nombre de stations', names='Commune', title='Répartition des stations dans les autres communes')
    elif clicked_category == 'Paris':
        # Afficher la répartition des stations par arrondissement à Paris
        return px.pie(paris_arrondissement_counts, values='Nombre de stations', names='Arrondissement', title='Répartition des stations par arrondissement à Paris')

    # Retourner le graphique initial si la catégorie cliquée n'est pas reconnue
    return px.pie(initial_data, values='Nombre de stations', names='Category', title='Paris vs Autres Communes')

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True)
