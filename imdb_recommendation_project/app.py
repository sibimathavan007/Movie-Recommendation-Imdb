import streamlit as st
import pandas as pd
from recommendation import load_data, compute_similarity, recommend_movies

st.title("🎬 IMDb Movie Recommendation System (2024)")

file_path = r"C:/Users/HP/Downloads/imdb_recommendation_project/movies_2024.csv"
df = load_data(file_path)
similarity = compute_similarity(df)

selected_movie = st.selectbox("Select a movie to get recommendations:", df['Movie Name'].unique())

if st.button("Recommend"):
    recommendations = recommend_movies(selected_movie, df, similarity)
    st.subheader("📽 Recommended Movies:")
    for movie in recommendations:
        st.write(f"- {movie}")
