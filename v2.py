import pandas as pd
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from Corpus import Corpus
from Document import NewsAPIDocument, GuardianDocument
import nltk
from Corpus import Corpus_v2
from SearchEngine import SearchEngine
from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)

nltk.download('stopwords')

def main():
    """
    Main function to demonstrate the usage of Corpus and SearchEngine classes.
    Includes data fetching, corpus creation, statistics, sentiment analysis,
    word cloud generation, and a basic search interface.
    """
    corpus_v2 = Corpus_v2("MonCorpusV2")

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

    print(Fore.BLUE + Style.BRIGHT + "Résultats de la recherche (search) :")
    search_results = corpus_v2.search('deep learning')
    if search_results:
        print(Fore.GREEN + str(search_results))
    else:
        print(Fore.RED + "Aucun résultat trouvé pour 'deep learning'.")

    print(Fore.BLUE + Style.BRIGHT + "\nConcordances :")
    concordances = corpus_v2.concorde('deep learning', context_size=3)
    if not concordances.empty:
        print(tabulate(concordances, headers="keys", tablefmt="grid", showindex=False))
    else:
        print(Fore.RED + "Aucune concordance trouvée pour 'deep learning'.")

    print(Fore.BLUE + Style.BRIGHT + "\nStatistiques sur les mots :")
    stats = corpus_v2.stats(n_mots=10)
    print(tabulate(stats, headers="keys", tablefmt="grid", showindex=False))

    print(Fore.YELLOW + "\nAffichage du nuage de mots...")
    corpus_v2.nuage_de_mots()

    print(Fore.BLUE + Style.BRIGHT + "\nAnalyse sentimentale :")
    corpus_v2.analyse_sentimentale()

    search_engine = SearchEngine(corpus_v2)

    query = input(Fore.CYAN + Style.BRIGHT + "\nEntrez votre requête de recherche : ").strip()

    if not query:
        print(Fore.RED + "La requête est vide. Veuillez entrer un ou plusieurs mots-clés.")
    else:
        resultats = search_engine.search(query)

        if resultats.empty:
            print(Fore.RED + f"Aucun résultat trouvé pour la requête : '{query}'.")
        else:
            print(Fore.GREEN + "\nRésultats de la recherche :")
            print(tabulate(resultats, headers="keys", tablefmt="grid", showindex=False))

if __name__ == "__main__":
    main()
