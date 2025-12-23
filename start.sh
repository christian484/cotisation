#!/bin/bash
# Script de démarrage rapide pour l'application

echo "🚀 Démarrage de l'application de gestion des devis Madagascar"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier si PostgreSQL est accessible
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL n'est pas installé ou psql n'est pas dans le PATH"
    echo "   Assurez-vous que PostgreSQL est installé et configuré"
fi

# Vérifier si les dépendances sont installées
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

echo "📦 Activation de l'environnement virtuel..."
source venv/bin/activate

echo "📦 Installation des dépendances..."
pip install -q -r requirements.txt

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Le fichier .env n'existe pas"
    echo "   Création d'un fichier .env à partir de .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ✓ Fichier .env créé. Veuillez le modifier avec vos paramètres."
    else
        echo "   ❌ Fichier .env.example non trouvé"
    fi
fi

echo ""
echo "✅ Configuration terminée"
echo ""
echo "📝 Pour démarrer l'application:"
echo "   python3 app.py"
echo ""
echo "📝 Pour migrer les données Excel:"
echo "   python3 database/migrate_excel_to_db.py"
echo ""
echo "🌐 L'application sera accessible sur: http://localhost:5000"
echo ""

