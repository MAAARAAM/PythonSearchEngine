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
    """
    Classe représentant un corpus de documents.
    Permet de gérer un ensemble de documents et d'effectuer diverses opérations,
    telles que l'ajout de documents, la récupération de données depuis des API externes,
    l'affichage trié des documents, et l'exportation vers des fichiers.
    """

    def __init__(self, nom):
        """
        Initialise un nouvel objet Corpus.

        Args:
            nom (str): Le nom du corpus.
        """
        self.nom = nom
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

    def add_document(self, doc):
        """
        Ajoute un document au corpus.

        Args:
            doc (Document): L'objet Document à ajouter.
        """
        doc_id = self.ndoc
        self.id2doc[doc_id] = doc
        self.ndoc += 1

        if doc.auteur not in self.authors:
            self.authors[doc.auteur] = Author(doc.auteur)
            self.naut += 1
        self.authors[doc.auteur].add_document(doc_id, doc)

    def fetch_newsapi_data(self, query, page_size=100):
        """
        Récupère les données depuis l'API NewsAPI.

        Args:
            query (str): La requête de recherche.
            page_size (int): Le nombre maximum d'articles à récupérer (par défaut 100).

        Returns:
            pd.DataFrame: Un DataFrame contenant les articles récupérés.
        """
        api_key = '00f6a1632dd94bd5ba33be1df3a5cdc9'
        url = f'https://newsapi.org/v2/everything?q={query}&pageSize={page_size}&apiKey={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            data = [
                {
                    'Author': article.get('author', 'No author available'),
                    'Title': article.get('title', 'No title available'),
                    'Description': article.get('description', 'No description available'),
                    'PublishedAt': article.get('publishedAt', 'No date available'),
                    'Content': article.get('content', 'No content available')
                }
                for article in articles
            ]
            return pd.DataFrame(data)
        else:
            print(f"Failed to fetch data from NewsAPI: {response.status_code} - {response.text}")
            return pd.DataFrame()

    def fetch_guardian_data(self, query, page_size=100):
        """
        Récupère les données depuis l'API The Guardian.

        Args:
            query (str): La requête de recherche.
            page_size (int): Le nombre maximum d'articles à récupérer (par défaut 100).

        Returns:
            pd.DataFrame: Un DataFrame contenant les articles récupérés.
        """
        api_key = '7c313d58-2e49-439f-a5cf-57b6e65a95fb'
        url = f'https://content.guardianapis.com/search?q={query}&page-size={page_size}&api-key={api_key}&show-fields=all'
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get('response', {}).get('results', [])
            data = [
                {
                    'Author': article.get('fields', {}).get('byline', 'No author available'),
                    'Title': article.get('webTitle', 'No title available'),
                    'Description': article.get('fields', {}).get('trailText', 'No description available'),
                    'PublishedAt': article.get('webPublicationDate', 'No date available'),
                    'Content': article.get('fields', {}).get('bodyText', 'No content available'),
                    'URL': article.get('webUrl', 'No URL available')
                }
                for article in articles
            ]
            return pd.DataFrame(data)
        else:
            print(f"Failed to fetch data from The Guardian: {response.status_code} - {response.text}")
            return pd.DataFrame()

    def afficher_documents_tries_par_date(self, n):
        """
        Affiche les documents triés par date, de la plus récente à la plus ancienne.

        Args:
            n (int): Le nombre de documents à afficher.
        """
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: x.date or datetime.min, reverse=True)[:n]
        for doc in sorted_docs:
            doc.afficher_informations()

    def afficher_documents_tries_par_titre(self, n):
        """
        Affiche les documents triés par titre (ordre alphabétique).

        Args:
            n (int): Le nombre de documents à afficher.
        """
        sorted_docs = sorted(self.id2doc.values(), key=lambda x: x.titre)[:n]
        for doc in sorted_docs:
            doc.afficher_informations()

    def __repr__(self):
        """
        Représentation textuelle de l'objet Corpus.

        Returns:
            str: Une chaîne représentant l'objet.
        """
        return f"Corpus(nom={self.nom}, ndoc={self.ndoc}, naut={self.naut})"

    def save(self, filepath):
        """
        Sauvegarde le corpus dans un fichier pickle.

        Args:
            filepath (str): Le chemin du fichier où sauvegarder le corpus.
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def export_to_json(self, filepath):
        """
        Exporte le corpus dans un fichier JSON.

        Args:
            filepath (str): Le chemin du fichier où exporter le corpus.
        """
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
        """
        Charge un corpus depuis un fichier pickle.

        Args:
            filepath (str): Le chemin du fichier à charger.

        Returns:
            Corpus: L'objet Corpus chargé.
        """
        print(f"Chargement du corpus depuis le fichier: {filepath}")
        with open(filepath, 'rb') as f:
            corpus = pickle.load(f)
        print("Chargement terminé")
        return corpus
    
class Corpus_v2(Corpus):
    """
    Une version étendue de la classe Corpus pour inclure des fonctionnalités supplémentaires 
    telles que la recherche avec expressions régulières, les statistiques textuelles, le nuage de mots, 
    et l'analyse sentimentale.
    """

    def __init__(self, nom):
        """
        Initialise un nouveau corpus.

        Args:
            nom (str): Le nom du corpus.
        """
        super().__init__(nom)
        self.textes_concat = ""

    def search(self, keyword):
        """
        Recherche les passages contenant un mot-clé dans le corpus.

        Args:
            keyword (str): Le mot-clé à rechercher.

        Returns:
            list: Une liste des passages contenant le mot-clé.
        """
        if not self.textes_concat:
            self.textes_concat = " ".join([doc.texte for doc in self.id2doc.values()])
        pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
        passages = [match.group(0) for match in pattern.finditer(self.textes_concat)]
        return passages

    def concorde(self, expression, context_size=5):
        """
        Crée un concordancier pour une expression donnée.

        Args:
            expression (str): L'expression à chercher.
            context_size (int): Le nombre de mots de contexte à afficher avant et après l'expression.

        Returns:
            pd.DataFrame: Un tableau contenant le contexte gauche, le motif trouvé et le contexte droit.
        """
        if not self.textes_concat:
            self.textes_concat = " ".join([doc.texte for doc in self.id2doc.values()])
        pattern = re.compile(
            r"(\S+\s){0," + str(context_size) + r"}(\b" + re.escape(expression) + r"\b)(\s\S+){0," + str(context_size) + r"}",
            re.IGNORECASE
        )
        results = []
        for match in pattern.finditer(self.textes_concat):
            contexte_gauche = match.group(1) or ""
            motif = match.group(2) or ""
            contexte_droit = match.group(3) or ""
            results.append({
                "Contexte gauche": contexte_gauche.strip(),
                "Motif trouvé": motif.strip(),
                "Contexte droit": contexte_droit.strip(),
            })
        return pd.DataFrame(results)

    def nettoyer_texte(self, texte):
        """
        Nettoie un texte en supprimant la ponctuation, les chiffres et en le mettant en minuscules.

        Args:
            texte (str): Le texte à nettoyer.

        Returns:
            str: Le texte nettoyé.
        """
        texte = texte.lower().replace("\n", " ")
        texte = re.sub(r'[^\w\s]', '', texte)
        texte = re.sub(r'\d+', '', texte)
        return texte

    def stats(self, n_mots=10):
        """
        Calcule les statistiques textuelles du corpus.

        Args:
            n_mots (int): Le nombre de mots les plus fréquents à afficher.

        Returns:
            pd.DataFrame: Un tableau contenant les mots les plus fréquents et leur fréquence.
        """
        stop_words = set(stopwords.words('english'))
        textes_nettoyes = [self.nettoyer_texte(doc.texte) for doc in self.id2doc.values()]
        freq = {}
        for texte in textes_nettoyes:
            mots = re.findall(r'\w+', texte)
            for mot in mots:
                if mot not in stop_words:
                    freq[mot] = freq.get(mot, 0) + 1
        df_freq = pd.DataFrame(list(freq.items()), columns=["Mot", "Fréquence"])
        df_freq_sorted = df_freq.sort_values(by="Fréquence", ascending=False).head(n_mots)
        print(df_freq_sorted)
        return df_freq_sorted

    def nuage_de_mots(self):
        """
        Génère et affiche un nuage de mots basé sur le contenu du corpus.
        """
        stop_words = set(stopwords.words('english'))
        textes = " ".join([doc.texte for doc in self.id2doc.values()])
        mots = re.findall(r'\w+', textes)
        mots_sans_stopwords = [mot for mot in mots if mot.lower() not in stop_words]
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(mots_sans_stopwords))
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()

    def analyse_sentimentale(self):
        """
        Effectue une analyse sentimentale sur le corpus et affiche la polarité moyenne.
        """
        sentiments = []
        for doc in self.id2doc.values():
            blob = TextBlob(doc.texte)
            sentiments.append(blob.sentiment.polarity)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        if avg_sentiment > 0.1:
            sentiment_label = "Positif"
        elif avg_sentiment < -0.1:
            sentiment_label = "Négatif"
        else:
            sentiment_label = "Neutre"
        print(f"Analyse sentimentale moyenne du corpus : {avg_sentiment:.2f} ({sentiment_label})")

    def afficher_documents_tries_par_titre(self, n=None):
        """
        Retourne les documents triés par titre.

        Args:
            n (int): Le nombre de documents à retourner. Si None, retourne tous les documents.

        Returns:
            list: Liste des documents triés par titre.
        """
        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.titre or "")
        return sorted_docs[:n] if n else sorted_docs

    def afficher_documents_tries_par_date(self, n=None):
        """
        Retourne les documents triés par date.

        Args:
            n (int): Le nombre de documents à retourner. Si None, retourne tous les documents.

        Returns:
            list: Liste des documents triés par date.
        """
        sorted_docs = sorted(self.id2doc.values(), key=lambda doc: doc.date or datetime.min, reverse=True)
        return sorted_docs[:n] if n else sorted_docs
