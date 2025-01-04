import pandas as pd
from Corpus import Corpus
from Document import NewsAPIDocument, GuardianDocument  # Importer les classes filles

corpus = Corpus("MonCorpus")

# Example usage :
newsapi_data = corpus.fetch_newsapi_data('deep learning', page_size=100)
newsapi_data['type'] = 'newsapi'  # Ajouter une colonne 'type' pour NewsAPI

guardian_data = corpus.fetch_guardian_data('deep learning', page_size=100)
guardian_data['type'] = 'guardian'  # Ajouter une colonne 'type' pour The Guardian

# Afficher les données récupérées de NewsAPI
print("Données récupérées de NewsAPI:")
print(newsapi_data)

# Afficher les données récupérées de The Guardian
print("\nDonnées récupérées de The Guardian:")
print(guardian_data)

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

# Vérifiez que les documents sont bien ajoutés au corpus
print(f"\nNombre de documents dans le corpus avant sauvegarde: {len(corpus.id2doc)}")

# Afficher les documents triés par date
print("\nDocuments triés par date:")
corpus.afficher_documents_tries_par_date(5)

# Afficher les documents triés par titre
print("\nDocuments triés par titre:")
corpus.afficher_documents_tries_par_titre(5)

# Sauvegarder le corpus
corpus.save('corpus.pkl')
print("Corpus sauvegardé dans 'corpus.pkl'")
# Sauvegarder le corpus dans un fichier CSV
corpus.export_to_json('corpus.json')
print("Corpus exporté dans 'corpus.json'")

# Charger le corpus
try:
    print("Tentative de chargement du corpus...")
    loaded_corpus = Corpus.load('corpus.pkl')
    print("\nCorpus chargé depuis le fichier:")

    # Obtenir le nombre total de documents
    total_docs = len(loaded_corpus.id2doc)
    print(f"Nombre total de documents : {total_docs}")

    # Vérifier s'il y a assez de documents pour appliquer cette logique
    if total_docs <= 20:
        print("\nTous les documents du corpus chargé :")
        for doc_id, doc in loaded_corpus.id2doc.items():
            print(f"ID: {doc_id}")
            print(f"Source: {doc.getType()}")
            print(f"Titre: {doc.titre}")
            print(f"Auteur: {doc.auteur}")
            print(f"Date: {doc.date}")
            print(f"Contenu: {doc.texte[:100]}...")  # Afficher les 100 premiers caractères du contenu
            print("-" * 50)
    else:
        for doc_id, doc in list(loaded_corpus.id2doc.items())[:10]:
            print(f"ID: {doc_id}")
            print(f"Source: {doc.getType()}")
            print(f"Titre: {doc.titre}")
            print(f"Auteur: {doc.auteur}")
            print(f"Date: {doc.date}")
            print(f"Contenu: {doc.texte[:100]}...")
            print("-" * 50)

        print("...\n(Plusieurs documents intermédiaires non affichés)\n...")

        for doc_id, doc in list(loaded_corpus.id2doc.items())[-10:]:
            print(f"ID: {doc_id}")
            print(f"Source: {doc.getType()}")
            print(f"Titre: {doc.titre}")
            print(f"Auteur: {doc.auteur}")
            print(f"Date: {doc.date}")
            print(f"Contenu: {doc.texte[:100]}...")
            print("-" * 50)

except Exception as e:
    print(f"Erreur lors du chargement du corpus: {e}")


