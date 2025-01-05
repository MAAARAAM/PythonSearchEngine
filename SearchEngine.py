import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from numpy.linalg import norm

class SearchEngine:

    def __init__(self, corpus):
        self.corpus = corpus  # Initialiser le corpus
        self.vocab = {}
        self.total_occurrences = {}
        self.doc_count = {}
        self.ndoc = len(self.corpus.id2doc)

        # Construire le vocabulaire et les matrices
        self.construire_vocab()
        self.construire_matrice_TF()
        self.construire_matrice_TFxIDF()

    # Méthode pour construire le vocabulaire
    def construire_vocab(self):
        vocab = {}
        for doc in self.corpus.id2doc.values():
            seen_in_doc = set()
            for word in doc.texte.split():
                word = word.lower().strip()
                if word not in vocab:
                    vocab[word] = {"id": len(vocab), "doc_count": 0, "total_occurrences": 0}
                vocab[word]["total_occurrences"] += 1
                if word not in seen_in_doc:
                    seen_in_doc.add(word)
                    vocab[word]["doc_count"] += 1

        self.vocab = vocab


    # Méthode pour construire la matrice TF
    from scipy.sparse import csr_matrix

    def construire_matrice_TF(self):
        rows, cols, data = [], [], []
        for doc_id, doc in enumerate(self.corpus.id2doc.values()):
            for word in doc.texte.split():
                word = word.lower().strip()  # Normalisation des mots
                if word in self.vocab:
                    word_index = self.vocab[word]["id"]  # Obtenir l'indice du mot (entier)
                    rows.append(doc_id)  # ID du document
                    cols.append(word_index)  # Indice du mot (entier)
                    data.append(1)  # Compte une occurrence
                else:
                    print(f"Mot hors vocabulaire ignoré : {word}")

        # Vérifications avant création de la matrice
        if any(r < 0 for r in rows) or any(c < 0 for c in cols):
            raise ValueError("Indices négatifs détectés dans rows ou cols.")

        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(self.ndoc, len(self.vocab)))
        print(f"Matrice TF construite. Dimensions : {self.mat_TF.shape}")


    # Méthode pour construire la matrice TFxIDF
    def construire_matrice_TFxIDF(self):
        print("Construction de la matrice TFxIDF...")
        N = self.ndoc  # Nombre total de documents
        idf = np.log(N / (1 + np.array([self.vocab[word]["doc_count"] for word in self.vocab])))  # Calcul de l'IDF

        rows, cols, data = [], [], []
        for doc_id, doc in self.corpus.id2doc.items():
            word_counts = {word: doc.texte.lower().split().count(word) for word in set(doc.texte.lower().split()) if word in self.vocab}
            for word, count in word_counts.items():
                word_id = self.vocab[word]["id"]
                tf = count
                tf_idf = tf * idf[word_id]  # Calcul du TF-IDF
                rows.append(doc_id)
                cols.append(word_id)
                data.append(tf_idf)

        self.mat_TFxIDF = csr_matrix((data, (rows, cols)), shape=(self.ndoc, len(self.vocab)))
        print(f"Matrice TFxIDF construite. Dimensions : {self.mat_TFxIDF.shape}")


    # Méthode pour calculer la similarité cosinus
    def _calculer_similarite_cosinus(self, vecteur_requete):
        mat_TFxIDF_dense = self.mat_TFxIDF.toarray()
        produit_scalaire = mat_TFxIDF_dense.dot(vecteur_requete)  # Produit scalaire entre la requête et chaque document
        norme_documents = np.linalg.norm(mat_TFxIDF_dense, axis=1)  # Normes des documents
        norme_requete = norm(vecteur_requete)  # Norme de la requête
        similarites = produit_scalaire / (norme_documents * norme_requete + 1e-10)  # Calcul de la similarité cosinus
        return similarites

    # Méthode pour effectuer une recherche
    def search(self, mots_clefs, n_documents=10):
        mots_clefs = [mot.lower() for mot in mots_clefs.split()]  # Traitement de la requête
        vecteur_requete = np.zeros(len(self.vocab))
        
        for mot in mots_clefs:
            if mot in self.vocab:
                vecteur_requete[self.vocab[mot]["id"]] = 1  # Remplir le vecteur de la requête avec 1 si le mot est présent
        
        similarites = self._calculer_similarite_cosinus(vecteur_requete)
        
        # Récupération des indices des documents les plus similaires
        indices = np.argsort(similarites)[::-1][:n_documents]  # Trie par similarité décroissante
        resultats = [(i, similarites[i]) for i in indices]
        
        # Création du DataFrame de résultats
        df_resultats = pd.DataFrame(resultats, columns=["Document", "Similarité"])
        return df_resultats
