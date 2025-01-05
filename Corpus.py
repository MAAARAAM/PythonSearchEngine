import requests
import pandas as pd
import pickle
import re
from datetime import datetime
from Document import Document
from Author import Author
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from nltk.corpus import stopwords

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
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: x.date or datetime.min, reverse=True)[:n]
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
        
    def export_to_json(self, filepath):
        # Filtrer les documents pour exclure ceux avec des données non valides
        data = [
            {
                'Titre': doc.titre,
                'Auteur': doc.auteur,
                'Date': doc.date.strftime("%Y-%m-%d") if doc.date else "Inconnue",
                'Texte': doc.texte
            }
            for doc in self.id2doc.values()
            if doc.titre != "[Removed]" and doc.auteur is not None
        ]
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                import json
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Corpus exporté avec succès dans le fichier : {filepath}")
        except Exception as e:
            print(f"Erreur lors de l'exportation vers JSON : {e}")


    @staticmethod
    def load(filepath):
        print(f"Chargement du corpus depuis le fichier: {filepath}")
        with open(filepath, 'rb') as f:
            corpus = pickle.load(f)
        print("Chargement terminé")
        return corpus
    
# Classe Corpus de la 2ème version
class Corpus_v2(Corpus):

    def __init__(self, nom):
        super().__init__(nom)
        self.textes_concat = ""

    # Partie 1.1 : Fonction de recherche avec expressions régulières
    def search(self, keyword):
        if not self.textes_concat:
            self.textes_concat = " ".join([doc.texte for doc in self.id2doc.values()])
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
        passages = [match.group(0) for match in pattern.finditer(self.textes_concat)]
        return passages

    # Partie 1.2 : Fonction Concordance
    def concorde(self, expression, context_size=5):
        if not self.textes_concat:
            self.textes_concat = " ".join([doc.texte for doc in self.id2doc.values()])
        
        # Expression régulière pour capturer le contexte gauche, le motif, et le contexte droit
        pattern = re.compile(
            r"(\S+\s){0," + str(context_size) + r"}(\b" + re.escape(expression) + r"\b)(\s\S+){0," + str(context_size) + r"}",
            re.IGNORECASE
        )
        
        results = []
        for match in pattern.finditer(self.textes_concat):
            contexte_gauche = match.group(1) or ""  # Contexte gauche (peut être vide)
            motif = match.group(2) or ""  # Motif trouvé
            contexte_droit = match.group(3) or ""  # Contexte droit (peut être vide)
            results.append({
                "Contexte gauche": contexte_gauche.strip(),
                "Motif trouvé": motif.strip(),
                "Contexte droit": contexte_droit.strip(),
            })
        
        return pd.DataFrame(results)


    # Partie 2 : Fonction de nettoyage de texte
    def nettoyer_texte(self, texte):
        texte = texte.lower().replace("\n", " ")
        texte = re.sub(r'[^\w\s]', '', texte)  # Supprimer la ponctuation
        texte = re.sub(r'\d+', '', texte)  # Supprimer les chiffres
        return texte

    # Partie 2.1 : Statistiques textuelles avec élimination des stopwords
    def stats(self, n_mots=10):
        stop_words = set(stopwords.words('english'))  # Liste des stopwords en anglais
        textes_nettoyes = [self.nettoyer_texte(doc.texte) for doc in self.id2doc.values()]
        
        freq = {}
        for texte in textes_nettoyes:
            mots = re.findall(r'\w+', texte)  # Trouver tous les mots (en ignorant les caractères spéciaux)
            for mot in mots:
                if mot not in stop_words:  # Éliminer les stopwords
                    freq[mot] = freq.get(mot, 0) + 1
        
        df_freq = pd.DataFrame(list(freq.items()), columns=["Mot", "Fréquence"])
        df_freq_sorted = df_freq.sort_values(by="Fréquence", ascending=False).head(n_mots)
        print(df_freq_sorted)
        
        return df_freq_sorted

    # Partie 3 : Nuage de mots avec élimination des stopwords
    def nuage_de_mots(self):
        stop_words = set(stopwords.words('english'))  # Liste des stopwords en anglais
        textes = " ".join([doc.texte for doc in self.id2doc.values()])
        
        # Nettoyer le texte et éliminer les stopwords
        mots = re.findall(r'\w+', textes)  # Trouver tous les mots
        mots_sans_stopwords = [mot for mot in mots if mot.lower() not in stop_words]  # Filtrer les stopwords en minuscules
        
        # Création du nuage de mots
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(mots_sans_stopwords))
        
        # Affichage du nuage de mots
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()

    # Partie 4 : Analyse sentimentale avec un affichage plus clair
    def analyse_sentimentale(self):
        sentiments = []
        for doc in self.id2doc.values():
            blob = TextBlob(doc.texte)
            sentiments.append(blob.sentiment.polarity)
        
        # Moyenne des sentiments
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Interprétation du score de polarité
        if avg_sentiment > 0.1:
            sentiment_label = "Positif"
        elif avg_sentiment < -0.1:
            sentiment_label = "Négatif"
        else:
            sentiment_label = "Neutre"
        
        print(f"Analyse sentimentale moyenne du corpus : {avg_sentiment:.2f} ({sentiment_label})")