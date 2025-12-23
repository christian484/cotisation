#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour insérer les types de locations journalières, transferts aéroport et guides
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'cotisation_madagascar'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', '2475'),
    'port': int(os.environ.get('DB_PORT', 5432))
}

# Types de locations journalières
TYPES_LOCATIONS = [
    ("Location 4x4", 340000, 0),  # Prix journalier sans carburant, avec carburant (0 = pas de location avec carburant)
    ("Location Bus", 380000, 0),
]

# Prix transfert aéroport
PRIX_TRANSFERT_AEROPORT = 250000  # Par trajet

# Prix guide accompagnateur
PRIX_GUIDE_ACCOMPAGNATEUR = 280000  # Par jour

def connect_db():
    """Établit la connexion à la base de données"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def insert_data():
    """Insère les données dans la base de données"""
    conn = connect_db()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        print("=" * 80)
        print("INSERTION DES TYPES DE LOCATIONS, TRANSFERTS ET GUIDES")
        print("=" * 80)
        
        # Insérer les types de locations journalières
        print("\n1. Insertion des types de locations journalières...")
        for nom, prix_sans_carburant, prix_avec_carburant in TYPES_LOCATIONS:
            cur.execute("""
                INSERT INTO types_locations_journalieres (
                    nom, prix_journalier_sans_carburant, prix_journalier_avec_carburant, actif
                )
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (nom) DO UPDATE SET 
                    prix_journalier_sans_carburant = EXCLUDED.prix_journalier_sans_carburant,
                    prix_journalier_avec_carburant = EXCLUDED.prix_journalier_avec_carburant
            """, (nom, prix_sans_carburant, prix_avec_carburant))
            print(f"  ✓ {nom}: {prix_sans_carburant:,} Ar/jour (sans carburant)")
        
        conn.commit()
        
        print(f"\n✅ Insertion terminée!")
        print(f"   - {len(TYPES_LOCATIONS)} type(s) de location(s) journalière(s)")
        print(f"   - Prix transfert aéroport: {PRIX_TRANSFERT_AEROPORT:,} Ar/trajet")
        print(f"   - Prix guide accompagnateur: {PRIX_GUIDE_ACCOMPAGNATEUR:,} Ar/jour")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    insert_data()
    print("\n" + "=" * 80)

