from dateutil import parser
from datetime import datetime

class Document:
    """
    Classe représentant un document générique.
    
    Attributs :
    titre (str) : Le titre du document.
    auteur (str) : L'auteur du document.
    date (datetime) : La date de publication du document.
    texte (str) : Le contenu du document.
    type (str) : Le type de document (par défaut "generic").
    """
    def __init__(self, titre, auteur, date, texte, doc_type="generic"):
        """
        Initialise un document avec les informations spécifiées.
        
        Arguments :
        titre (str) : Le titre du document.
        auteur (str) : L'auteur du document.
        date (str) : La date de publication sous forme de chaîne ISO.
        texte (str) : Le contenu du document.
        doc_type (str) : Le type du document (par défaut "generic").
        """
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
        """
        Affiche les informations principales du document (titre, auteur, date, extrait du texte).
        """
        print(f'Titre : {self.titre}')
        print(f'Auteur : {self.auteur}')
        print(f'Date : {self.date.strftime("%Y-%m-%d") if self.date else "Inconnue"}')
        print(f'Texte : {self.texte[:100]}...')  # Afficher les 100 premiers caractères du texte
        print("-" * 50)

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères du document.
        
        Retour :
        str : La chaîne représentant le document.
        """
        return f"Document(titre={self.titre})"

    def getType(self):
        """
        Retourne le type du document.
        
        Retour :
        str : Le type du document.
        """
        return self.type

class NewsAPIDocument(Document):
    """
    Classe représentant un document provenant de NewsAPI.
    
    Attributs supplémentaires :
    description (str) : Une description du document.
    """
    def __init__(self, titre, auteur, date, texte, description):
        """
        Initialise un document NewsAPI avec les informations spécifiées.
        
        Arguments :
        titre (str) : Le titre du document.
        auteur (str) : L'auteur du document.
        date (str) : La date de publication sous forme de chaîne ISO.
        texte (str) : Le contenu du document.
        description (str) : La description du document.
        """
        super().__init__(titre, auteur, date, texte, doc_type="newsapi")
        self.description = description

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères du document NewsAPI.
        
        Retour :
        str : La chaîne représentant le document NewsAPI.
        """
        return f"NewsAPIDocument(titre={self.titre}, auteur={self.auteur}, date={self.date}, description={self.description})"

class GuardianDocument(Document):
    """
    Classe représentant un document provenant du Guardian.
    
    Attributs supplémentaires :
    description (str) : Une description du document.
    """
    def __init__(self, titre, auteur, date, texte, description):
        """
        Initialise un document Guardian avec les informations spécifiées.
        
        Arguments :
        titre (str) : Le titre du document.
        auteur (str) : L'auteur du document.
        date (str) : La date de publication sous forme de chaîne ISO.
        texte (str) : Le contenu du document.
        description (str) : La description du document.
        """
        super().__init__(titre, auteur, date, texte, doc_type="guardian")
        self.description = description

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères du document Guardian.
        
        Retour :
        str : La chaîne représentant le document Guardian.
        """
        return f"GuardianDocument(titre={self.titre}, auteur={self.auteur}, date={self.date}, description={self.description})"
