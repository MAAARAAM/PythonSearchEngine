import pandas as pd
from Corpus import Corpus
from Document import NewsAPIDocument, GuardianDocument  # Importer les classes filles
from colorama import init, Fore, Style

# Initialiser colorama
init(autoreset=True)

corpus = Corpus("MonCorpus")

# Exemple d'utilisation :
newsapi_data = corpus.fetch_newsapi_data('deep learning', page_size=100)
newsapi_data['type'] = 'newsapi'  # Ajouter une colonne 'type' pour NewsAPI

guardian_data = corpus.fetch_guardian_data('deep learning', page_size=100)
guardian_data['type'] = 'guardian'  # Ajouter une colonne 'type' pour The Guardian

# Combiner les données des deux sources
combined_data = pd.concat([newsapi_data, guardian_data], ignore_index=True)

# Créer des objets Document pour chaque entrée dans combined_data et les ajouter au corpus
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

# Sauvegarder le corpus
corpus.save('corpus.pkl')
print(Fore.GREEN + Style.BRIGHT + "Corpus sauvegardé dans 'corpus.pkl'")

# Sauvegarder le corpus dans un fichier JSON
corpus.export_to_json('corpus.json')
print(Fore.GREEN + "Corpus exporté dans 'corpus.json'")

# Charger le corpus
try:
    print(Fore.CYAN + "\nTentative de chargement du corpus...")
    loaded_corpus = Corpus.load('corpus.pkl')
    print(Fore.CYAN + "\nCorpus chargé depuis le fichier:")

    # Obtenir le nombre total de documents
    total_docs = len(loaded_corpus.id2doc)
    print(Fore.YELLOW + f"Nombre total de documents : {total_docs}")

    # Vérifier s'il y a assez de documents pour appliquer cette logique
    if total_docs <= 20:
        print(Fore.MAGENTA + "\nTous les documents du corpus chargé :")
        for doc_id, doc in loaded_corpus.id2doc.items():
            print(Fore.CYAN + f"ID: {doc_id}")
            print(Fore.YELLOW + f"Source: {doc.getType()}")
            print(Fore.GREEN + f"Titre: {doc.titre}")
            print(Fore.LIGHTWHITE_EX + f"Auteur: {doc.auteur}")
            print(Fore.WHITE + f"Date: {doc.date}")
            print(Fore.WHITE + f"Contenu: {doc.texte[:100]}...")  # Afficher les 100 premiers caractères du contenu
            print(Fore.WHITE + "-" * 50)
    else:
        print(Fore.MAGENTA + "\nLes 10 premiers documents :")
        for doc_id, doc in list(loaded_corpus.id2doc.items())[:10]:
            print(Fore.CYAN + f"ID: {doc_id}")
            print(Fore.YELLOW + f"Source: {doc.getType()}")
            print(Fore.GREEN + f"Titre: {doc.titre}")
            print(Fore.LIGHTWHITE_EX + f"Auteur: {doc.auteur}")
            print(Fore.WHITE + f"Date: {doc.date}")
            print(Fore.WHITE + f"Contenu: {doc.texte[:100]}...")
            print(Fore.WHITE + "-" * 50)

        print(Fore.LIGHTWHITE_EX + "...\n(Plusieurs documents intermédiaires non affichés)\n...")

        print(Fore.MAGENTA + "\nLes 10 derniers documents :")
        for doc_id, doc in list(loaded_corpus.id2doc.items())[-10:]:
            print(Fore.CYAN + f"ID: {doc_id}")
            print(Fore.YELLOW + f"Source: {doc.getType()}")
            print(Fore.GREEN + f"Titre: {doc.titre}")
            print(Fore.LIGHTWHITE_EX + f"Auteur: {doc.auteur}")
            print(Fore.WHITE + f"Date: {doc.date}")
            print(Fore.WHITE + f"Contenu: {doc.texte[:100]}...")
            print(Fore.WHITE + "-" * 50)

    # Ajouter un menu interactif pour afficher les documents selon différents critères
    while True:
        print(Fore.MAGENTA + "\nMenu :")
        print(Fore.CYAN + "1. Afficher les documents triés par date")
        print(Fore.CYAN + "2. Afficher les documents triés par titre")
        print(Fore.CYAN + "3. Afficher les documents de NewsAPI")
        print(Fore.CYAN + "4. Afficher les documents de The Guardian")
        print(Fore.CYAN + "5. Quitter")
        choix = input(Fore.GREEN + "Votre choix (1/2/3/4/5) : ")

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
            print(Fore.RED + "Au revoir !")
            break
        else:
            print(Fore.RED + "Choix invalide, veuillez réessayer.")

except Exception as e:
    print(Fore.RED + f"Erreur lors du chargement du corpus: {e}")
