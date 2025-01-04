from dateutil import parser
from datetime import datetime

class Document:
    def __init__(self, titre, auteur, date, texte, doc_type="generic"):
        self.titre = titre
        self.auteur = auteur
        self.texte = texte
        self.type = doc_type
        try:
            if date and date != 'No date available':
                self.date = parser.isoparse(date).replace(tzinfo=None)
            else:
                self.date = None
        except Exception as e:
            print(f"Erreur lors de l'analyse de la date : {e}")
            self.date = None

    def afficher_informations(self):
        print(f'Titre : {self.titre}')
        print(f'Auteur : {self.auteur}')
        print(f'Date : {self.date.strftime("%Y-%m-%d") if self.date else "Inconnue"}')
        print(f'Texte : {self.texte[:100]}...')  # Afficher les 100 premiers caractères du texte

    def __str__(self):
        return f"Document(titre={self.titre})"

    def getType(self):
        return self.type

class NewsAPIDocument(Document):
    def __init__(self, titre, auteur, date, texte, description):
        super().__init__(titre, auteur, date, texte, doc_type="newsapi")
        self.description = description

    def __str__(self):
        return f"NewsAPIDocument(titre={self.titre}, auteur={self.auteur}, date={self.date}, description={self.description})"

class GuardianDocument(Document):
    def __init__(self, titre, auteur, date, texte, description):
        super().__init__(titre, auteur, date, texte, doc_type="guardian")
        self.description = description

    def __str__(self):
        return f"GuardianDocument(titre={self.titre}, auteur={self.auteur}, date={self.date}, description={self.description})"