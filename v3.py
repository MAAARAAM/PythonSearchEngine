import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from Corpus import Corpus_v2
from Document import NewsAPIDocument, GuardianDocument
from SearchEngine import SearchEngine

# Initialize Dash app
app = dash.Dash(__name__)

# Step 1: Initialize Corpus and Load Data
corpus_v2 = Corpus_v2("MonCorpusV3")

newsapi_data = corpus_v2.fetch_newsapi_data('deep learning', page_size=100)
newsapi_data['type'] = 'newsapi'

guardian_data = corpus_v2.fetch_guardian_data('deep learning', page_size=100)
guardian_data['type'] = 'guardian'

combined_data = pd.concat([newsapi_data, guardian_data], ignore_index=True)

for index, row in combined_data.iterrows():
    if row['type'] == 'newsapi':
        doc = NewsAPIDocument(
            titre=row.get('Title', 'No title available'),
            auteur=row.get('Author', 'No author available'),
            date=row.get('PublishedAt', 'No date available'),
            texte=row.get('Content', 'No content available'),
            description=row.get('Description', 'No description available')
        )
    elif row['type'] == 'guardian':
        doc = GuardianDocument(
            titre=row.get('Title', 'No title available'),
            auteur=row.get('Author', 'No author available'),
            date=row.get('PublishedAt', 'No date available'),
            texte=row.get('Content', 'No content available'),
            description=row.get('Description', 'No description available')
        )
    corpus_v2.add_document(doc)

# Step 2: Search Engine Initialization
search_engine = SearchEngine(corpus_v2)

# Step 3: Define the Dash layout
app.layout = html.Div([
    html.H1("Moteur de Recherche de Corpus"),

    # Query Input
    html.Div([
        html.Label("Requête:"),
        dcc.Input(id='query-input', type='text', placeholder='Entrez votre requête ici', style={'width': '100%'}),
    ], style={'margin-bottom': '10px'}),

    # Number of Documents Slider
    html.Div([
        html.Label("Nombre de documents:"),
        dcc.Slider(
            id='num-docs-slider',
            min=1,
            max=20,
            step=1,
            value=5,
            marks={i: str(i) for i in range(1, 21)}
        ),
    ], style={'margin-bottom': '20px'}),

    # Search Type Dropdown
    html.Div([
        html.Label("Type de recherche:"),
        dcc.Dropdown(
            id='search-type-dropdown',
            options=[
                {'label': 'Recherche simple', 'value': 'simple'},
                {'label': 'Recherche avancée', 'value': 'advanced'},
                {'label': 'Concordance', 'value': 'concordance'}
            ],
            value='simple'
        ),
    ], style={'margin-bottom': '20px'}),

    # Search Button
    html.Button('Rechercher', id='search-button', n_clicks=0),

    # Results Area
    html.Div(id='results-area', style={'margin-top': '20px'})
])

# Step 4: Define the callback for search functionality
@app.callback(
    Output('results-area', 'children'),
    Input('search-button', 'n_clicks'),
    State('query-input', 'value'),
    State('num-docs-slider', 'value'),
    State('search-type-dropdown', 'value')
)
def perform_search(n_clicks, query, num_docs, search_type):
    if not query:
        return html.Div("Veuillez entrer une requête valide.", style={'color': 'red'})

    if search_type == 'simple':
        results = search_engine.search(query, n_documents=num_docs)
    elif search_type == 'advanced':
        results = search_engine.advanced_search(query, n_documents=num_docs)
    elif search_type == 'concordance':
        results = corpus_v2.concorde(query, context_size=3)
    else:
        return html.Div("Type de recherche non reconnu.", style={'color': 'red'})

    if results.empty:
        return html.Div(f"Aucun résultat trouvé pour : '{query}'.", style={'color': 'red'})

    # Display results in a table
    return html.Div([
        html.H3("Résultats de la recherche:"),
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in results.columns])),
            html.Tbody([
                html.Tr([html.Td(results.iloc[i][col]) for col in results.columns]) for i in range(len(results))
            ])
        ], style={'border': '1px solid black', 'border-collapse': 'collapse', 'width': '100%'})
    ])

# Step 5: Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
