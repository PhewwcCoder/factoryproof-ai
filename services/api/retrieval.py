"""Local hybrid baseline: TF-IDF plus corpus-trained latent semantic vectors.

This is real retrieval, not a hosted embedding claim. Metadata limits candidates.
"""
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank(query: str, documents: list[dict], evidence_type: str | None = None) -> list[dict]:
    if not documents:
        return []
    texts = [' '.join(p['text'] for p in d.get('pages', [])) + ' ' + d.get('name', '') for d in documents]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return []
    q = vectorizer.transform([query.replace('_', ' ')])
    lexical = cosine_similarity(q, matrix).ravel()
    semantic = lexical.copy()
    if min(matrix.shape) > 2:
        svd = TruncatedSVD(n_components=min(8, min(matrix.shape) - 1), random_state=42)
        latent = svd.fit_transform(matrix)
        semantic = np.maximum(0, cosine_similarity(svd.transform(q), latent).ravel())
    results = []
    for i, doc in enumerate(documents):
        match = doc.get('facts', {}).get('evidence_type') == evidence_type if evidence_type else True
        if not match:
            continue
        score = float(.6 * lexical[i] + .4 * semantic[i])
        if score <= 0 and not evidence_type:
            continue
        results.append({'document': doc, 'score': round(score, 4),
                        'lexical_score': round(float(lexical[i]), 4), 'semantic_score': round(float(semantic[i]), 4)})
    return sorted(results, key=lambda item: item['score'], reverse=True)
