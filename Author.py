class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add_document(self, doc_id, document):
        self.production[doc_id] = document
        self.ndoc += 1

    def average_document_length(self):
        if self.ndoc == 0:
            return 0
        return sum(len(doc.texte) for doc in self.production.values()) / self.ndoc

    def afficher_informations(self):
        print(f'Auteur : {self.name}')  
        print(f'Nombre de documents : {self.ndoc}')
        print(f'Taille moyenne des documents : {self.average_document_length():.2f} caractères')

    def __str__(self):
        return f'{self.name} ({self.ndoc} documents)'