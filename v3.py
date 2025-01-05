import pandas as pd
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from Corpus import Corpus_v2
from Document import NewsAPIDocument, GuardianDocument
from SearchEngine import SearchEngine
from colorama import init
from tabulate import tabulate
import nltk
from tqdm import tqdm
import ipywidgets as widgets
from IPython.display import display, clear_output

nltk.download('stopwords')
init(autoreset=True)

def main():
    """
    Combine functionalities of v1 and v2, and introduce enhancements from TD8.
    All features are encapsulated within an interactive interface.
    """
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

    # Step 3: Interface Widgets
    title_label = widgets.Label("\nMoteur de Recherche de Corpus\n")
    query_input = widgets.Text(description="Requête:")
    num_docs_slider = widgets.IntSlider(value=5, min=1, max=20, step=1, description="Nb docs:")
    search_type_dropdown = widgets.Dropdown(
        options=['Recherche simple', 'Recherche avancée', 'Concordance'],
        value='Recherche simple',
        description='Type:'
    )
    output_area = widgets.Output()
    search_button = widgets.Button(description="Rechercher")

    def on_search_click(b):
        """Handle search button click."""
        with output_area:
            clear_output()
            query = query_input.value.strip()
            num_docs = num_docs_slider.value
            search_type = search_type_dropdown.value

            if not query:
                print("Veuillez entrer une requête valide.")
                return

            if search_type == 'Recherche simple':
                results = search_engine.search(query, n_documents=num_docs)
            elif search_type == 'Recherche avancée':
                results = search_engine.advanced_search(query, n_documents=num_docs)
            elif search_type == 'Concordance':
                results = corpus_v2.concorde(query, context_size=3)
            else:
                print("Type de recherche non reconnu.")
                return

            if results.empty:
                print(f"Aucun résultat trouvé pour : '{query}'.")
            else:
                print("\nRésultats de la recherche :")
                print(tabulate(results, headers="keys", tablefmt="grid", showindex=False))

    search_button.on_click(on_search_click)

    # Layout
    interface = widgets.VBox([
        title_label,
        widgets.HBox([query_input, num_docs_slider, search_type_dropdown]),
        search_button,
        output_area
    ])

    display(interface)

if __name__ == "__main__":
    main()
