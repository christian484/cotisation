#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test de connexion à PostgreSQL
"""

import psycopg2
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("Test de connexion à PostgreSQL")
print("=" * 60)
print()

# Afficher la configuration (sans le mot de passe)
print("Configuration:")
print(f"  Host: {os.getenv('DB_HOST')}")
print(f"  Database: {os.getenv('DB_NAME')}")
print(f"  User: {os.getenv('DB_USER')}")
print(f"  Port: {os.getenv('DB_PORT')}")
print(f"  Password: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
print()

# Tester la connexion
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT', 5432))
    )
    
    print("✅ Connexion réussie à PostgreSQL!")
    print()
    
    # Vérifier que les tables existent
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    
    if tables:
        print(f"✅ {len(tables)} table(s) trouvée(s) dans la base de données:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("⚠️  Aucune table trouvée. Exécutez le script schema.sql pour créer les tables.")
        print("   Commande: psql -U postgres -d cotisation_madagascar -f database/schema.sql")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print("❌ Erreur de connexion à PostgreSQL:")
    print(f"   {e}")
    print()
    print("Vérifiez:")
    print("   1. Que PostgreSQL est démarré")
    print("   2. Que la base de données existe")
    print("   3. Que les paramètres dans .env sont corrects")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

print()
print("=" * 60)

