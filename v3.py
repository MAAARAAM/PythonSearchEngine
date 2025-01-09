import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
from Corpus import Corpus_v2
from Document import NewsAPIDocument, GuardianDocument
from SearchEngine import SearchEngine
import dash_bootstrap_components as dbc

# Initialize Dash app with Bootstrap theme and suppress callback exceptions
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

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
    # Store for storing extracted data
    dcc.Store(id='corpus-data-store'),

    # Interface for Theme Selection
    dbc.Row([
        dbc.Col(html.H1("Interface de Recherche Avancée", className="text-center text-primary mb-4"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Thème d'extraction:"),
            dcc.Input(id='theme-input', type='text', placeholder='Entrez le thème ici', className='form-control mb-3'),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Button('Charger les données', id='load-data-button', color='success', className='mt-3')
        ])
    ]),

    dbc.Row([
        dbc.Col(html.Div(id='data-loading-status', className='mt-4'))
    ]),

    html.Hr(),

    # Interface 1
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

    dbc.Row([dbc.Col(html.Div(id='results-area', className='mt-4'))]),

    html.Hr(),

    # Interface 2
    dbc.Row([
        dbc.Col(html.H1("Moteur de Recherche de Corpus", className="text-center text-primary mb-4"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Button('Afficher les documents triés par date', id='sort-date-button', color='info', className='mx-2'),
            dbc.Button('Afficher les documents triés par titre', id='sort-title-button', color='info', className='mx-2'),
            dbc.Button('Afficher les documents par auteur', id='by-author-button', color='info', className='mx-2'),
        ], width=12, className="d-flex justify-content-center mb-3")
    ]),

    dbc.Row([dbc.Col(html.Div(id='document-list', className='mt-4'))]),

    html.Hr()
], fluid=True)

# Step 4: Define the callbacks
@app.callback(
    [Output('corpus-data-store', 'data'),
     Output('data-loading-status', 'children')],
    Input('load-data-button', 'n_clicks'),
    State('theme-input', 'value')
)

def load_data(n_clicks, theme):
    if not theme:
        return None, html.Div("Veuillez entrer un thème valide pour charger les données.", style={'color': 'red'})

    # Fetch data based on the theme
    newsapi_data = corpus_v2.fetch_newsapi_data(theme, page_size=100)
    newsapi_data['type'] = 'newsapi'

    guardian_data = corpus_v2.fetch_guardian_data(theme, page_size=100)
    guardian_data['type'] = 'guardian'

    combined_data = pd.concat([newsapi_data, guardian_data], ignore_index=True)

    documents = []
    for index, row in combined_data.iterrows():
        if row['type'] == 'newsapi':
            documents.append({
                'titre': row.get('Title', 'No title available'),
                'auteur': row.get('Author', 'No author available'),
                'date': row.get('PublishedAt', 'No date available'),
                'texte': row.get('Content', 'No content available'),
                'description': row.get('Description', 'No description available'),
                'type': 'newsapi'
            })
        elif row['type'] == 'guardian':
            documents.append({
                'titre': row.get('Title', 'No title available'),
                'auteur': row.get('Author', 'No author available'),
                'date': row.get('PublishedAt', 'No date available'),
                'texte': row.get('Content', 'No content available'),
                'description': row.get('Description', 'No description available'),
                'type': 'guardian'
            })

    return documents, html.Div(f"Données chargées avec succès pour le thème : '{theme}'.", style={'color': 'green'})

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
    Output('document-list', 'children'),
    [Input('sort-date-button', 'n_clicks'),
     Input('sort-title-button', 'n_clicks'),
     Input('by-author-button', 'n_clicks'),
     Input('corpus-data-store', 'data')]
)

def update_document_list(sort_date_clicks, sort_title_clicks, by_author_clicks, corpus_data):
    if not corpus_data:
        return "Aucun document disponible. Veuillez charger les données."
    
    # Convert the data back into a DataFrame
    df = pd.DataFrame(corpus_data)

    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'sort-date-button':
            df = df.sort_values(by='date', ascending=True)
        elif button_id == 'sort-title-button':
            df = df.sort_values(by='titre', ascending=True)
        elif button_id == 'by-author-button':
            # Filter valid authors (exclude null)
            authors = df['auteur'].dropna().unique()

            return html.Div([
                html.Label("Sélectionnez un auteur:"),
                dcc.Dropdown(
                    id='author-dropdown',
                    options=[
                        {'label': author, 'value': author}
                        for author in authors if author  # Exclude null or empty authors
                    ],
                    className='form-control mb-3'
                ),
                html.Div(id='author-documents')
            ])

    return html.Ul([html.Li(f"{row['titre']} - {row['auteur'] or 'Auteur inconnu'}") for _, row in df.iterrows()])
@app.callback(
    Output('author-documents', 'children'),
    [Input('author-dropdown', 'value'),
     State('corpus-data-store', 'data')]
)
def update_author_documents(author, corpus_data):
    if not corpus_data:
        return "Aucun document disponible. Veuillez charger les données."
    
    if not author:
        return "Veuillez sélectionner un auteur."
    
    df = pd.DataFrame(corpus_data)
    author_docs = df[df['auteur'] == author]

    return html.Ul([html.Li(doc) for doc in author_docs['titre']])

# Step 5: Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
