
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import joblib
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Téléchargement des ressources NLTK nécessaires
nltk.download('stopwords')
nltk.download('wordnet')

# Configuration des stopwords
stop_words_en = set(stopwords.words('english'))
stop_words_fr = set(stopwords.words('french'))
stop_words = stop_words_en.union(stop_words_fr)

lemmatizer = WordNetLemmatizer()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Système de Recommandation de Journaux",
    page_icon="📚",
    layout="wide"
)

# Fonctions de prétraitement du texte
def clean_text(text):
    if isinstance(text, str):
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = text.strip()
        return text
    return ""

def remove_stopwords(text):
    words = text.split()
    meaningful_words = [word for word in words if word not in stop_words]
    return ' '.join(meaningful_words)

def lemmatize_text(text):
    words = text.split()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(lemmatized_words)

# Interface principale
def main():
    st.title("🎓 Système de Recommandation de Journaux Académiques")
    
    # Création de colonnes pour une meilleure mise en page
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Informations sur votre article")
        titre = st.text_input("Titre de l'article", key="titre")
        resume = st.text_area("Résumé (Abstract)", key="resume")
        mots_cles = st.text_input("Mots-clés (séparés par des virgules)", key="mots_cles")

    with col2:
        st.subheader("ℹ️ Comment ça marche")
        st.info("""
        1. Entrez les informations de votre article
        2. Le système analysera votre texte
        3. Vous recevrez deux types de recommandations :
           - Basées sur le score SJR
           - Basées sur la similarité du contenu
        """)

    if st.button("🔍 Trouver des journaux recommandés"):
        if titre and resume and mots_cles:
            with st.spinner("Analyse en cours..."):
                try:
                    # Prétraitement du texte avec les nouvelles fonctions
                    texte_combine = f"{titre} {resume} {mots_cles}"
                    texte_traite = clean_text(texte_combine)
                    texte_traite = remove_stopwords(texte_traite)
                    texte_traite = lemmatize_text(texte_traite)

                    # Chargement des modèles
                    tfidf = joblib.load('Tokenizers/tfidf_vectorizer.joblib')
                    kmeans = joblib.load('Models/kmeans_model.joblib')

                    # Transformation et prédiction
                    vecteur = tfidf.transform([texte_traite])
                    cluster_num = kmeans.predict(vecteur)[0]

                    # Affichage des résultats
                    st.success("✅ Analyse terminée !")

                    st.subheader("📊 Recommandations")
                    tab1, tab2 = st.tabs(["Par score SJR", "Par similarité"])

                    df = pd.read_csv('data/df_clustering.csv')
                    with tab1:
                        st.subheader("📈 Recommandations par score SJR")
                        same_cluster_df = df[df['cluster'] == cluster_num].copy()
                        same_cluster_df['sjr_score'] = pd.to_numeric(same_cluster_df['sjr_score'], errors='coerce')
                        same_cluster_df = same_cluster_df.dropna(subset=['sjr_score'])
                        
                        # Garder uniquement les journaux uniques avec le score SJR le plus élevé
                        top_10_high_sjr = (same_cluster_df.sort_values(by='sjr_score', ascending=False)
                                          .drop_duplicates(subset=['journal_name'])
                                          .head(10))

                        # Style CSS pour les cards
                        st.markdown("""
                        <style>
                            .journal-card {
                                background-color: #ffffff;
                                border-radius: 10px;
                                padding: 20px;
                                margin: 10px 0;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                border-left: 5px solid #1E88E5;
                                transition: transform 0.2s ease-in-out;
                            }
                            .journal-card:hover {
                                transform: translateX(10px);
                                box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
                            }
                            .journal-name {
                                color: #1E88E5;
                                font-size: 1.2em;
                                font-weight: bold;
                                margin-bottom: 10px;
                            }
                            .sjr-score {
                                background-color: #f0f7ff;
                                padding: 8px 15px;
                                border-radius: 20px;
                                display: inline-block;
                                color: #1E88E5;
                                font-weight: bold;
                            }
                            .rank-badge {
                                background-color: #1E88E5;
                                color: white;
                                padding: 5px 10px;
                                border-radius: 15px;
                                font-size: 0.9em;
                                float: right;
                            }
                        </style>
                        """, unsafe_allow_html=True)

                        # Affichage des cards
                        for idx, (_, journal) in enumerate(top_10_high_sjr.iterrows(), 1):
                            card_html = f"""
                            <div class="journal-card">
                                <div class="rank-badge">Rang #{idx}</div>
                                <div class="journal-name">{journal['journal_name']}</div>
                                <div class="sjr-score">Score SJR: {journal['sjr_score']:.3f}</div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)

                    with tab2:
                        st.subheader("🔍 Recommandations par similarité")
                        same_cluster_df['combined_text'] = (
                            same_cluster_df['title'] + ' ' +
                            same_cluster_df['abstract'] + ' ' +
                            same_cluster_df['author_keywords']
                        )
                        same_cluster_df['processed_text'] = same_cluster_df['combined_text'].apply(clean_text)
                        same_cluster_df['processed_text'] = same_cluster_df['processed_text'].apply(remove_stopwords)
                        same_cluster_df['processed_text'] = same_cluster_df['processed_text'].apply(lemmatize_text)

                        X_cluster = tfidf.transform(same_cluster_df['processed_text'])
                        knn = NearestNeighbors(n_neighbors=10, metric='cosine')
                        knn.fit(X_cluster)

                        distances, indices = knn.kneighbors(vecteur)
                        closest_neighbors = same_cluster_df.iloc[indices[0]]
                        
                        # Création d'un DataFrame formaté pour l'affichage
                        display_df_knn = closest_neighbors[['journal_name', 'sjr_score']].copy()
                        display_df_knn.columns = ['Journal', 'Score SJR']
                        display_df_knn['Score SJR'] = display_df_knn['Score SJR'].round(3)
                        display_df_knn['Similarité'] = (1 - distances[0]) * 100
                        display_df_knn['Similarité'] = display_df_knn['Similarité'].round(1)
                        display_df_knn.index = range(1, len(display_df_knn) + 1)
                        
                        # Ajout du style CSS pour les cards de similarité
                        st.markdown("""
                        <style>
                            .similarity-card {
                                background-color: #ffffff;
                                border-radius: 12px;
                                padding: 25px;
                                margin: 15px 0;
                                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                                border-left: 5px solid #4CAF50;
                                transition: all 0.3s ease;
                                position: relative;
                                overflow: hidden;
                            }
                            .similarity-card:hover {
                                transform: translateY(-5px);
                                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                            }
                            .journal-title {
                                color: #2E7D32;
                                font-size: 1.3em;
                                font-weight: bold;
                                margin-bottom: 15px;
                            }
                            .metrics-container {
                                display: flex;
                                gap: 20px;
                                margin-top: 15px;
                            }
                            .metric {
                                background-color: #E8F5E9;
                                padding: 10px 15px;
                                border-radius: 25px;
                                font-size: 0.9em;
                            }
                            .similarity-score {
                                color: #2E7D32;
                                font-weight: bold;
                            }
                            .sjr-metric {
                                background-color: #F1F8E9;
                            }
                            .similarity-bar {
                                width: 100%;
                                height: 8px;
                                background-color: #E8F5E9;
                                border-radius: 4px;
                                margin-top: 15px;
                                overflow: hidden;
                            }
                            .similarity-fill {
                                height: 100%;
                                background-color: #4CAF50;
                                transition: width 0.8s ease-in-out;
                            }
                        </style>
                        """, unsafe_allow_html=True)

                        # Affichage des cards
                        for idx, (_, journal) in enumerate(closest_neighbors.iterrows(), 1):
                            similarity = (1 - distances[0][idx-1]) * 100
                            card_html = f"""
                            <div class="similarity-card">
                                <div class="journal-title">{journal['journal_name']}</div>
                                <div class="similarity-bar">
                                    <div class="similarity-fill" style="width: {similarity}%;"></div>
                                </div>
                                <div class="metrics-container">
                                    <div class="metric similarity-score">
                                        <span>🎯 Similarité: {similarity:.1f}%</span>
                                    </div>
                                    <div class="metric sjr-metric">
                                        <span>📊 Score SJR: {journal['sjr_score']:.3f}</span>
                                    </div>
                                </div>
                            </div>
                            """
                            st.markdown(card_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {str(e)}")
        else:
            st.warning("⚠️ Veuillez remplir tous les champs avant de continuer.")


if __name__ == "__main__":
    main()
