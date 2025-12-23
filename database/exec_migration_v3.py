#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour exécuter la migration SQL vers la version 3 directement via Python
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

def execute_migration():
    """Exécute le script de migration SQL"""
    print("=" * 80)
    print("MIGRATION VERS LA VERSION 3")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Lire le fichier SQL
        with open('database/migrate_to_v3.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Exécuter le SQL
        print("\nExécution de la migration...")
        cur.execute(sql_content)
        conn.commit()
        
        print("✅ Migration terminée avec succès!")
        
        # Vérifier que les tables existent
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('visites', 'types_voitures', 'visites_jour')
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        if tables:
            print(f"\n✅ Tables créées:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("\n⚠️  Tables non trouvées")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        return False
    
    return True

if __name__ == "__main__":
    if execute_migration():
        print("\n" + "=" * 80)
        print("Vous pouvez maintenant exécuter: python3 database/insert_itineraires_hotels_complet.py")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("ERREUR LORS DE LA MIGRATION")
        print("=" * 80)

