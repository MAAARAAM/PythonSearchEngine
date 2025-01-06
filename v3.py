import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from Corpus import Corpus_v2
from Document import NewsAPIDocument, GuardianDocument
from SearchEngine import SearchEngine
import dash_bootstrap_components as dbc

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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

def get_authors(corpus):
    """
    Extract all unique authors from the corpus.

    Args:
        corpus (Corpus): The loaded corpus object.

    Returns:
        dict: A dictionary mapping author names to their documents.
    """
    authors = {}
    for doc_id, doc in corpus.id2doc.items():
        auteur = doc.auteur
        if not auteur or auteur == 'No author available':
            continue  # Ignore documents without a valid author
        if auteur not in authors:
            authors[auteur] = []
        authors[auteur].append(doc)
    return authors

# Step 3: Define the Dash layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Moteur de Recherche de Corpus", className="text-center text-primary mb-4"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Requête:"),
            dcc.Input(id='query-input', type='text', placeholder='Entrez votre requête ici', className='form-control mb-3'),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Nombre de documents:"),
            dcc.Slider(
                id='num-docs-slider',
                min=1,
                max=20,
                step=1,
                value=5,
                marks={i: str(i) for i in range(1, 21)}
            ),
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Button('Rechercher', id='search-button', color='primary', className='mt-3')
        ])
    ]),

    dbc.Row([
        dbc.Col(html.Div(id='results-area', className='mt-4'))
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(html.H3("Autres fonctionnalités", className="text-secondary mb-4"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Button('Afficher les documents triés par date', id='sort-date-button', color='info', className='mb-2'),
            html.Div(id='sort-date-results', className='mb-4')
        ]),
        dbc.Col([
            dbc.Button('Afficher les documents triés par titre', id='sort-title-button', color='info', className='mb-2'),
            html.Div(id='sort-title-results', className='mb-4')
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Button('Afficher les documents par auteur', id='by-author-button', color='info', className='mb-2'),
            html.Div(id='by-author-results', className='mb-4')
        ])
    ])
], fluid=True)

# Step 4: Define the callbacks
@app.callback(
    Output('results-area', 'children'),
    Input('search-button', 'n_clicks'),
    State('query-input', 'value'),
    State('num-docs-slider', 'value')
)
def perform_search(n_clicks, query, num_docs):
    if not query:
        return html.Div("Veuillez entrer une requête valide.", style={'color': 'red'})

    results = search_engine.search(query, n_documents=num_docs)

    if results.empty:
        return html.Div(f"Aucun résultat trouvé pour : '{query}'.", style={'color': 'red'})

    return html.Table([
        html.Thead(html.Tr([html.Th(col) for col in results.columns])),
        html.Tbody([
            html.Tr([html.Td(results.iloc[i][col]) for col in results.columns]) for i in range(len(results))
        ])
    ], className='table table-striped')

@app.callback(
    Output('sort-date-results', 'children'),
    Input('sort-date-button', 'n_clicks')
)
def display_sorted_by_date(n_clicks):
    if not n_clicks:
        return ""

    sorted_docs = corpus_v2.afficher_documents_tries_par_date(10)
    return html.Ul([html.Li(doc.titre) for doc in sorted_docs])

@app.callback(
    Output('sort-title-results', 'children'),
    Input('sort-title-button', 'n_clicks')
)
def display_sorted_by_title(n_clicks):
    if not n_clicks:
        return ""

    sorted_docs = corpus_v2.afficher_documents_tries_par_titre(10)
    return html.Ul([html.Li(doc.titre) for doc in sorted_docs])

@app.callback(
    Output('by-author-results', 'children'),
    Input('by-author-button', 'n_clicks')
)
def display_by_author(n_clicks):
    if not n_clicks:
        return ""

    authors = get_authors(corpus_v2)
    return html.Div([
        html.Label("Sélectionnez un auteur:"),
        dcc.Dropdown(
            id='author-dropdown',
            options=[{'label': author, 'value': author} for author in authors.keys()],
            className='form-control mb-3'
        ),
        html.Div(id='author-documents')
    ])

@app.callback(
    Output('author-documents', 'children'),
    Input('author-dropdown', 'value')
)
def update_author_documents(author):
    if not author:
        return "Veuillez sélectionner un auteur."

    authors = get_authors(corpus_v2)
    documents = authors.get(author, [])

    return html.Ul([html.Li(doc.titre) for doc in documents])

# Step 5: Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
