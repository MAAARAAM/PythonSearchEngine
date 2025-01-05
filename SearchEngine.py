import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from numpy.linalg import norm

class SearchEngine:
    """
    Une classe pour implémenter un moteur de recherche basé sur la similarité cosinus
    et les matrices TF et TF-IDF.

    Attributes:
        corpus (Corpus): Le corpus contenant les documents.
        vocab (dict): Le vocabulaire contenant les mots et leurs informations.
        total_occurrences (dict): Le nombre total d'occurrences des mots.
        doc_count (dict): Le nombre de documents contenant chaque mot.
        ndoc (int): Le nombre total de documents dans le corpus.
        mat_TF (csr_matrix): La matrice des fréquences des termes (TF).
        mat_TFxIDF (csr_matrix): La matrice des fréquences pondérées par IDF (TF-IDF).
    """

    def __init__(self, corpus):
        """
        Initialise le moteur de recherche avec un corpus donné et construit les matrices nécessaires.

        Args:
            corpus (Corpus): Le corpus contenant les documents.
        """
        self.corpus = corpus
        self.vocab = {}
        self.total_occurrences = {}
        self.doc_count = {}
        self.ndoc = len(self.corpus.id2doc)

        self.construire_vocab()
        self.construire_matrice_TF()
        self.construire_matrice_TFxIDF()

    def construire_vocab(self):
        """
        Construit le vocabulaire à partir des textes des documents dans le corpus.
        """
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

    def construire_matrice_TF(self):
        """
        Construit la matrice des fréquences des termes (TF) pour le corpus.
        """
        rows, cols, data = [], [], []
        for doc_id, doc in enumerate(self.corpus.id2doc.values()):
            for word in doc.texte.split():
                word = word.lower().strip()
                if word in self.vocab:
                    word_index = self.vocab[word]["id"]
                    rows.append(doc_id)
                    cols.append(word_index)
                    data.append(1)

        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(self.ndoc, len(self.vocab)))
        print(f"Matrice TF construite. Dimensions : {self.mat_TF.shape}")

    def construire_matrice_TFxIDF(self):
        """
        Construit la matrice TF-IDF pour le corpus.
        """
        print("Construction de la matrice TFxIDF...")
        N = self.ndoc
        idf = np.log(N / (1 + np.array([self.vocab[word]["doc_count"] for word in self.vocab])))

        rows, cols, data = [], [], []
        for doc_id, doc in self.corpus.id2doc.items():
            word_counts = {
                word: doc.texte.lower().split().count(word)
                for word in set(doc.texte.lower().split()) if word in self.vocab
            }
            for word, count in word_counts.items():
                word_id = self.vocab[word]["id"]
                tf = count
                tf_idf = tf * idf[word_id]
                rows.append(doc_id)
                cols.append(word_id)
                data.append(tf_idf)

        self.mat_TFxIDF = csr_matrix((data, (rows, cols)), shape=(self.ndoc, len(self.vocab)))
        print(f"Matrice TFxIDF construite. Dimensions : {self.mat_TFxIDF.shape}")

    def _calculer_similarite_cosinus(self, vecteur_requete):
        """
        Calcule la similarité cosinus entre une requête et tous les documents.

        Args:
            vecteur_requete (numpy.array): Le vecteur représentant la requête.

        Returns:
            numpy.array: Les similarités cosinus pour chaque document.
        """
        mat_TFxIDF_dense = self.mat_TFxIDF.toarray()
        produit_scalaire = mat_TFxIDF_dense.dot(vecteur_requete)
        norme_documents = np.linalg.norm(mat_TFxIDF_dense, axis=1)
        norme_requete = norm(vecteur_requete)
        similarites = produit_scalaire / (norme_documents * norme_requete + 1e-10)
        return similarites

    def search(self, mots_clefs, n_documents=10):
        """
        Effectue une recherche basée sur une requête de mots-clés.

        Args:
            mots_clefs (str): La requête contenant les mots-clés.
            n_documents (int): Le nombre maximum de documents à retourner.

        Returns:
            pandas.DataFrame: Un DataFrame contenant les documents les plus pertinents et leurs similarités.
        """
        mots_clefs = [mot.lower() for mot in mots_clefs.split()]
        vecteur_requete = np.zeros(len(self.vocab))

        for mot in mots_clefs:
            if mot in self.vocab:
                vecteur_requete[self.vocab[mot]["id"]] = 1

        similarites = self._calculer_similarite_cosinus(vecteur_requete)
        indices = np.argsort(similarites)[::-1][:n_documents]
        resultats = [(i, similarites[i]) for i in indices]

        df_resultats = pd.DataFrame(resultats, columns=["Document", "Similarité"])
        return df_resultats
