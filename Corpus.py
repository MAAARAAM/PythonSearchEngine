import requests
import pandas as pd
import pickle
import re
from datetime import datetime
from Document import Document
from Author import Author

class Corpus:
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

    def add_document(self, doc):
        doc_id = self.ndoc
        self.id2doc[doc_id] = doc
        self.ndoc += 1

        # Ajouter l'auteur au dictionnaire des auteurs
        if doc.auteur not in self.authors:
            self.authors[doc.auteur] = Author(doc.auteur)
            self.naut += 1
        self.authors[doc.auteur].add_document(doc_id, doc)

    def fetch_newsapi_data(self, query, page_size=100):
        api_key = '00f6a1632dd94bd5ba33be1df3a5cdc9'  # Remplacez par votre clé API valide
        url = f'https://newsapi.org/v2/everything?q={query}&pageSize={page_size}&apiKey={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            data = [{'Author': article.get('author', 'No author available'),
                     'Title': article.get('title', 'No title available'),
                     'Description': article.get('description', 'No description available'),
                     'PublishedAt': article.get('publishedAt', 'No date available'),
                     'Content': article.get('content', 'No content available')} for article in articles]
            return pd.DataFrame(data)
        else:
            print(f"Failed to fetch data from NewsAPI: {response.status_code} - {response.text}")
            return pd.DataFrame()

    def fetch_guardian_data(self, query, page_size=100):
        api_key = '7c313d58-2e49-439f-a5cf-57b6e65a95fb'  # Remplacez par votre clé API valide
        url = f'https://content.guardianapis.com/search?q={query}&page-size={page_size}&api-key={api_key}&show-fields=all'
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get('response', {}).get('results', [])
            data = [{'Author': article.get('fields', {}).get('byline', 'No author available'),
                     'Title': article.get('webTitle', 'No title available'),
                     'Description': article.get('fields', {}).get('trailText', 'No description available'),
                     'PublishedAt': article.get('webPublicationDate', 'No date available'),
                     'Content': article.get('fields', {}).get('bodyText', 'No content available'),
                     'URL': article.get('webUrl', 'No URL available')} for article in articles]
            return pd.DataFrame(data)
        else:
            print(f"Failed to fetch data from The Guardian: {response.status_code} - {response.text}")
            return pd.DataFrame()

    def afficher_documents_tries_par_date(self, n):
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: x.date or datetime.max)[:n]
        for doc in sorted_docs:
            doc.afficher_informations()

    def afficher_documents_tries_par_titre(self, n):
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: x.titre)[:n]
        for doc in sorted_docs:
            doc.afficher_informations()

    def __repr__(self):
        return f"Corpus(nom={self.nom}, ndoc={self.ndoc}, naut={self.naut})"

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        
    def export_to_csv(self, filepath):
        data = [
            {
                'Titre': doc.titre,
                'Auteur': doc.auteur,
                'Date': doc.date.strftime("%Y-%m-%d") if doc.date else "Inconnue",
                'URL': doc.url,
                'Texte': doc.texte[:100]  # Limitez le texte pour éviter des fichiers trop lourds
            }
            for doc in self.id2doc.values()
        ]
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            print(f"Corpus exporté avec succès dans le fichier : {filepath}")
        except Exception as e:
            print(f"Erreur lors de l'exportation vers CSV : {e}")


    @staticmethod
    def load(filepath):
        print(f"Chargement du corpus depuis le fichier: {filepath}")
        with open(filepath, 'rb') as f:
            corpus = pickle.load(f)
        print("Chargement terminé")
        return corpus