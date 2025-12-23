# Système de Gestion des Devis de Voyage à Madagascar

Application web Python/Flask avec PostgreSQL pour automatiser la gestion des devis de voyage organisé à Madagascar.

## 🚀 Fonctionnalités

- ✅ Gestion des clients
- ✅ Création et gestion des devis
- ✅ Migration automatique des données Excel vers PostgreSQL
- ✅ Visualisation détaillée des devis avec itinéraire jour par jour
- ✅ Calcul automatique des totaux en Ariary et Euro
- ✅ Interface web moderne et responsive

## 📋 Prérequis

- Python 3.8+
- PostgreSQL 12+
- pip (gestionnaire de paquets Python)

## 🔧 Installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

3. **Configurer PostgreSQL**

Créez une base de données PostgreSQL :
```sql
CREATE DATABASE cotisation_madagascar;
```

4. **Configurer les variables d'environnement**

Copiez `.env.example` vers `.env` et modifiez les valeurs :
```bash
cp .env.example .env
```

Éditez `.env` avec vos paramètres de connexion PostgreSQL.

5. **Créer les tables de la base de données**

Exécutez le script SQL pour créer le schéma :
```bash
psql -U postgres -d cotisation_madagascar -f database/schema.sql
```

Ou utilisez Python :
```python
python -c "from database.migrate_excel_to_db import connect_db; import psycopg2; conn = connect_db(); cur = conn.cursor(); cur.execute(open('database/schema.sql').read()); conn.commit()"
```

6. **Migrer les données Excel (optionnel)**

Si vous avez un fichier Excel à migrer :
```bash
python database/migrate_excel_to_db.py
```

## 🎯 Utilisation

1. **Démarrer l'application**

```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

2. **Accéder à l'interface web**

- Page d'accueil : Liste des devis
- `/clients` : Liste des clients
- `/devis/nouveau` : Créer un nouveau devis
- `/clients/nouveau` : Créer un nouveau client

## 📊 Structure de la Base de Données

- `clients` : Informations des clients
- `devis` : Devis principaux
- `categories_couts` : Catégories de coûts (Pirogue, Bateau, Location, etc.)
- `couts_devis` : Coûts par catégorie pour chaque devis
- `jours_voyage` : Itinéraire jour par jour
- `transferts` : Transferts (Pirogue, Bateau, etc.)
- `locations_vehicules` : Locations de véhicules
- `guidages` : Services de guidage
- `reserves_parcs` : Réserves et parcs nationaux
- `hebergements` : Hébergements (hôtels)
- `repas` : Repas (PD, DN, DJ, Vinette)
- `imprevus` : Imprévus et frais supplémentaires

## 🔄 Migration des Données Excel

Le script `database/migrate_excel_to_db.py` lit le fichier Excel `Bases de datos internos.xlsx` et migre toutes les données vers PostgreSQL.

Structure Excel attendue :
- Lignes 1-18 : Informations client et catégories de coûts
- Ligne 19 : En-têtes des colonnes
- Lignes 20-34 : Données jour par jour de l'itinéraire
- Lignes 35-54 : Données supplémentaires

## 🛠️ Développement

### Structure du Projet

```
cotisation/
├── app.py                 # Application Flask principale
├── database/
│   ├── schema.sql         # Schéma de base de données
│   └── migrate_excel_to_db.py  # Script de migration Excel
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── devis_detail.html
│   ├── nouveau_devis.html
│   ├── clients.html
│   └── nouveau_client.html
├── static/
│   └── css/
│       └── style.css      # Styles CSS
├── requirements.txt        # Dépendances Python
├── .env.example           # Exemple de configuration
└── README.md              # Ce fichier
```

## 📝 Notes

- Les montants sont stockés en Ariary (monnaie malgache)
- Les conversions en Euro sont calculées automatiquement selon le taux de change
- L'application utilise Flask en mode développement (debug=True)
- Pour la production, configurez un serveur WSGI (Gunicorn, uWSGI, etc.)

## 🐛 Dépannage

**Erreur de connexion à PostgreSQL :**
- Vérifiez que PostgreSQL est démarré
- Vérifiez les paramètres dans `.env`
- Vérifiez que la base de données existe

**Erreur lors de la migration Excel :**
- Vérifiez que le fichier Excel existe
- Vérifiez que les noms de feuilles correspondent au format attendu
- Consultez les logs pour plus de détails

## 📄 Licence

Ce projet est fourni tel quel pour usage interne.

