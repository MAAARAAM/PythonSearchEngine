class Author:
    """
    Classe représentant un auteur et ses documents associés.

    Attributs :
    name (str) : Le nom de l'auteur.
    ndoc (int) : Le nombre de documents associés à l'auteur.
    production (dict) : Un dictionnaire contenant les documents de l'auteur, où la clé est l'ID du document et la valeur est le document lui-même.
    """
    def __init__(self, name):
        """
        Initialise un auteur avec son nom.

        Arguments :
        name (str) : Le nom de l'auteur.
        """
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add_document(self, doc_id, document):
        """
        Ajoute un document à la production de l'auteur.

        Arguments :
        doc_id (str) : L'ID du document.
        document (Document) : L'objet document à ajouter.
        """
        self.production[doc_id] = document
        self.ndoc += 1

    def average_document_length(self):
        """
        Calcule la longueur moyenne des documents de l'auteur.

        Retour :
        float : La taille moyenne des documents en caractères. Retourne 0 si l'auteur n'a pas de documents.
        """
        if self.ndoc == 0:
            return 0
        return sum(len(doc.texte) for doc in self.production.values()) / self.ndoc

    def afficher_informations(self):
        """
        Affiche les informations sur l'auteur : son nom, le nombre de documents, et la taille moyenne des documents.
        """
        print(f'Auteur : {self.name}')  
        print(f'Nombre de documents : {self.ndoc}')
        print(f'Taille moyenne des documents : {self.average_document_length():.2f} caractères')

    def __str__(self):
        """
        Retourne une représentation sous forme de chaîne de caractères de l'auteur.

        Retour :
        str : La chaîne représentant l'auteur avec le nombre de documents associés.
        """
        return f'{self.name} ({self.ndoc} documents)'
