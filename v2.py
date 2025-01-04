import pandas as pd
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textblob import TextBlob
from nltk.corpus import stopwords
from Corpus import Corpus
from Document import NewsAPIDocument, GuardianDocument
import nltk
from Corpus import Corpus_v2

# Assurez-vous d'avoir téléchargé les stopwords de nltk
nltk.download('stopwords')

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

# Exemple de recherche et de concordance
print(corpus_v2.search('deep learning'))
print(corpus_v2.concorde('deep learning', context_size=3))

# Exemple de statistiques
corpus_v2.stats(n_mots=10)

# Affichage du nuage de mots
corpus_v2.nuage_de_mots()

# Analyse sentimentale
corpus_v2.analyse_sentimentale()
