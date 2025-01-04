import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from numpy.linalg import norm

class SearchEngine:
    def __init__(self, corpus):
        self.id2doc = corpus.id2doc  # Corpus contenant les documents
        self.ndoc = len(self.id2doc)
        self.construire_vocab()
        self.construire_matrice_TF()
        self.construire_matrice_TFxIDF()

    # Méthode pour construire le vocabulaire
    def construire_vocab(self):
        print("Construction du vocabulaire...")
        mots = set()
        for doc in self.id2doc.values():
            mots.update(set(doc.texte.lower().split()))  # Séparation par mots et suppression des doublons
        mots = sorted(mots)  # Tri des mots par ordre alphabétique
        self.vocab = {mot: {"id": i, "total_occurrences": 0, "doc_count": 0} for i, mot in enumerate(mots)}
        print(f"Vocabulaire construit : {len(self.vocab)} mots uniques")
        print("Vocabulaire terminé.\n")

    # Méthode pour construire la matrice TF
    def construire_matrice_TF(self):
        print("Construction de la matrice TF...")
        rows, cols, data = [], [], []
        for i, doc in self.id2doc.items():
            word_counts = {}
            for word in doc.texte.lower().split():  # Comptage des mots dans chaque document
                if word in self.vocab:
                    word_counts[word] = word_counts.get(word, 0) + 1
            for word, count in word_counts.items():
                word_id = self.vocab[word]["id"]
                rows.append(i - 1)  # Lignes correspondant aux documents
                cols.append(word_id)  # Colonnes correspondant aux mots
                data.append(count)  # Fréquence du terme
                self.vocab[word]["total_occurrences"] += count  # Mise à jour des occurrences
                self.vocab[word]["doc_count"] += 1  # Mise à jour des documents contenant le mot

        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(self.ndoc, len(self.vocab)))
        print(f"Matrice TF construite. Dimensions : {self.mat_TF.shape}")
        print(f"Exemple de valeurs TF pour le premier document : {self.mat_TF[0].toarray()}\n")

    # Méthode pour construire la matrice TFxIDF
    def construire_matrice_TFxIDF(self):
        print("Construction de la matrice TFxIDF...")
        N = self.ndoc  # Nombre total de documents
        idf = np.log(N / (1 + np.array([self.vocab[word]["doc_count"] for word in self.vocab])))  # Calcul de l'IDF

        rows, cols, data = [], [], []
        for i, doc in self.id2doc.items():
            word_counts = {word: doc.texte.lower().split().count(word) for word in set(doc.texte.lower().split()) if word in self.vocab}
            for word, count in word_counts.items():
                word_id = self.vocab[word]["id"]
                tf = count
                tf_idf = tf * idf[word_id]  # Calcul du TF-IDF
                rows.append(i - 1)
                cols.append(word_id)
                data.append(tf_idf)

        self.mat_TFxIDF = csr_matrix((data, (rows, cols)), shape=(self.ndoc, len(self.vocab)))
        print(f"Matrice TFxIDF construite. Dimensions : {self.mat_TFxIDF.shape}")
        print(f"Exemple de valeurs TFxIDF pour le premier document : {self.mat_TFxIDF[0].toarray()}\n")

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
