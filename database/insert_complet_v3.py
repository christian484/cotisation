#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour insérer TOUS les itinéraires, hôtels, visites et types de voitures
Version 3 complète avec toutes les données
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

# Données complètes des itinéraires et hôtels
ITINERAIRES_HOTELS = {
    "Antananarivo": [
        ("Palissandre Tana", 1050000),
        ("Hôtel du Louvres", 650000),
        ("Chalets des Roses", 200000),
        ("Sakamanga", 280000),
        ("Radisson Blu", 950000),
        ("Novotel", 1450000),
        ("Maison Gallieni", 650000),
        ("Asia and Africa", 430000),
        ("Relais des Plateaux", 780000),
    ],
    "Antsirabe": [
        ("MenabeL", 280000),
        ("Hotel H1", 150000),
        ("Royal Palace", 260000),
        ("Plumeria", 370000),
        ("Arotel", 350000),
    ],
    "Miandrivazo": [
        ("Soa lia", 380000),
        ("Eden de la Tsiribihina", 480000),
        ("Princesse de la Tsiribihina", 190000),
    ],
    "Descente du Tsiribihina": [
        ("Chaland moteur (1 pers)", 2800000),
        ("Chaland moteur (2 pers)", 1500000),
        ("Chaland moteur (3 pers)", 1200000),
        ("Chaland moteur (4-8 pers)", 900000),
    ],
    "Bekopaka": [
        ("Soleil du Tsingy", 1080000),
        ("Olympe de Bemaraha", 500000),
        ("Grand Hotel du Tsingy", 500000),
        ("Palissandre Bekopaka", 1100000),
    ],
    "Morondava": [
        ("Palissandres Morondava", 1050000),
        ("Vezo Beach", 470000),
        ("Kily house", 310000),
        ("Laguna Beach", 489000),
    ],
    "Ifaty": [
        ("Le Paradisier", 780000),
        ("Dunes de l'Ifaty", 680000),
        ("Bamboo Club", 300000),
        ("Ifaty Beach Club", 390000),
    ],
    "Ranohira": [
        ("Jardin du roi", 810000),
        ("Hotel H1", 320000),
        ("Isalo Rock Lodge", 710000),
    ],
    "Fianarantsoa": [
        ("Zomatel", 340000),
        ("La rizière", 210000),
        ("Tripolitsa", 290000),
        ("Ambalakely", 320000),
    ],
    "PN Ranomafana": [
        ("Thermal", 580000),
        ("Centrest", 380000),
    ],
    "Diego Suarez": [
        ("Grand Hotel de Diego", 650000),
        ("Allamanda Hotel", 440000),
    ],
    "Ankarana": [
        ("Ankarana Lodge", 550000),
    ],
    "Ankify": [
        ("Baobab Ankify", 510000),
    ],
    "Nosy Be": [
        ("Tsarakomba Miavana tide", 1200000),
        ("Anjiamarongo Beach Ressort", 410000),
        ("Nosy Lodge", 410000),
        ("Nosy Be Hotel and Spa", 750000),
        ("Ravintsara Wellness", 1280000),
        ("L'heure Bleu", 995000),
        ("Eden Lodge", 2900000),
        ("Royal Beach", 1800000),
    ],
    "Sainte Marie": [
        ("Princesse Bora Lodge", 1870000),
        ("Mantis Soanambo", 1450000),
    ],
    "Akany ny Nofy": [
        ("Palmarium beach", 380000),
    ],
    "Transfert Bateaux Palmarium": [
        ("Transfert Bateaux Palmarium", 600000),
    ],
    "Ambositra": [],  # Nouvel itinéraire sans hôtels
    "Belo sur Mer": [],  # Nouvel itinéraire sans hôtels
    "Excursion Nosy Be": [],  # Nouvel itinéraire sans hôtels
}

# Données des visites par localité
# Format: (nom_visite, prix_par_personne, prix_par_voiture, type_prix, guidage_obligatoire, guidage_prix_base, guidage_nb_personnes_base, guidage_type_calcul, taxe_communale)
VISITES_PAR_LOCALITE = {
    "Andasibe": [
        ("Pereyras", 25000, 0, "personne", True, 45000, 3, "par_groupe", 0),
        ("Reserve de Mitsinjo", 65000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Voimma nocturna", 45000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("PN Analamazaotra", 90000, 0, "personne", True, 120000, 4, "par_groupe", 0),
        ("PN Mantadia", 90000, 0, "personne", True, 120000, 4, "par_groupe", 0),
        ("Reserve de Vakona", 50000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Voimma Diurne", 60000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Antananarivo": [
        ("Rova Ambohimanga", 20000, 0, "personne", True, 10000, 1, "par_personne", 0),
        ("Tour du ville", 0, 300000, "voiture", False, 0, 0, "par_groupe", 0),
    ],
    "Antsirabe": [
        ("Lac Tritriva", 35000, 0, "personne", True, 50000, 4, "par_groupe", 0),
        ("Manandona", 90000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("AVIMA", 120000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Betafo", 90000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Ambositra": [
        ("Rova Ambositra", 40000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Art Malagasy", 25000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Antoetra", 75000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Ranomafana": [
        ("PN Ranomafana", 110000, 0, "personne", True, 150000, 4, "par_groupe", 0),
        ("Arboretum", 50000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Immersion Tanala", 90000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Fianarantsoa": [
        ("Haute ville", 50000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Ambalamahatazana", 60000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Bel avenir Escuela granja", 75000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("cave à vin Lazan'i Betsileo", 50000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Soa landy", 25000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Papier Antemoro", 25000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Reserve Anja", 50000, 0, "personne", True, 80000, 4, "par_groupe", 0),
    ],
    "Ranohira": [
        ("PN de isalo", 130000, 0, "personne", True, 240000, 4, "par_groupe", 0),
        ("Fenetre Isalo", 60000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Ifaty": [
        ("PN Zombitse", 90000, 0, "personne", True, 160000, 4, "par_groupe", 0),
        ("Reniala", 65000, 0, "personne", True, 10000, 1, "par_personne", 0),
        ("Arboretum Antsokay", 65000, 0, "personne", True, 10000, 1, "par_personne", 0),
    ],
    "Belo sur Mer": [
        ("Sortie Quad Saline", 350000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Transfert bateau", 700000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Morondava": [
        ("Peages", 0, 200000, "voiture", False, 0, 0, "par_groupe", 0),
        ("Imprevus", 0, 140000, "voiture", False, 0, 0, "par_groupe", 0),
        ("Mangily soahonko", 100000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Kirindy", 280000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
    "Bekopaka": [
        ("Bacc Tsimafana", 0, 200000, "voiture", False, 0, 0, "par_groupe", 0),
        ("Bacc Manambolo", 0, 100000, "voiture", False, 0, 0, "par_groupe", 0),
        ("Pirogue Manambolo", 50000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("PN Tsingy de Bemaraha", 110000, 0, "personne", True, 260000, 4, "par_groupe", 0),
        ("Droit de roulage", 0, 20000, "voiture", False, 0, 0, "par_groupe", 0),
    ],
    "Diego Suarez": [
        ("3 baies de Diego", 40000, 0, "personne", True, 150000, 1, "par_voiture", 0),
        ("PN Montagne d'ambre", 110000, 0, "personne", True, 200000, 4, "par_groupe", 0),
        ("Mer emeraudes", 150000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Tsingy rouge", 60000, 0, "personne", True, 25000, 1, "par_personne", 0),
        ("PN Ankarana", 130000, 0, "personne", True, 200000, 4, "par_groupe", 0),
    ],
    "Ankify": [
        ("Plantation Millot", 150000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Plantation cacao Ambanja", 50000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Transfert bateau", 0, 400000, "bateau", False, 0, 0, "par_groupe", 0),
    ],
    "Excursion Nosy Be": [
        ("Nosy Komba", 320000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Nosy Tanihely", 320000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Nosy Iranja", 480000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Nosy Sakatia", 320000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Tour de l'ile et Mont Passot", 320000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Lemuria Land", 250000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Nosy Iranja Bivouac", 1700000, 0, "personne", False, 0, 0, "par_groupe", 0),
        ("Reserve Lokobe", 300000, 0, "personne", False, 0, 0, "par_groupe", 0),
    ],
}

# Taxes communales par localité
TAXES_COMMUNALES = {
    "Andasibe": 10000,  # Par personne
    "Ranomafana": 10000,  # Par visiteur
    "Ranohira": 10000,  # Par personne
    "Bekopaka": 10000,  # Par personne
    "Diego Suarez": 10000,  # Par personne
}

# Types de voitures avec leurs consommations
TYPES_VOITURES = [
    ("SUV", 13.0),
    ("Terracan", 15.0),
    ("Nissan", 15.0),
    ("Toyota BVM", 15.0),
    ("BVAutomatique", 16.0),
    ("LC200/Nissan Patrol V8/INFINITY/LEXUS", 18.0),
    ("LC 300/Ford T8", 18.0),
    ("LC 300/Ford T9", 18.0),
    ("Bus", 20.0),
]

def connect_db():
    """Établit la connexion à la base de données"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def calculer_prix_guidage(nb_personnes, prix_base, nb_personnes_base, type_calcul):
    """Calcule le prix du guidage selon les règles"""
    if type_calcul == "par_personne":
        return prix_base * nb_personnes
    elif type_calcul == "par_voiture":
        return prix_base  # Prix fixe par voiture
    else:  # par_groupe
        # Calculer le nombre de groupes nécessaires
        # Ex: 1-4 personnes = 1 groupe, 5-8 = 2 groupes, etc.
        nb_groupes = (nb_personnes + nb_personnes_base - 1) // nb_personnes_base
        return prix_base * nb_groupes

def insert_data():
    """Insère toutes les données dans la base de données"""
    conn = connect_db()
    if not conn:
        return
    
    cur = conn.cursor()
    
    try:
        print("=" * 80)
        print("INSERTION COMPLÈTE DES DONNÉES VERSION 3")
        print("=" * 80)
        
        # 1. Insérer les types de voitures
        print("\n1. Insertion des types de voitures...")
        type_voiture_ids = {}
        for nom, consommation in TYPES_VOITURES:
            cur.execute("""
                INSERT INTO types_voitures (nom, consommation_l_100km, ordre, actif)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (nom) DO UPDATE SET consommation_l_100km = EXCLUDED.consommation_l_100km
                RETURNING id
            """, (nom, consommation, len(type_voiture_ids) + 1))
            type_id = cur.fetchone()[0]
            type_voiture_ids[nom] = type_id
            print(f"  ✓ {nom}: {consommation}L/100km")
        conn.commit()
        
        # 2. Insérer les itinéraires
        print("\n2. Insertion des itinéraires...")
        itineraire_ids = {}
        ordre = 1
        
        # Ajouter tous les itinéraires (y compris ceux sans hôtels)
        tous_itinéraires = set(ITINERAIRES_HOTELS.keys())
        tous_itinéraires.update(VISITES_PAR_LOCALITE.keys())
        
        for itineraire_nom in sorted(tous_itinéraires):
            cur.execute("""
                INSERT INTO itineraires (nom, ordre)
                VALUES (%s, %s)
                ON CONFLICT (nom) DO UPDATE SET ordre = EXCLUDED.ordre
                RETURNING id
            """, (itineraire_nom, ordre))
            itineraire_id = cur.fetchone()[0]
            itineraire_ids[itineraire_nom] = itineraire_id
            print(f"  ✓ {itineraire_nom} (ID: {itineraire_id})")
            ordre += 1
        conn.commit()
        
        # 3. Insérer les hôtels
        print("\n3. Insertion des hôtels...")
        total_hotels = 0
        for itineraire_nom, hotels in ITINERAIRES_HOTELS.items():
            if itineraire_nom not in itineraire_ids:
                continue
            itineraire_id = itineraire_ids[itineraire_nom]
            
            for hotel_nom, prix in hotels:
                cur.execute("""
                    INSERT INTO hotels (itineraire_id, nom, prix_double, actif)
                    VALUES (%s, %s, %s, TRUE)
                    ON CONFLICT (itineraire_id, nom) 
                    DO UPDATE SET prix_double = EXCLUDED.prix_double, actif = TRUE
                """, (itineraire_id, hotel_nom, prix))
                total_hotels += 1
            
            if hotels:
                print(f"  ✓ {itineraire_nom}: {len(hotels)} hôtel(s)")
        conn.commit()
        
        # 4. Insérer les visites
        print("\n4. Insertion des visites...")
        total_visites = 0
        for localite, visites in VISITES_PAR_LOCALITE.items():
            if localite not in itineraire_ids:
                continue
            itineraire_id = itineraire_ids[localite]
            
            # Récupérer la taxe communale si elle existe
            taxe_communale = TAXES_COMMUNALES.get(localite, 0)
            
            for visite_data in visites:
                nom_visite = visite_data[0]
                prix_par_personne = visite_data[1]
                prix_par_voiture = visite_data[2]
                type_prix = visite_data[3]
                guidage_obligatoire = visite_data[4]
                guidage_prix_base = visite_data[5]
                guidage_nb_personnes_base = visite_data[6]
                guidage_type_calcul = visite_data[7]
                taxe_visite = visite_data[8] if len(visite_data) > 8 else taxe_communale
                
                cur.execute("""
                    INSERT INTO visites (
                        itineraire_id, nom, prix_par_personne, prix_par_voiture, type_prix,
                        guidage_obligatoire, guidage_prix_base, guidage_nb_personnes_base,
                        guidage_type_calcul, taxe_communale, ordre, actif
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                    ON CONFLICT (itineraire_id, nom) 
                    DO UPDATE SET 
                        prix_par_personne = EXCLUDED.prix_par_personne,
                        prix_par_voiture = EXCLUDED.prix_par_voiture,
                        type_prix = EXCLUDED.type_prix,
                        guidage_obligatoire = EXCLUDED.guidage_obligatoire,
                        guidage_prix_base = EXCLUDED.guidage_prix_base,
                        guidage_nb_personnes_base = EXCLUDED.guidage_nb_personnes_base,
                        guidage_type_calcul = EXCLUDED.guidage_type_calcul,
                        taxe_communale = EXCLUDED.taxe_communale
                """, (itineraire_id, nom_visite, prix_par_personne, prix_par_voiture, type_prix,
                      guidage_obligatoire, guidage_prix_base, guidage_nb_personnes_base,
                      guidage_type_calcul, taxe_visite, total_visites + 1))
                total_visites += 1
            
            print(f"  ✓ {localite}: {len(visites)} visite(s)")
        conn.commit()
        
        print(f"\n✅ Insertion terminée!")
        print(f"   - {len(type_voiture_ids)} type(s) de voiture(s)")
        print(f"   - {len(itineraire_ids)} itinéraire(s)")
        print(f"   - {total_hotels} hôtel(s)")
        print(f"   - {total_visites} visite(s)")
        
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

