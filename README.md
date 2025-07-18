# Projet SororIT - Guide d'installation

## Prérequis
- Python 3.8+
- PostgreSQL installé et configuré
- Git

## Installation

### 1. Cloner le projet
```bash
git clone [URL_DU_REPO]
cd SororIT
```

### 2. Créer l'environnement virtuel

**Ubuntu/Mac:**
```bash
python3 -m venv dbt-env
source dbt-env/bin/activate
```

**Windows:**
```bash
python -m venv dbt-env
dbt-env\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration PostgreSQL

#### Ubuntu
```bash
sudo -u postgres psql
```

#### Mac (avec Homebrew)
```bash
psql postgres
```

#### Windows
Utiliser pgAdmin ou psql depuis le menu Windows

# Pour changer votre mot de passe PostgreSQL
ALTER USER Aicha WITH PASSWORD 'nouveau_mdp_aicha';
ALTER USER Gaelle WITH PASSWORD 'nouveau_mdp_gaelle';
\q
```

### 5. Configuration dbt

Copier le fichier d'exemple :
```bash
cp profiles.yml.example ~/.dbt/profiles.yml
```

**Ubuntu/Mac:**
```bash
nano ~/.dbt/profiles.yml
```

**Windows:**
```bash
notepad %USERPROFILE%\.dbt\profiles.yml
```

Modifier les valeurs :
- `user`: votre nom d'utilisateur PostgreSQL
- `password`: votre mot de passe PostgreSQL
- `host`: localhost (ou l'adresse de votre serveur PostgreSQL)

### 6. Tester la configuration
```bash
dbt debug
```

Vous devriez voir `Connection test: [OK]`.

### 7. Exécuter le projet
```bash
dbt run
dbt test
```

## Structure du projet

- `models/staging/`: Modèles de données brutes
- `models/intermediate/`: Transformations intermédiaires
- `models/marts/`: Modèles finaux pour l'analyse
- `tests/`: Tests de qualité des données
- `macros/`: Fonctions réutilisables

## Bonnes pratiques

1. **Branches Git**: Créer une branche pour chaque fonctionnalité
2. **Tests**: Toujours tester avant de merger (`dbt test`)
3. **Documentation**: Documenter les modèles dans les fichiers `.yml`
4. **Peer Review**: Faire réviser les modifications par un collègue

## Environnements

- **dev**: Développement local (votre schéma personnel)
- **staging**: Tests d'intégration (optionnel)
- **prod**: Production (attention aux modifications)

## Problèmes courants

### Erreur de connexion PostgreSQL
- Vérifier que PostgreSQL est démarré
- Vérifier les identifiants dans `~/.dbt/profiles.yml`
- Tester la connexion directe : `psql -h localhost -U YOUR_USERNAME -d dbsoror`

### Erreur "dbt command not found"
- Vérifier que l'environnement virtuel est activé
- Réinstaller dbt : `pip install dbt-postgres`

### Conflits de schéma
- Chaque développeur devrait avoir son propre schéma
- Utiliser `schema: dev_{{ var('developer_name') }}` dans les modèles

## Contact

Pour toute question technique, contactez l'équipe sur [canal de communication].