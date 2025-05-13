import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ✅ This must be the first Streamlit command
st.set_page_config(page_title="🎬 IMDb Recommender", layout="wide")

# --- Load and Prepare Data ---
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Clean column names
    df = df.dropna(subset=["Movie Name", "Storyline"])
    return df

def compute_similarity(df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['Storyline'])
    similarity = cosine_similarity(tfidf_matrix)
    return tfidf, tfidf_matrix, similarity

def recommend_movies(title, df, similarity, top_n=5):
    if title not in df['Movie Name'].values:
        return ["❌ Movie not found in dataset."]
    
    idx = df[df['Movie Name'] == title].index[0]
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    recommended_titles = [df.iloc[i[0]]['Movie Name'] for i in sim_scores]
    return recommended_titles

# --- Load data and compute similarity ---
df = load_data("movies_2024.csv")
tfidf, tfidf_matrix, similarity = compute_similarity(df)

# --- Streamlit UI ---
st.title("🎬 IMDb Movie Recommender System")

tab1, tab2 = st.tabs(["📜 Recommend by Storyline", "🎞️ Recommend by Movie Title"])

# --- Tab 1: Storyline Input ---
with tab1:
    st.subheader("Enter a Movie Storyline:")
    user_input = st.text_area("Paste a movie plot here", height=150)

    if st.button("Recommend Based on Storyline"):
        if user_input.strip():
            input_vec = tfidf.transform([user_input])
            sim_scores = cosine_similarity(input_vec, tfidf_matrix).flatten()
            top_indices = sim_scores.argsort()[-5:][::-1]
            results = df.iloc[top_indices]

            st.subheader("Recommended Movies:")
            for _, row in results.iterrows():
                st.markdown(f"**🎬 {row['Movie Name']}**")
                st.write(row['Storyline'])
                st.markdown("---")
        else:
            st.warning("⚠️ Please enter a valid storyline.")

# --- Tab 2: Title Dropdown Input ---
with tab2:
    st.subheader("Select a Movie Title:")
    selected_title = st.selectbox("Choose a movie to find similar ones:", df['Movie Name'].unique())

    if st.button("Recommend Based on Title"):
        recommendations = recommend_movies(selected_title, df, similarity)
        st.subheader(f"Movies similar to '{selected_title}':")
        for title in recommendations:
            st.markdown(f"➡️ {title}")
