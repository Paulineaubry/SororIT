
from flask import Flask, render_template, request

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Charger le CSV
df = pd.read_csv("static/metiers_enrichis.csv")
df['texte'] = df['Métier'] + " " + df['Description_FR']

@app.route("/")
def home():
    return render_template("page1.html")

@app.route("/good-morning")
def good_morning():
    return render_template("good_morning.html")

@app.route("/we-can-do-it", methods=["GET", "POST"])
def we_can_do_it():
    if request.method == "POST":
        # Récupérer les réponses du questionnaire
        answers = [request.form.get(f"q{i}") for i in range(1, 9)]

        # Définir les domaines
        domains = [
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "DevOps / Cloud", "Produit / Gestion"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "Cybersécurité", "Produit / Gestion"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "DevOps / Cloud", "Produit / Gestion"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "Produit / Gestion", "Cybersécurité"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "Cybersécurité", "Produit / Gestion"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "Cybersécurité", "Produit / Gestion"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "DevOps / Cloud", "Produit / Gestion"],
            ["Développement Web / Mobile", "Data & IA", "Design / UX-UI / Jeux vidéo", "DevOps / Cloud", "Produit / Gestion"],
        ]

        # Calculer le score par domaine
        scores = {
            "Développement Web / Mobile": 0,
            "Data & IA": 0,
            "Design / UX-UI / Jeux vidéo": 0,
            "DevOps / Cloud": 0,
            "Cybersécurité": 0,
            "Produit / Gestion": 0
        }

        for i, ans in enumerate(answers):
            if ans:
                scores[domains[i][int(ans) - 1]] += 1

        # Domaine dominant
        best_domain = max(scores, key=scores.get)

        # Trouver les métiers correspondants avec TF-IDF
        filtered_df = df[df['Catégorie'].str.contains(best_domain.split()[0], case=False)].copy()
        recommendations = []
        if not filtered_df.empty:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(filtered_df['texte'])
            user_vector = vectorizer.transform([best_domain])
            similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
            filtered_df['score'] = similarities
            recommendations = filtered_df.sort_values(by='score', ascending=False).head(3).to_dict(orient="records")

        return render_template("we_can_do_it.html", result=best_domain, recommendations=recommendations)

    return render_template("we_can_do_it.html", result=None)


@app.route("/we-want-you")
def we_want_you():
    return render_template("we_want_you.html")

if __name__ == "__main__":
    app.run(debug=True)

