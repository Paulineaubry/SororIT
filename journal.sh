# Journal de configuration SororIT

## 1. Configuration environnement dbt 

# Environnement virtuel
python3 -m venv dbt-env

# Active l'environnement virtuel
source dbt-env/bin/activate

# Installe le package dbt-postgres
pip install dbt-postgres==1.7.9

# Initialise le projet dbt
dbt init SororIT

# Configuration interactive:
# Enter a number : 1 (for PostgreSQL)
# host (hostname for the instance): localhost
# port (port for the instance): 5432
# user (username for the instance): Pauline
# password (password for the instance): wildidou
# dbname : dbsoror
# schema : dev_pauline
# threads : 4

# Vérifie la connection à la base de données
dbt debug

## 2. Configuration PostgreSQL pour l'équipe

# Se connecter à PostgreSQL en tant que superutilisateur
sudo -u postgres psql
```

```sql
-- Créer l'utilisateur principal 
CREATE USER "Pauline" WITH PASSWORD 'mot_de_passe_pauline';
CREATE DATABASE dbsoror OWNER "Pauline";
GRANT ALL PRIVILEGES ON DATABASE dbsoror TO "Pauline";

-- Créer les utilisateurs pour Aicha et Gaëlle
CREATE USER "Aicha" WITH PASSWORD 'mot_de_passe_aicha';
CREATE USER "Gaelle" WITH PASSWORD 'mot_de_passe_gaelle';

-- Donner les privilèges sur la base existante
GRANT ALL PRIVILEGES ON DATABASE dbsoror TO "Aicha";
GRANT ALL PRIVILEGES ON DATABASE dbsoror TO "Gaelle";

-- Se connecter à la base
\c dbsoror;

-- Créer les schémas personnels pour chaque développeuse
CREATE SCHEMA dev_pauline AUTHORIZATION "Pauline";
CREATE SCHEMA dev_aicha AUTHORIZATION "Aicha";
CREATE SCHEMA dev_gaelle AUTHORIZATION "Gaelle";

-- Créer le schéma partagé pour les tests d'intégration
CREATE SCHEMA staging;
GRANT ALL PRIVILEGES ON SCHEMA staging TO "Pauline", "Aicha", "Gaelle";

-- Vérifier la configuration
\l  -- Lister les bases de données
\dn -- Lister les schémas
\du -- Lister les utilisateurs

\q
```

## 3. Configuration pour chaque membre de l'équipe

### Pauline (Ubuntu)
```yaml
# nano ~/.dbt/profiles.yml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: Pauline
      password: mot_de_passe_pauline
      port: 5432
      dbname: dbsoror
      schema: dev_pauline
      threads: 4
```

### Aicha (Mac)
```yaml
# nano ~/.dbt/profiles.yml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: Aicha
      password: mot_de_passe_aicha
      port: 5432
      dbname: dbsoror
      schema: dev_aicha
      threads: 4
```

### Gaëlle (Windows)
```yaml
# %USERPROFILE%\.dbt\profiles.yml
SororIT:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: Gaelle
      password: mot_de_passe_gaelle
      port: 5432
      dbname: dbsoror
      schema: dev_gaelle
      threads: 4
```

## 4. Commandes de vérification

```bash
# Test de la configuration
dbt debug

# Exécution des modèles
dbt run

# Lancement des tests
dbt test

# Génération de la documentation
dbt docs generate
dbt docs serve
```

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

## Notes importantes
- Chaque développeuse travaille dans son propre schéma
- Le schéma `staging` est partagé pour les tests d'intégration
- Ne jamais commiter le fichier `profiles.yml` dans Git
- Toujours tester avant de merger (`dbt test`)
- Utiliser des branches Git pour chaque fonctionnalité