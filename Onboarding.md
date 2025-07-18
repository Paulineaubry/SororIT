# Onboarding DBT + Supabase - Projet SororIT

Bienvenue Aisha, Gaëlle ! Voici les étapes pour rejoindre le projet SororIT et exécuter vos modèles dbt connectés à Supabase.

---

## Prérequis

Assurez-vous d'avoir installé :

* Python 3.8+
* Git
* pip
* Un éditeur de code (VS Code recommandé)

---

## Installation du projet

```bash
# Cloner le dépôt
git clone https://github.com/Paulineaubry/SororIT.git
cd SororIT

# Créer l'environnement virtuel
python3 -m venv dbt-env
source dbt-env/bin/activate

# Installer dbt
pip install dbt-postgres==1.7.9
```

---

## Création du fichier profiles.yml

Créer le fichier `profiles.yml` dans le bon dossier :

* **Linux / Mac** : `~/.dbt/profiles.yml`
* **Windows** : `%USERPROFILE%\.dbt\profiles.yml`

### 🔹 Exemple pour Aicha

```yaml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: db.ynmlhxhpvqupdwiptyrn.supabase.co
      user: postgres
      password: VOTRE_MOT_DE_PASSE_SUPABASE
      port: 5432
      dbname: postgres
      schema: dev_aicha
      threads: 4
      sslmode: require
```

### 🔹 Exemple pour Gaëlle

Changer simplement `schema: dev_gaelle`

> Ne pas committer ce fichier dans Git.

---

## Fichier `.gitignore`

Créez un fichier `.gitignore` à la racine du projet si ce n'est pas encore fait, avec le contenu suivant :

```
# Fichiers sensibles et virtuels
dbt-env/
*.pyc
__pycache__/

# Configuration dbt personnelle
~/.dbt/
*.dbt
```

Cela empêchera d'ajouter par erreur vos fichiers locaux sensibles ou l'environnement virtuel Python.

---

## Tests

Dans le terminal :

```bash
source dbt-env/bin/activate
dbt debug
```

Attendu :

```
Connection test: [OK]
All checks passed!
```

Puis :

```bash
dbt run
dbt test
```

---

## Workflow Git

### 🔹 Correspondance des branches

| Membre  | Branche Git              | Fonctionnalité                   |
| ------- | ------------------------ | -------------------------------- |
| Aicha   | `We_can_do_it`           | Questionnaire d’orientation tech |
| Gaëlle  | `We_want_you`            | Liste d’associations engagées    |
| Pauline | `Good_morning_techwoman` | Podcasts / Blogs / YouTube       |

### 🔹 Exemple de commandes Git pour Aicha

Commencez par créer votre branche localement si elle n'existe pas encore (ou la récupérer depuis GitHub) :

```bash
# Vérifier les branches distantes disponibles
git fetch origin

# Créer la branche en local à partir de la distante /  Se placer sur sa branche 
git checkout -b We_can_do_it origin/We_can_do_it

# Ajouter/modifier un modèle
dbt run
dbt test

# Commit + push
git add .
git commit -m "feat: ajout du modèle d'orientation"
git push origin We_can_do_it
```

Créer ensuite une **pull request** dans GitHub vers `main`.


