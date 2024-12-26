# pip install streamlit-aggrid
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
                        # same_cluster_df = df[df['cluster'] == cluster_num]
                        same_cluster_df = df[df['cluster'] == cluster_num].copy()
                        same_cluster_df['sjr_score'] = pd.to_numeric(same_cluster_df['sjr_score'], errors='coerce')
                        same_cluster_df = same_cluster_df.dropna(subset=['sjr_score'])
                        top_10_high_sjr = same_cluster_df.sort_values(by='sjr_score', ascending=False).head(10)
                        
                        # Création d'un DataFrame formaté pour l'affichage
                        display_df_sjr = top_10_high_sjr[['journal_name', 'sjr_score']].copy()
                        display_df_sjr.columns = ['Journal', 'Score SJR']
                        display_df_sjr['Score SJR'] = display_df_sjr['Score SJR'].round(3)
                        display_df_sjr.index = range(1, len(display_df_sjr) + 1)
                        
                        # Affichage avec mise en forme
                        st.markdown("""
                        <style>
                            .journal-title {
                                font-weight: bold;
                                color: #1E88E5;
                                font-size: 1.1em;
                            }
                        </style>
                        """, unsafe_allow_html=True)

                        st.dataframe(
                            display_df_sjr,
                            column_config={
                                "Journal": st.column_config.TextColumn(
                                    "Journal",
                                    width=800,
                                    help="Nom du journal académique"
                                ),
                                "Score SJR": st.column_config.NumberColumn(
                                    "Score SJR",
                                    width=400,
                                    format="%.3f",
                                    help="Scientific Journal Rankings score"
                                )
                            },
                            hide_index=False,
                            use_container_width=False,
                            height=800
                        )

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
                        
                        # Affichage avec mise en forme
                        st.dataframe(
                            display_df_knn,
                            column_config={
                                "Journal": st.column_config.TextColumn(
                                    "Journal",
                                    width=800,
                                    help="Nom du journal académique"
                                ),
                                "Score SJR": st.column_config.NumberColumn(
                                    "Score SJR",
                                    width=250,
                                    format="%.3f"
                                ),
                                "Similarité": st.column_config.ProgressColumn(
                                    "Similarité (%)",
                                    width=600,
                                    format="%.1f%%",
                                    min_value=0,
                                    max_value=100,
                                    help="Pourcentage de similarité avec votre article"
                                )
                            },
                            hide_index=False,
                            use_container_width=False,
                            height=850
                        )
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {str(e)}")
        else:
            st.warning("⚠️ Veuillez remplir tous les champs avant de continuer.")


if __name__ == "__main__":
    main()
