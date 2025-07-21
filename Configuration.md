# Journal de configuration SororIT - version Supabase

## 1. Configuration environnement dbt (avec Supabase)

### Environnement virtuel

```bash
python3 -m venv dbt-env
source dbt-env/bin/activate
```

### Installation DBT

```bash
pip install dbt-postgres==1.7.9
```

### Initialisation du projet DBT

```bash
dbt init SororIT
```

## 2. Configuration Supabase pour l'équipe

### Création du projet Supabase

* Projet créé sur [https://app.supabase.com]
* Un seul utilisateur PostgreSQL : `postgres`
* Base de données : `postgres`
* Hôte : `db.ynmlhxhpvqupdwiptyrn.supabase.co`
* Port : `5432`

### Création des schémas (exécuter dans SQL Editor Supabase)

```sql
create schema if not exists dev_pauline;
create schema if not exists dev_aicha;
create schema if not exists dev_gaelle;
create schema if not exists staging;
```

### Droits (facultatif si vous êtes toutes sur le compte `postgres`)

```sql
grant all privileges on schema dev_pauline to postgres;
grant all privileges on schema dev_aicha to postgres;
grant all privileges on schema dev_gaelle to postgres;
grant all privileges on schema staging to postgres;
```

---

## 3. Fichier de configuration dbt pour chaque membre

### Pauline

```yaml
# ~/.dbt/profiles.yml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: db.ynmlhxhpvqupdwiptyrn.supabase.co
      user: postgres
      password: VOTRE_MDP_SUPABASE
      port: 5432
      dbname: postgres
      schema: dev_pauline
      threads: 4
      sslmode: require
```

### Aicha

```yaml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: db.ynmlhxhpvqupdwiptyrn.supabase.co
      user: postgres
      password: VOTRE_MDP_SUPABASE
      port: 5432
      dbname: postgres
      schema: dev_aicha
      threads: 4
      sslmode: require
```

### Gaëlle

```yaml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: db.ynmlhxhpvqupdwiptyrn.supabase.co
      user: postgres
      password: VOTRE_MDP_SUPABASE
      port: 5432
      dbname: postgres
      schema: dev_gaelle
      threads: 4
      sslmode: require
```

> ⚠️ Ne jamais commit ce fichier dans Git

---

## 4. Commandes utiles DBT

```bash
# Tester la connexion
dbt debug

# Exécuter les modèles
dbt run

# Tester la qualité
dbt test

# Générer la documentation
dbt docs generate
dbt docs serve
```

---

## 5. Workflow Git recommandé

```bash
# Créer une branche pour une nouvelle fonctionnalité
git checkout -b feature/nom-de-la-fonctionnalite

# Développer et tester
dbt run
dbt test

# Commiter les changements
git add .
git commit -m "Description des changements"

# Pousser et créer une pull request
git push origin feature/nom-de-la-fonctionnalite
```

---

## Notes importantes

* Chaque développeuse travaille dans son propre schéma : `dev_<prenom>`
* Le schéma `staging` est partagé pour les tests d'intégration
* Ne jamais committer `profiles.yml`
* Toujours tester avec `dbt test` avant de merger
* Utiliser des branches Git séparées par fonctionnalité
