# Guide de Configuration - Fichier .env

## 📝 Configuration du fichier .env

Le fichier `.env` contient les paramètres de configuration de l'application. Il a été créé automatiquement avec des valeurs par défaut.

### 🔧 Paramètres à modifier

Ouvrez le fichier `.env` avec votre éditeur de texte préféré et modifiez les valeurs suivantes selon votre configuration PostgreSQL :

```env
# Configuration de la base de données PostgreSQL
DB_HOST=localhost              # Adresse du serveur PostgreSQL (généralement localhost)
DB_NAME=cotisation_madagascar  # Nom de votre base de données
DB_USER=postgres               # Nom d'utilisateur PostgreSQL
DB_PASSWORD=postgres           # Mot de passe PostgreSQL (⚠️ À CHANGER)
DB_PORT=5432                   # Port PostgreSQL (généralement 5432)

# Clé secrète pour Flask (à changer en production)
SECRET_KEY=changez-moi-en-production-avec-une-cle-secrete-forte
```

### 📋 Étapes de configuration

1. **Ouvrir le fichier .env**
   ```bash
   nano .env
   # ou
   vim .env
   # ou avec votre éditeur préféré
   ```

2. **Modifier les paramètres PostgreSQL**
   
   Remplacez les valeurs par défaut par vos propres paramètres :
   
   - `DB_HOST` : Si PostgreSQL est sur une autre machine, mettez l'adresse IP ou le nom d'hôte
   - `DB_NAME` : Le nom de votre base de données (doit exister)
   - `DB_USER` : Votre nom d'utilisateur PostgreSQL
   - `DB_PASSWORD` : Votre mot de passe PostgreSQL
   - `DB_PORT` : Le port PostgreSQL (par défaut 5432)

3. **Générer une clé secrète pour Flask**
   
   Pour la production, générez une clé secrète sécurisée :
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   
   Copiez le résultat et remplacez `SECRET_KEY` dans le fichier `.env`

### ✅ Vérification de la configuration

Pour vérifier que votre configuration est correcte, vous pouvez tester la connexion :

```bash
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )
    print('✅ Connexion réussie à PostgreSQL!')
    conn.close()
except Exception as e:
    print(f'❌ Erreur de connexion: {e}')
"
```

### 🔒 Sécurité

⚠️ **Important** :
- Ne partagez JAMAIS votre fichier `.env` publiquement
- Ne commitez PAS le fichier `.env` dans Git (il devrait être dans `.gitignore`)
- Utilisez des mots de passe forts pour PostgreSQL
- Changez la `SECRET_KEY` en production

### 📝 Exemple de configuration typique

Si vous avez installé PostgreSQL localement avec les paramètres par défaut :

```env
DB_HOST=localhost
DB_NAME=cotisation_madagascar
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe_ici
DB_PORT=5432
SECRET_KEY=votre-cle-secrete-generee
```

### 🆘 Dépannage

**Erreur "connection refused"** :
- Vérifiez que PostgreSQL est démarré : `sudo systemctl status postgresql`
- Vérifiez que le port 5432 est ouvert

**Erreur "database does not exist"** :
- Créez la base de données : `createdb -U postgres cotisation_madagascar`
- Ou via psql : `psql -U postgres -c "CREATE DATABASE cotisation_madagascar;"`

**Erreur "password authentication failed"** :
- Vérifiez votre mot de passe PostgreSQL
- Vérifiez que l'utilisateur existe : `psql -U postgres -c "\du"`

