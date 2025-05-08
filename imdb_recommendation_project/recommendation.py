import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna()
    return df

def compute_similarity(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['Storyline'])
    similarity = cosine_similarity(tfidf_matrix)
    return similarity

def recommend_movies(title, df, similarity, top_n=5):
    if title not in df['Movie Name'].values:
        return ["❌ Movie not found in dataset."]
    
    idx = df[df['Movie Name'] == title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommended_titles = [df.iloc[i[0]]['Movie Name'] for i in sim_scores]
    return recommended_titles
