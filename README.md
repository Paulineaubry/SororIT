# SororIT - Application pour les femmes dans la tech

**SororIT** est une application web dédiée aux femmes françaises qui souhaitent s'informer, se former, se connecter et s'inspirer dans le monde du numérique et de la tech.

---

## Objectif du projet

Favoriser l'accès des femmes aux métiers du numérique, en leur proposant des ressources personnalisées, locales et inspirantes.

---

## Fonctionnalités principales

### 1. **We want you**

* Regroupe les associations et écoles engagées pour la diversité dans le numérique
* Données géolocalisées selon la ville / région de l'utilisatrice

### 2. **You can do it**

* Questionnaire interactif
* Analyse les intérêts et compétences de l'utilisatrice
* Recommande un domaine tech pour se former (ex : dev, data, design)

### 3. **Good morning techwoman**

* Propose des ressources inspirantes :

  * Podcasts
  * Chaînes YouTube
  * Blogs tech
* Mises à jour via APIs ou bases collaboratives

---

## Technologies utilisées

* **Python** / **Flask** : backend de l'application web
* **Supabase** : hébergement PostgreSQL et gestion des utilisateurs
* **PostgreSQL** : base de données relationnelle
* **DBT** : modélisation des données
* **Pandas** : traitement et manipulation de données
* **APIs** : pour les ressources (podcasts, assos, etc.)

---

## Structure du projet

```
SororIT/
├── dbt/                  # Projet DBT (models, macros, tests)
├── flask_app/            # Backend Flask
├── data/                 # Fichiers CSV / exemples
├── notebooks/            # Explorations pandas
├── .dbt/                 # Profiles locaux dbt (non commité)
├── README.md             # Ce fichier
├── ONBOARDING.md         # Guide de démarrage équipe
```

---

## Installation rapide

```bash
# Cloner le projet
git clone https://github.com/Paulineaubry/SororIT.git
cd SororIT

# Créer et activer l'environnement Python
python3 -m venv dbt-env
source dbt-env/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## Commandes utiles

```bash
# Lancer DBT
dbt debug
dbt run
dbt test

dbt docs generate
dbt docs serve

# Lancer le serveur Flask
cd flask_app
flask run
```

---

## 👥 Équipe et rôles

| Membre  | Fonctionnalité                      | Branche Git              |
| ------- | ----------------------------------- | ------------------------ |
| Pauline | Good Morning Techwoman              | `Good_morning_techwoman` |
| Aicha   | You Can Do It (questionnaire)       | `We_can_do_it`           |
| Gaëlle  | We Want You (associations + cartes) | `We_want_you`            |

---

## 🚀 Objectifs à venir

* Intégration frontend Flask + templates Jinja
* Affichage dynamique des associations sur carte
* API déployable en ligne (Railway, Render, etc.)

---

Pour plus d'infos :contacter l'équipe via GitHub.
