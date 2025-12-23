#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse de la table visites_jour dans la base de données
"""

import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'cotisation_madagascar'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'port': int(os.environ.get('DB_PORT', 5432))
}

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def analyser_visites_jour():
    conn = connect_db()
    if not conn:
        return
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 80)
    print("ANALYSE DE LA TABLE visites_jour")
    print("=" * 80)
    print()
    
    # 1. Vérifier si la table existe
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'visites_jour'
        );
    """)
    table_exists = cur.fetchone()['exists']
    
    if not table_exists:
        print("❌ La table 'visites_jour' n'existe pas dans la base de données!")
        print("   Vous devez exécuter la migration v3 ou v4.")
        conn.close()
        return
    
    print("✅ La table 'visites_jour' existe")
    print()
    
    # 2. Analyser la structure de la table
    print("📋 STRUCTURE DE LA TABLE:")
    print("-" * 80)
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = 'visites_jour'
        ORDER BY ordinal_position;
    """)
    
    colonnes = cur.fetchall()
    for col in colonnes:
        longueur = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
        print(f"  • {col['column_name']:<25} {col['data_type']:<20} {longueur:<10} {nullable} {default}")
    
    print()
    
    # 3. Compter le nombre total d'enregistrements
    cur.execute("SELECT COUNT(*) as total FROM visites_jour")
    total = cur.fetchone()['total']
    print(f"📊 NOMBRE TOTAL D'ENREGISTREMENTS: {total}")
    print()
    
    if total == 0:
        print("⚠️  Aucune donnée dans la table visites_jour")
        conn.close()
        return
    
    # 4. Analyser les colonnes de prix
    print("💰 ANALYSE DES COLONNES DE PRIX:")
    print("-" * 80)
    
    colonnes_prix = ['prix_entree', 'prix_guidage', 'prix_taxe_communale', 'prix_total']
    
    for col in colonnes_prix:
        cur.execute(f"""
            SELECT 
                COUNT(*) as total,
                COUNT({col}) as non_null,
                COUNT(*) - COUNT({col}) as null_count,
                MIN({col}) as min_val,
                MAX({col}) as max_val,
                AVG({col}) as avg_val,
                SUM({col}) as sum_val
            FROM visites_jour
            WHERE {col} IS NOT NULL
        """)
        stats = cur.fetchone()
        
        print(f"\n  📌 {col}:")
        print(f"     • Total d'enregistrements: {stats['total']}")
        print(f"     • Valeurs non-null: {stats['non_null']}")
        print(f"     • Valeurs null: {stats['null_count']}")
        if stats['non_null'] > 0:
            print(f"     • Minimum: {stats['min_val']:,.2f} Ar" if stats['min_val'] else "     • Minimum: 0 Ar")
            print(f"     • Maximum: {stats['max_val']:,.2f} Ar" if stats['max_val'] else "     • Maximum: 0 Ar")
            print(f"     • Moyenne: {stats['avg_val']:,.2f} Ar" if stats['avg_val'] else "     • Moyenne: 0 Ar")
            print(f"     • Somme totale: {stats['sum_val']:,.2f} Ar" if stats['sum_val'] else "     • Somme totale: 0 Ar")
    
    print()
    
    # 5. Afficher quelques exemples de données
    print("📝 EXEMPLES DE DONNÉES (5 premiers enregistrements):")
    print("-" * 80)
    
    cur.execute("""
        SELECT 
            vj.*,
            v.nom as visite_nom,
            v.guidage_obligatoire,
            v.guidage_type_calcul,
            jv.numero_jour,
            jv.date_jour
        FROM visites_jour vj
        LEFT JOIN visites v ON vj.visite_id = v.id
        LEFT JOIN jours_voyage jv ON vj.jour_voyage_id = jv.id
        ORDER BY vj.id
        LIMIT 5
    """)
    
    exemples = cur.fetchall()
    
    if exemples:
        for i, ex in enumerate(exemples, 1):
            print(f"\n  Exemple {i}:")
            print(f"    • ID: {ex['id']}")
            print(f"    • Visite: {ex['visite_nom'] or 'N/A'}")
            print(f"    • Jour de voyage ID: {ex['jour_voyage_id']}")
            print(f"    • Numéro jour: {ex['numero_jour']}")
            print(f"    • Date jour: {ex['date_jour']}")
            print(f"    • Nombre personnes: {ex['nombre_personnes']}")
            print(f"    • Prix entrée: {ex['prix_entree']:,.2f} Ar" if ex['prix_entree'] else "    • Prix entrée: NULL ou 0")
            print(f"    • Prix guidage: {ex['prix_guidage']:,.2f} Ar" if ex['prix_guidage'] else "    • Prix guidage: NULL ou 0")
            print(f"    • Prix taxe communale: {ex['prix_taxe_communale']:,.2f} Ar" if ex['prix_taxe_communale'] else "    • Prix taxe communale: NULL ou 0")
            print(f"    • Prix total: {ex['prix_total']:,.2f} Ar" if ex['prix_total'] else "    • Prix total: NULL ou 0")
            if ex['guidage_obligatoire']:
                print(f"    • Guidage obligatoire: OUI (type: {ex['guidage_type_calcul']})")
            else:
                print(f"    • Guidage obligatoire: NON")
    else:
        print("  Aucun enregistrement trouvé")
    
    print()
    
    # 6. Statistiques par visite
    print("📊 STATISTIQUES PAR VISITE:")
    print("-" * 80)
    
    cur.execute("""
        SELECT 
            v.nom as visite_nom,
            COUNT(vj.id) as nb_occurrences,
            SUM(vj.prix_entree) as total_entree,
            SUM(vj.prix_guidage) as total_guidage,
            SUM(vj.prix_taxe_communale) as total_taxe,
            SUM(vj.prix_total) as total_prix
        FROM visites_jour vj
        LEFT JOIN visites v ON vj.visite_id = v.id
        GROUP BY v.nom
        ORDER BY nb_occurrences DESC
        LIMIT 10
    """)
    
    stats_visites = cur.fetchall()
    
    if stats_visites:
        print(f"\n  Top 10 des visites les plus fréquentes:\n")
        for stat in stats_visites:
            print(f"    • {stat['visite_nom'] or 'N/A'}:")
            print(f"      - Occurrences: {stat['nb_occurrences']}")
            print(f"      - Total entrée: {stat['total_entree']:,.2f} Ar" if stat['total_entree'] else "      - Total entrée: 0 Ar")
            print(f"      - Total guidage: {stat['total_guidage']:,.2f} Ar" if stat['total_guidage'] else "      - Total guidage: 0 Ar")
            print(f"      - Total taxe: {stat['total_taxe']:,.2f} Ar" if stat['total_taxe'] else "      - Total taxe: 0 Ar")
            print(f"      - Total prix: {stat['total_prix']:,.2f} Ar" if stat['total_prix'] else "      - Total prix: 0 Ar")
            print()
    else:
        print("  Aucune statistique disponible")
    
    print()
    
    # 7. Vérifier les relations avec la table visites
    print("🔗 VÉRIFICATION DES RELATIONS:")
    print("-" * 80)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total_visites_jour,
            COUNT(DISTINCT visite_id) as nb_visites_differentes,
            COUNT(CASE WHEN visite_id IS NULL THEN 1 END) as visites_sans_lien
        FROM visites_jour
    """)
    
    relations = cur.fetchone()
    print(f"  • Total visites_jour: {relations['total_visites_jour']}")
    print(f"  • Nombre de visites différentes: {relations['nb_visites_differentes']}")
    print(f"  • Visites sans lien (visite_id NULL): {relations['visites_sans_lien']}")
    
    print()
    print("=" * 80)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    analyser_visites_jour()

