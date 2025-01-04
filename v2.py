import pandas as pd
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from nltk.corpus import stopwords
from Corpus import Corpus
from Document import NewsAPIDocument, GuardianDocument
import nltk

# Assurez-vous d'avoir téléchargé les stopwords de nltk
nltk.download('stopwords')

# Classe Corpus_v2 modifiée
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
        pattern = re.compile(r"(\S*\s){0," + str(context_size) + r"}" + re.escape(expression) + r"(\s\S*){0," + str(context_size) + r"}", re.IGNORECASE)
        concordances = [match.group(0) for match in pattern.finditer(self.textes_concat)]
        df_concordance = pd.DataFrame(concordances, columns=["Concordance"])
        return df_concordance

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

# Exemple d'utilisation
corpus_v2 = Corpus_v2("MonCorpusV2")

# Exemple d'ajout de documents et récupération de données
newsapi_data = corpus_v2.fetch_newsapi_data('deep learning', page_size=100)
newsapi_data['type'] = 'newsapi'

guardian_data = corpus_v2.fetch_guardian_data('deep learning', page_size=100)
guardian_data['type'] = 'guardian'

# Combinez les données
combined_data = pd.concat([newsapi_data, guardian_data], ignore_index=True)

# Ajoutez des documents au corpus
for index, row in combined_data.iterrows():
    if row['type'] == 'newsapi':
        doc = NewsAPIDocument(
            titre=row.get('Title', 'No title available'),
            auteur=row.get('Author', 'No author available'),
            date=row.get('PublishedAt', 'No date available'),
            url=row.get('URL', 'No URL available'),
            texte=row.get('Content', 'No content available'),
            description=row.get('Description', 'No description available')
        )
    elif row['type'] == 'guardian':
        doc = GuardianDocument(
            titre=row.get('Title', 'No title available'),
            auteur=row.get('Author', 'No author available'),
            date=row.get('PublishedAt', 'No date available'),
            url=row.get('URL', 'No URL available'),
            texte=row.get('Content', 'No content available'),
            description=row.get('Description', 'No description available')
        )
    corpus_v2.add_document(doc)

# Exemple de recherche et de concordance
print(corpus_v2.search('deep learning'))
print(corpus_v2.concorde('deep learning', context_size=3))

# Exemple de statistiques
corpus_v2.stats(n_mots=10)

# Affichage du nuage de mots
corpus_v2.nuage_de_mots()

# Analyse sentimentale
corpus_v2.analyse_sentimentale()
