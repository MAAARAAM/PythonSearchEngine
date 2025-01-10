import pandas as pd
from Corpus import Corpus
from Document import NewsAPIDocument, GuardianDocument
from colorama import init, Fore, Style

init(autoreset=True)

def main():
    """
    Main function to demonstrate the creation and management of a corpus.
    Includes data fetching from NewsAPI and The Guardian, saving/loading the corpus,
    and providing an interactive menu for displaying documents.
    """
    corpus = Corpus("MonCorpus")

    newsapi_data = corpus.fetch_newsapi_data('deep learning', page_size=100)
    newsapi_data['type'] = 'newsapi'

    guardian_data = corpus.fetch_guardian_data('deep learning', page_size=100)
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
        corpus.add_document(doc)

    corpus.save('corpus.pkl')
    print(Fore.GREEN + Style.BRIGHT + "Corpus sauvegardé dans 'corpus.pkl'")

    corpus.export_to_json('corpus.json')
    print(Fore.GREEN + "Corpus exporté dans 'corpus.json'")

    try:
        print(Fore.CYAN + "\nTentative de chargement du corpus...")
        loaded_corpus = Corpus.load('corpus.pkl')
        print(Fore.CYAN + "\nCorpus chargé depuis le fichier:")

        total_docs = len(loaded_corpus.id2doc)
        print(Fore.YELLOW + f"Nombre total de documents : {total_docs}")

        if total_docs <= 20:
            print(Fore.MAGENTA + "\nTous les documents du corpus chargé :")
            for doc_id, doc in loaded_corpus.id2doc.items():
                print_document_details(doc_id, doc)
        else:
            print(Fore.MAGENTA + "\nLes 10 premiers documents :")
            for doc_id, doc in list(loaded_corpus.id2doc.items())[:10]:
                print_document_details(doc_id, doc)

            print(Fore.LIGHTWHITE_EX + "...\n(Plusieurs documents intermédiaires non affichés)\n...")

            print(Fore.MAGENTA + "\nLes 10 derniers documents :")
            for doc_id, doc in list(loaded_corpus.id2doc.items())[-10:]:
                print_document_details(doc_id, doc)

        interactive_menu(loaded_corpus)

    except Exception as e:
        print(Fore.RED + f"Erreur lors du chargement du corpus: {e}")

def print_document_details(doc_id, doc):
    """
    Print the details of a single document in a formatted style.

    Args:
        doc_id (int): The document ID.
        doc (Document): The document object containing its details.
    """
    print(Fore.CYAN + f"ID: {doc_id}")
    print(Fore.YELLOW + f"Source: {doc.getType()}")
    print(Fore.GREEN + f"Titre: {doc.titre}")
    print(Fore.LIGHTWHITE_EX + f"Auteur: {doc.auteur}")
    print(Fore.WHITE + f"Date: {doc.date}")
    print(Fore.WHITE + f"Contenu: {doc.texte[:1000]}...")
    print(Fore.WHITE + "-" * 50)

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
        if auteur not in authors:
            authors[auteur] = []
        authors[auteur].append(doc)
    return authors


def interactive_menu(loaded_corpus):
    """
    Display an interactive menu for various document display options.

    Args:
        loaded_corpus (Corpus): The loaded corpus object.
    """
    authors = get_authors(loaded_corpus) 

    while True:
        print(Fore.MAGENTA + "\nMenu :")
        print(Fore.CYAN + "1. Afficher les documents triés par date")
        print(Fore.CYAN + "2. Afficher les documents triés par titre")
        print(Fore.CYAN + "3. Afficher les documents de NewsAPI")
        print(Fore.CYAN + "4. Afficher les documents de The Guardian")
        print(Fore.CYAN + "5. Afficher les documents par auteur")
        print(Fore.CYAN + "6. Quitter")
        choix = input(Fore.GREEN + "Votre choix (1/2/3/4/5/6) : ")

        if choix == '1':
            print(Fore.YELLOW + "\nDocuments triés par date :")
            loaded_corpus.afficher_documents_tries_par_date(5)
        elif choix == '2':
            print(Fore.YELLOW + "\nDocuments triés par titre :")
            loaded_corpus.afficher_documents_tries_par_titre(5)
        elif choix == '3':
            print(Fore.YELLOW + "\nDocuments de NewsAPI :")
            for doc_id, doc in loaded_corpus.id2doc.items():
                if doc.getType() == 'newsapi':
                    doc.afficher_informations()
        elif choix == '4':
            print(Fore.YELLOW + "\nDocuments de The Guardian :")
            for doc_id, doc in loaded_corpus.id2doc.items():
                if doc.getType() == 'guardian':
                    doc.afficher_informations()
        elif choix == '5':
            print(Fore.YELLOW + "\nListe des auteurs :")
            for idx, auteur in enumerate(authors.keys(), start=1):
                print(Fore.CYAN + f"{idx}. {auteur}")

            auteur_choisi = input(Fore.GREEN + "Choisissez un auteur (numéro) : ")
            try:
                auteur_choisi = int(auteur_choisi) - 1
                auteur_nom = list(authors.keys())[auteur_choisi]
                print(Fore.YELLOW + f"\nDocuments de {auteur_nom} :")
                for doc in authors[auteur_nom]:
                    doc.afficher_informations()
            except (ValueError, IndexError):
                print(Fore.RED + "Choix invalide, veuillez réessayer.")
        elif choix == '6':
            print(Fore.RED + "Au revoir !")
            break
        else:
            print(Fore.RED + "Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    main()
