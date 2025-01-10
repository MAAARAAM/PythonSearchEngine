import unittest
from Corpus import Corpus, Corpus_v2
from Document import NewsAPIDocument, GuardianDocument
from SearchEngine import SearchEngine
import pandas as pd


class TestCorpus(unittest.TestCase):
    def setUp(self):
        """
        Set up test cases by initializing corpus instances and sample data.
        """
        self.corpus_v1 = Corpus("TestCorpusV1")
        self.corpus_v2 = Corpus_v2("TestCorpusV2")

        # Mocked data for testing
        self.mock_data = pd.DataFrame([
            {
                'Title': 'Test Title 1',
                'Author': 'Author 1',
                'PublishedAt': '2023-01-01',
                'Content': 'This is a test content about deep learning.',
                'Description': 'Test description',
                'type': 'newsapi'
            },
            {
                'Title': 'Test Title 2',
                'Author': 'Author 2',
                'PublishedAt': '2023-01-02',
                'Content': 'Another content about machine learning.',
                'Description': 'Another test description',
                'type': 'guardian'
            }
        ])

        for _, row in self.mock_data.iterrows():
            if row['type'] == 'newsapi':
                doc = NewsAPIDocument(
                    titre=row['Title'],
                    auteur=row['Author'],
                    date=row['PublishedAt'],
                    texte=row['Content'],
                    description=row['Description']
                )
            elif row['type'] == 'guardian':
                doc = GuardianDocument(
                    titre=row['Title'],
                    auteur=row['Author'],
                    date=row['PublishedAt'],
                    texte=row['Content'],
                    description=row['Description']
                )
            self.corpus_v1.add_document(doc)
            self.corpus_v2.add_document(doc)

    def test_add_document(self):
        """
        Test adding documents to the corpus.
        """
        self.assertEqual(len(self.corpus_v1.id2doc), len(self.mock_data))
        self.assertEqual(len(self.corpus_v2.id2doc), len(self.mock_data))

    def test_search_functionality(self):
        """
        Test search functionality in Corpus_v2.
        """
        search_engine = SearchEngine(self.corpus_v2)
        results = search_engine.search("deep learning")
        self.assertGreater(len(results), 0)

    def test_statistics(self):
        """
        Test word statistics generation in Corpus_v2.
        """
        stats = self.corpus_v2.stats(n_mots=5)
        self.assertIsNotNone(stats)

    def test_wordcloud_generation(self):
        """
        Test word cloud generation in Corpus_v2.
        """
        try:
            self.corpus_v2.nuage_de_mots()
        except Exception as e:
            self.fail(f"Word cloud generation failed: {e}")

    def test_sentiment_analysis(self):
        """
        Test sentiment analysis in Corpus_v2.
        """
        try:
            self.corpus_v2.analyse_sentimentale()
        except Exception as e:
            self.fail(f"Sentiment analysis failed: {e}")

if __name__ == "__main__":
    unittest.main()
