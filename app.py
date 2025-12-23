#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Flask pour la gestion des devis de voyage à Madagascar
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import os
from functools import wraps
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration de la base de données
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'cotisation_madagascar'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'port': int(os.environ.get('DB_PORT', 5432))
}

def get_db_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def db_query(query, params=None, fetch_one=False, fetch_all=False):
    """Exécute une requête SQL et retourne les résultats"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = None
        
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        print(f"Erreur SQL: {e}")
        return None
    finally:
        cur.close()
        conn.close()

# Routes principales
@app.route('/')
def index():
    """Page d'accueil - Liste des devis"""
    devis = db_query("""
        SELECT d.*, c.nom as client_nom, c.reference as client_ref
        FROM devis d
        LEFT JOIN clients c ON d.client_id = c.id
        ORDER BY d.created_at DESC
        LIMIT 50
    """, fetch_all=True)
    
    return render_template('index.html', devis=devis or [])

@app.route('/devis/<int:devis_id>')
def voir_devis(devis_id):
    """Affiche les détails d'un devis"""
    devis = db_query("""
        SELECT d.*, c.nom as client_nom, c.reference as client_ref,
               c.email, c.telephone
        FROM devis d
        LEFT JOIN clients c ON d.client_id = c.id
        WHERE d.id = %s
    """, (devis_id,), fetch_one=True)
    
    if not devis:
        flash('Devis non trouvé', 'error')
        return redirect(url_for('index'))
    
    # Recalculer les totaux avant d'afficher
    calculer_totaux_devis(devis_id)
    
    # Récupérer les jours de voyage
    jours = db_query("""
        SELECT * FROM jours_voyage
        WHERE devis_id = %s
        ORDER BY numero_jour
    """, (devis_id,), fetch_all=True)
    
    # Récupérer les coûts par catégorie
    couts = db_query("""
        SELECT cc.nom, cd.montant_ariary, cd.montant_euro
        FROM couts_devis cd
        JOIN categories_couts cc ON cd.categorie_id = cc.id
        WHERE cd.devis_id = %s
        ORDER BY cc.ordre
    """, (devis_id,), fetch_all=True)
    
    # Récupérer les détails pour chaque jour
    jours_details = []
    for jour in jours or []:
        jour_id = jour['id']
        
        transferts = db_query("""
            SELECT * FROM transferts WHERE jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        locations = db_query("""
            SELECT l.*, tv.nom as type_voiture_nom, tv.consommation_l_100km
            FROM locations_vehicules l
            LEFT JOIN types_voitures tv ON l.type_voiture_id = tv.id
            WHERE l.jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        guidages = db_query("""
            SELECT * FROM guidages WHERE jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        reserves = db_query("""
            SELECT * FROM reserves_parcs WHERE jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        hebergements = db_query("""
            SELECT h.*, ho.nom as hotel_nom
            FROM hebergements h
            LEFT JOIN hotels ho ON h.hotel_id = ho.id
            WHERE h.jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        repas = db_query("""
            SELECT * FROM repas WHERE jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        visites = db_query("""
            SELECT vj.*, v.nom as visite_nom
            FROM visites_jour vj
            LEFT JOIN visites v ON vj.visite_id = v.id
            WHERE vj.jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        locations_journalieres = db_query("""
            SELECT lj.*, tlj.nom as type_location_nom
            FROM locations_journalieres lj
            LEFT JOIN types_locations_journalieres tlj ON lj.type_location_id = tlj.id
            WHERE lj.jour_voyage_id = %s
        """, (jour_id,), fetch_all=True)
        
        # Calculer les totaux par jour
        total_hebergement_jour = sum(
            (float(h.get('prix_ariary') or 0) + float(h.get('transfert_htl') or 0))
            for h in (hebergements or [])
        )
        
        total_visites_jour = sum(
            float(v.get('prix_total') or 0)
            for v in (visites or [])
        )
        
        total_carburant_jour = sum(
            float(l.get('prix_carburant_total') or 0)
            for l in (locations or [])
        )
        
        total_locations_jour = sum(
            float(l.get('prix_ariary') or 0)
            for l in (locations or [])
        )
        
        total_locations_journalieres_jour = sum(
            float(lj.get('prix_total') or 0)
            for lj in (locations_journalieres or [])
        )
        
        total_jour = (total_hebergement_jour + total_visites_jour + 
                     total_carburant_jour + total_locations_jour + 
                     total_locations_journalieres_jour)
        
        jours_details.append({
            'jour': jour,
            'transferts': transferts or [],
            'locations': locations or [],
            'locations_journalieres': locations_journalieres or [],
            'guidages': guidages or [],
            'reserves': reserves or [],
            'hebergements': hebergements or [],
            'repas': repas or [],
            'visites': visites or [],
            'total_hebergement_jour': total_hebergement_jour,
            'total_visites_jour': total_visites_jour,
            'total_carburant_jour': total_carburant_jour,
            'total_locations_jour': total_locations_jour,
            'total_locations_journalieres_jour': total_locations_journalieres_jour,
            'total_jour': total_jour
        })
    
    # Récupérer les imprévus
    imprevus = db_query("""
        SELECT * FROM imprevus WHERE devis_id = %s
    """, (devis_id,), fetch_all=True)
    
    # Récupérer les transferts aéroport
    transferts_aeroport = db_query("""
        SELECT * FROM transferts_aeroport WHERE devis_id = %s
    """, (devis_id,), fetch_all=True)
    
    # Récupérer les guides accompagnateurs
    guides_accompagnateurs = db_query("""
        SELECT * FROM guides_accompagnateurs WHERE devis_id = %s
    """, (devis_id,), fetch_all=True)
    
    return render_template('devis_detail.html', 
                         devis=devis,
                         jours_details=jours_details,
                         couts=couts or [],
                         imprevus=imprevus or [],
                         transferts_aeroport=transferts_aeroport or [],
                         guides_accompagnateurs=guides_accompagnateurs or [])

@app.route('/devis/nouveau', methods=['GET', 'POST'])
def nouveau_devis():
    """Créer un nouveau devis"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        client_id = request.form.get('client_id')
        reference = request.form.get('reference')
        date_cotation = request.form.get('date_cotation')
        nombre_personnes = int(request.form.get('nombre_personnes', 0))
        nombre_adultes = int(request.form.get('nombre_adultes', 0))
        nombre_enfants = int(request.form.get('nombre_enfants', 0))
        nombre_bebes = int(request.form.get('nombre_bebes', 0))
        nombre_chambres = int(request.form.get('nombre_chambres', 0))
        taux_change = float(request.form.get('taux_change', 4420))
        marge_percent = float(request.form.get('marge_percent', 18))
        
        # Créer le devis
        result = db_query("""
            INSERT INTO devis (
                client_id, reference, date_cotation, nombre_personnes,
                nombre_adultes, nombre_enfants, nombre_bebes, nombre_chambres,
                taux_change, marge_percent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (client_id, reference, date_cotation, nombre_personnes,
              nombre_adultes, nombre_enfants, nombre_bebes, nombre_chambres,
              taux_change, marge_percent), fetch_one=True)
        
        if result:
            devis_id = result['id']
            
            # Traiter les jours de voyage si fournis
            jours_data = request.form.getlist('jours[]')
            created_jour_ids = []  # Pour stocker les IDs des jours créés
            if jours_data:
                import json
                for jour_json in jours_data:
                    try:
                        jour_data = json.loads(jour_json)
                        numero_jour = int(jour_data.get('numero_jour', 0))
                        itineraire_id = jour_data.get('itineraire_id')
                        date_jour = jour_data.get('date_jour')
                        hotel_id = jour_data.get('hotel_id')
                        type_chambre = jour_data.get('type_chambre', 'Double')
                        nombre_chambres_jour = int(jour_data.get('nombre_chambres', 1))
                        transfert_htl = float(jour_data.get('transfert_htl', 0))
                        
                        if numero_jour and itineraire_id:
                            # Créer le jour de voyage
                            jour_result = db_query("""
                                INSERT INTO jours_voyage (devis_id, numero_jour, itineraire_id, date_jour, ordre)
                                VALUES (%s, %s, %s, %s, %s)
                                RETURNING id
                            """, (devis_id, numero_jour, itineraire_id, date_jour, numero_jour), fetch_one=True)
                            
                            if jour_result:
                                jour_voyage_id = jour_result['id']
                                created_jour_ids.append(jour_voyage_id)
                                
                                # Ajouter l'hébergement si un hôtel est sélectionné
                                if hotel_id:
                                    hotel = db_query("SELECT prix_double, prix_triple, nom FROM hotels WHERE id = %s", (hotel_id,), fetch_one=True)
                                    if hotel:
                                        prix_chambre = float(hotel['prix_triple'] if type_chambre == 'Triple' and hotel['prix_triple'] else hotel['prix_double'])
                                        prix_total = prix_chambre * nombre_chambres_jour
                                        
                                        db_query("""
                                            INSERT INTO hebergements (jour_voyage_id, hotel_id, type_chambre, nom_hotel, nombre_chambres, prix_ariary, transfert_htl)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                                        """, (jour_voyage_id, hotel_id, type_chambre, hotel['nom'], nombre_chambres_jour, prix_total, transfert_htl))
                                
                                # Ajouter les visites si fournies (peut être plusieurs)
                                visites_data = jour_data.get('visites', [])
                                if isinstance(visites_data, str):
                                    # Si c'est une chaîne JSON, la parser
                                    try:
                                        visites_data = json.loads(visites_data)
                                    except:
                                        visites_data = []
                                
                                # S'assurer que visites_data est une liste
                                if not isinstance(visites_data, list):
                                    visites_data = []
                                
                                for visite_data in visites_data:
                                    visite_id = visite_data.get('visite_id') if isinstance(visite_data, dict) else None
                                    nb_personnes_visite = int(visite_data.get('nb_personnes', 0) or 0) if isinstance(visite_data, dict) else 0
                                    
                                    if visite_id and nb_personnes_visite > 0:
                                        visite = db_query("""
                                            SELECT id, nom, prix_par_personne, prix_par_voiture, type_prix,
                                                   guidage_obligatoire, guidage_prix_base, guidage_nb_personnes_base,
                                                   guidage_type_calcul, taxe_communale
                                            FROM visites WHERE id = %s
                                        """, (visite_id,), fetch_one=True)
                                        
                                        if visite:
                                            # Calculer le prix d'entrée
                                            prix_entree = 0
                                            if visite['type_prix'] == 'personne':
                                                prix_entree = float(visite['prix_par_personne'] or 0) * nb_personnes_visite
                                            elif visite['type_prix'] in ('voiture', 'bateau'):
                                                prix_entree = float(visite['prix_par_voiture'] or 0)
                                            
                                            # Calculer le prix du guidage si obligatoire
                                            prix_guidage = 0
                                            if visite['guidage_obligatoire'] and visite['guidage_prix_base']:
                                                guidage_prix_base = float(visite['guidage_prix_base'])
                                                guidage_nb_base = int(visite['guidage_nb_personnes_base'] or 4)
                                                guidage_type = visite['guidage_type_calcul']
                                                
                                                if guidage_type == 'par_personne':
                                                    prix_guidage = guidage_prix_base * nb_personnes_visite
                                                elif guidage_type == 'par_voiture':
                                                    prix_guidage = guidage_prix_base
                                                else:  # par_groupe
                                                    nb_groupes = (nb_personnes_visite + guidage_nb_base - 1) // guidage_nb_base
                                                    prix_guidage = guidage_prix_base * nb_groupes
                                            
                                            # Calculer la taxe communale
                                            prix_taxe = float(visite['taxe_communale'] or 0) * nb_personnes_visite
                                            
                                            # Prix total de la visite
                                            prix_total_visite = prix_entree + prix_guidage + prix_taxe
                                            
                                            db_query("""
                                                INSERT INTO visites_jour (jour_voyage_id, visite_id, nombre_personnes, nombre_voitures,
                                                                         prix_entree, prix_guidage, prix_taxe_communale, prix_total)
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                            """, (jour_voyage_id, visite_id, nb_personnes_visite, 0, 
                                                  prix_entree, prix_guidage, prix_taxe, prix_total_visite))
                                
                                # Ajouter la location de véhicule si fournie
                                type_voiture_id = jour_data.get('type_voiture_id')
                                kilometrage = float(jour_data.get('kilometrage', 0) or 0)
                                prix_carburant_pompe = float(jour_data.get('prix_carburant_pompe', 0) or 0)
                                
                                if type_voiture_id and kilometrage > 0:
                                    type_voiture = db_query("""
                                        SELECT consommation_l_100km FROM types_voitures WHERE id = %s
                                    """, (type_voiture_id,), fetch_one=True)
                                    
                                    if type_voiture:
                                        consommation_l_100km = float(type_voiture['consommation_l_100km'])
                                        
                                        # Calculer la consommation totale
                                        consommation_totale = (kilometrage * consommation_l_100km) / 100
                                        
                                        # Calculer le prix total du carburant
                                        prix_carburant_total = consommation_totale * (prix_carburant_pompe + 500)
                                        
                                        db_query("""
                                            INSERT INTO locations_vehicules (jour_voyage_id, type_voiture_id, type_location,
                                                                            nombre_vehicules, prix_ariary, kilometrage,
                                                                            consommation_carburant, prix_carburant_pompe, prix_carburant_total)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        """, (jour_voyage_id, type_voiture_id, 'Location sans carburant', 1, 0,
                                              kilometrage, consommation_totale, prix_carburant_pompe, prix_carburant_total))
                    except Exception as e:
                        print(f"Erreur lors de l'ajout du jour: {e}")
            
            # Traiter le guide accompagnateur si prix fourni
            prix_guide_par_jour = float(request.form.get('prix_guide_par_jour', 0) or 0)
            
            # Compter le nombre de jours ajoutés
            nombre_jours_guide = len(jours_data) if jours_data else 0
            
            if prix_guide_par_jour > 0 and nombre_jours_guide > 0:
                prix_total_guide = prix_guide_par_jour * nombre_jours_guide
                
                db_query("""
                    INSERT INTO guides_accompagnateurs (devis_id, nombre_guides, nombre_jours, prix_par_jour, prix_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (devis_id, 1, nombre_jours_guide, prix_guide_par_jour, prix_total_guide))
            
            # Traiter le type de location journalière (4x4/Bus) si fourni
            type_location_id = request.form.get('type_location_id')
            if type_location_id:
                type_location_id = int(type_location_id)
                nombre_jours = len(jours_data) if jours_data else 0
                
                if nombre_jours > 0:
                    # Récupérer le prix depuis la table types_locations_journalieres
                    type_location = db_query("""
                        SELECT prix_journalier_sans_carburant FROM types_locations_journalieres WHERE id = %s
                    """, (type_location_id,), fetch_one=True)
                    
                    if type_location:
                        prix_par_jour = float(type_location['prix_journalier_sans_carburant'])
                        prix_total_location = prix_par_jour * nombre_jours
                        
                        # Créer une entrée dans locations_journalieres pour chaque jour
                        for jour_id in created_jour_ids:
                            db_query("""
                                INSERT INTO locations_journalieres (jour_voyage_id, type_location_id, avec_carburant, nombre_vehicules, nombre_jours, prix_total)
                                VALUES (%s, %s, FALSE, 1, 1, %s)
                            """, (jour_id, type_location_id, prix_par_jour))
            
            # Traiter le transfert aéroport si sélectionné
            if request.form.get('transfert_aeroport') == 'on':
                type_transfert = request.form.get('type_transfert', 'Aéroport-Hôtel')
                nb_trajets = 2 if type_transfert == 'Aller-Retour' else 1
                
                # Lire le prix depuis la base de données
                config = db_query("SELECT valeur FROM config_prix WHERE cle = 'transfert_aeroport_par_trajet'", fetch_one=True)
                prix_par_trajet = float(config['valeur']) if config else 250000
                prix_total_transfert = prix_par_trajet * nb_trajets
                
                db_query("""
                    INSERT INTO transferts_aeroport (devis_id, type_transfert, nombre_trajets, prix_par_trajet, prix_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (devis_id, type_transfert, nb_trajets, prix_par_trajet, prix_total_transfert))
            
            # Calculer automatiquement les totaux
            calculer_totaux_devis(devis_id)
            
            flash('Devis créé avec succès', 'success')
            return redirect(url_for('gerer_jours_voyage', devis_id=devis_id))
        else:
            flash('Erreur lors de la création du devis', 'error')
    
    # Récupérer la liste des clients
    clients = db_query("SELECT id, nom, reference FROM clients ORDER BY nom", fetch_all=True)
    
    # Récupérer la liste des itinéraires
    itineraires = db_query("SELECT id, nom FROM itineraires ORDER BY ordre, nom", fetch_all=True)
    
    return render_template('nouveau_devis.html', clients=clients or [], itineraires=itineraires or [])

@app.route('/devis/<int:devis_id>/jours', methods=['GET', 'POST'])
def gerer_jours_voyage(devis_id):
    """Gérer les jours de voyage d'un devis"""
    devis = db_query("""
        SELECT d.*, c.nom as client_nom
        FROM devis d
        LEFT JOIN clients c ON d.client_id = c.id
        WHERE d.id = %s
    """, (devis_id,), fetch_one=True)
    
    if not devis:
        flash('Devis non trouvé', 'error')
        return redirect(url_for('index'))
    
    # Récupérer les itinéraires
    itineraires = db_query("SELECT id, nom FROM itineraires ORDER BY ordre, nom", fetch_all=True)
    
    # Récupérer les jours existants avec leurs hébergements
    jours_raw = db_query("""
        SELECT jv.id, jv.numero_jour, jv.date_jour, jv.itineraire_id,
               i.nom as itineraire_nom
        FROM jours_voyage jv
        LEFT JOIN itineraires i ON jv.itineraire_id = i.id
        WHERE jv.devis_id = %s
        ORDER BY jv.numero_jour
    """, (devis_id,), fetch_all=True)
    
    jours = []
    for jour in (jours_raw or []):
        # Récupérer l'hébergement pour ce jour
        hebergement = db_query("""
            SELECT h.*, ho.nom as hotel_nom
            FROM hebergements h
            LEFT JOIN hotels ho ON h.hotel_id = ho.id
            WHERE h.jour_voyage_id = %s
            LIMIT 1
        """, (jour['id'],), fetch_one=True)
        
        jour_dict = dict(jour)
        if hebergement:
            jour_dict.update({
                'hebergement_id': hebergement['id'],
                'hotel_id': hebergement['hotel_id'],
                'hotel_nom': hebergement['hotel_nom'],
                'type_chambre': hebergement['type_chambre'],
                'nombre_chambres': hebergement['nombre_chambres'],
                'prix_hebergement': hebergement['prix_ariary'],
                'transfert_htl': hebergement['transfert_htl']
            })
        jours.append(jour_dict)
    
    return render_template('gerer_jours_voyage.html', 
                         devis=devis,
                         itineraires=itineraires or [],
                         jours=jours or [])

@app.route('/clients')
def liste_clients():
    """Liste des clients"""
    clients = db_query("""
        SELECT c.*, COUNT(d.id) as nombre_devis
        FROM clients c
        LEFT JOIN devis d ON c.id = d.client_id
        GROUP BY c.id
        ORDER BY c.nom
    """, fetch_all=True)
    
    return render_template('clients.html', clients=clients or [])

@app.route('/clients/nouveau', methods=['GET', 'POST'])
def nouveau_client():
    """Créer un nouveau client"""
    if request.method == 'POST':
        reference = request.form.get('reference')
        nom = request.form.get('nom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        
        result = db_query("""
            INSERT INTO clients (reference, nom, email, telephone)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (reference, nom, email, telephone), fetch_one=True)
        
        if result:
            flash('Client créé avec succès', 'success')
            return redirect(url_for('liste_clients'))
        else:
            flash('Erreur lors de la création du client', 'error')
    
    return render_template('nouveau_client.html')

@app.route('/api/itineraires', methods=['GET'])
def api_itineraires():
    """Retourne la liste des itinéraires"""
    itineraires = db_query("""
        SELECT id, nom FROM itineraires ORDER BY ordre, nom
    """, fetch_all=True)
    
    return jsonify([{'id': it['id'], 'nom': it['nom']} for it in (itineraires or [])])

@app.route('/api/itineraires/<int:itineraire_id>/hotels', methods=['GET'])
def api_hotels_itineraire(itineraire_id):
    """Retourne la liste des hôtels pour un itinéraire donné"""
    hotels = db_query("""
        SELECT id, nom, prix_double, prix_triple
        FROM hotels
        WHERE itineraire_id = %s AND actif = TRUE
        ORDER BY nom
    """, (itineraire_id,), fetch_all=True)
    
    return jsonify([{
        'id': h['id'],
        'nom': h['nom'],
        'prix_double': float(h['prix_double']) if h['prix_double'] else 0,
        'prix_triple': float(h['prix_triple']) if h['prix_triple'] else 0
    } for h in (hotels or [])])

@app.route('/api/itineraires/<int:itineraire_id>/visites', methods=['GET'])
def api_visites_itineraire(itineraire_id):
    """Retourne la liste des visites pour un itinéraire donné"""
    visites = db_query("""
        SELECT id, nom, prix_par_personne, prix_par_voiture, type_prix,
               guidage_obligatoire, guidage_prix_base, guidage_nb_personnes_base,
               guidage_type_calcul, taxe_communale
        FROM visites
        WHERE itineraire_id = %s AND actif = TRUE
        ORDER BY ordre, nom
    """, (itineraire_id,), fetch_all=True)
    
    return jsonify([{
        'id': v['id'],
        'nom': v['nom'],
        'prix_par_personne': float(v['prix_par_personne']) if v['prix_par_personne'] else 0,
        'prix_par_voiture': float(v['prix_par_voiture']) if v['prix_par_voiture'] else 0,
        'type_prix': v['type_prix'],
        'guidage_obligatoire': v['guidage_obligatoire'],
        'guidage_prix_base': float(v['guidage_prix_base']) if v['guidage_prix_base'] else 0,
        'guidage_nb_personnes_base': int(v['guidage_nb_personnes_base']) if v['guidage_nb_personnes_base'] else 0,
        'guidage_type_calcul': v['guidage_type_calcul'],
        'taxe_communale': float(v['taxe_communale']) if v['taxe_communale'] else 0
    } for v in (visites or [])])

@app.route('/api/types_voitures', methods=['GET'])
def api_types_voitures():
    """Retourne la liste des types de voitures"""
    types = db_query("""
        SELECT id, nom, consommation_l_100km
        FROM types_voitures
        WHERE actif = TRUE
        ORDER BY ordre, nom
    """, fetch_all=True)
    
    return jsonify([{
        'id': t['id'],
        'nom': t['nom'],
        'consommation_l_100km': float(t['consommation_l_100km'])
    } for t in (types or [])])

@app.route('/api/calculer_guidage', methods=['POST'])
def api_calculer_guidage():
    """Calcule le prix du guidage selon les règles"""
    data = request.get_json()
    nb_personnes = int(data.get('nb_personnes', 0))
    prix_base = float(data.get('prix_base', 0))
    nb_personnes_base = int(data.get('nb_personnes_base', 4))
    type_calcul = data.get('type_calcul', 'par_groupe')
    
    if type_calcul == 'par_personne':
        prix_total = prix_base * nb_personnes
    elif type_calcul == 'par_voiture':
        prix_total = prix_base  # Prix fixe par voiture
    else:  # par_groupe
        # Calculer le nombre de groupes nécessaires
        # Ex: 1-4 personnes = 1 groupe, 5-8 = 2 groupes, etc.
        nb_groupes = (nb_personnes + nb_personnes_base - 1) // nb_personnes_base
        prix_total = prix_base * nb_groupes
    
    return jsonify({
        'prix_total': prix_total,
        'nb_groupes': nb_groupes if type_calcul == 'par_groupe' else 1
    })

@app.route('/api/calculer_carburant', methods=['POST'])
def api_calculer_carburant():
    """Calcule la consommation et le prix du carburant"""
    data = request.get_json()
    kilometrage = float(data.get('kilometrage', 0))
    consommation_l_100km = float(data.get('consommation_l_100km', 0))
    prix_pompe = float(data.get('prix_pompe', 0))
    
    # Calcul: (kilometrage * consommation) / 100
    consommation_totale = (kilometrage * consommation_l_100km) / 100
    
    # Prix: consommation * (prix_pompe + 500)
    prix_total = consommation_totale * (prix_pompe + 500)
    
    return jsonify({
        'consommation_totale': round(consommation_totale, 2),
        'prix_total': round(prix_total, 2)
    })

@app.route('/api/devis/<int:devis_id>/jours', methods=['GET'])
def api_jours_devis(devis_id):
    """Retourne les jours de voyage d'un devis"""
    jours = db_query("""
        SELECT jv.*, i.nom as itineraire_nom
        FROM jours_voyage jv
        LEFT JOIN itineraires i ON jv.itineraire_id = i.id
        WHERE jv.devis_id = %s
        ORDER BY jv.numero_jour
    """, (devis_id,), fetch_all=True)
    
    return jsonify([dict(jour) for jour in (jours or [])])

@app.route('/api/devis/<int:devis_id>/jours', methods=['POST'])
def ajouter_jour_devis(devis_id):
    """Ajoute un jour de voyage à un devis"""
    data = request.get_json()
    
    numero_jour = int(data.get('numero_jour', 0))
    itineraire_id = data.get('itineraire_id')
    date_jour = data.get('date_jour')
    
    if not numero_jour:
        return jsonify({'error': 'Numéro de jour requis'}), 400
    
    # Vérifier que le devis existe
    devis = db_query("SELECT id FROM devis WHERE id = %s", (devis_id,), fetch_one=True)
    if not devis:
        return jsonify({'error': 'Devis non trouvé'}), 404
    
    # Créer ou mettre à jour le jour de voyage
    result = db_query("""
        INSERT INTO jours_voyage (devis_id, numero_jour, itineraire_id, date_jour, ordre)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (devis_id, numero_jour)
        DO UPDATE SET itineraire_id = EXCLUDED.itineraire_id, date_jour = EXCLUDED.date_jour
        RETURNING id
    """, (devis_id, numero_jour, itineraire_id, date_jour, numero_jour), fetch_one=True)
    
    if result:
        return jsonify({'success': True, 'jour_id': result['id']})
    else:
        return jsonify({'error': 'Erreur lors de la création du jour'}), 500

@app.route('/api/devis/<int:devis_id>/jours/<int:jour_id>/hebergement', methods=['POST'])
def ajouter_hebergement_jour(devis_id, jour_id):
    """Ajoute un hébergement à un jour de voyage"""
    data = request.get_json()
    
    hotel_id = data.get('hotel_id')
    type_chambre = data.get('type_chambre', 'Double')
    nombre_chambres = int(data.get('nombre_chambres', 1))
    transfert_htl = float(data.get('transfert_htl', 0))
    
    # Récupérer le prix de l'hôtel
    hotel = db_query("""
        SELECT prix_double, prix_triple FROM hotels WHERE id = %s
    """, (hotel_id,), fetch_one=True)
    
    if not hotel:
        return jsonify({'error': 'Hôtel non trouvé'}), 404
    
    # Calculer le prix selon le type de chambre
    if type_chambre == 'Triple' and hotel['prix_triple']:
        prix_chambre = float(hotel['prix_triple'])
    else:
        prix_chambre = float(hotel['prix_double'])
    
    prix_total = prix_chambre * nombre_chambres
    
    # Récupérer le nom de l'hôtel
    hotel_nom = db_query("SELECT nom FROM hotels WHERE id = %s", (hotel_id,), fetch_one=True)
    nom_hotel = hotel_nom['nom'] if hotel_nom else None
    
    # Créer ou mettre à jour l'hébergement
    result = db_query("""
        INSERT INTO hebergements (jour_voyage_id, hotel_id, type_chambre, nom_hotel, nombre_chambres, prix_ariary, transfert_htl)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id
    """, (jour_id, hotel_id, type_chambre, nom_hotel, nombre_chambres, prix_total, transfert_htl), fetch_one=True)
    
    if result:
        # Recalculer les totaux automatiquement
        calculer_totaux_devis(devis_id)
        
        return jsonify({
            'success': True,
            'hebergement_id': result['id'],
            'prix_total': prix_total
        })
    else:
        return jsonify({'error': 'Erreur lors de l\'ajout de l\'hébergement'}), 500

@app.route('/api/devis/<int:devis_id>/jours/<int:jour_id>/visite', methods=['POST'])
def ajouter_visite_jour(devis_id, jour_id):
    """Ajoute une visite à un jour de voyage"""
    data = request.get_json()
    
    visite_id = data.get('visite_id')
    nombre_personnes = int(data.get('nombre_personnes', 1))
    
    if not visite_id:
        return jsonify({'error': 'Visite requise'}), 400
    
    # Récupérer les informations de la visite
    visite = db_query("""
        SELECT id, nom, prix_par_personne, prix_par_voiture, type_prix,
               guidage_obligatoire, guidage_prix_base, guidage_nb_personnes_base,
               guidage_type_calcul, taxe_communale
        FROM visites WHERE id = %s
    """, (visite_id,), fetch_one=True)
    
    if not visite:
        return jsonify({'error': 'Visite non trouvée'}), 404
    
    # Calculer le prix d'entrée
    prix_entree = 0
    if visite['type_prix'] == 'personne':
        prix_entree = float(visite['prix_par_personne']) * nombre_personnes
    elif visite['type_prix'] in ('voiture', 'bateau'):
        prix_entree = float(visite['prix_par_voiture'])
    
    # Calculer le prix du guidage si obligatoire
    prix_guidage = 0
    if visite['guidage_obligatoire'] and visite['guidage_prix_base']:
        guidage_prix_base = float(visite['guidage_prix_base'])
        guidage_nb_base = int(visite['guidage_nb_personnes_base'])
        guidage_type = visite['guidage_type_calcul']
        
        if guidage_type == 'par_personne':
            prix_guidage = guidage_prix_base * nombre_personnes
        elif guidage_type == 'par_voiture':
            prix_guidage = guidage_prix_base
        else:  # par_groupe
            nb_groupes = (nombre_personnes + guidage_nb_base - 1) // guidage_nb_base
            prix_guidage = guidage_prix_base * nb_groupes
    
    # Calculer la taxe communale
    prix_taxe = float(visite['taxe_communale'] or 0) * nombre_personnes
    
    # Prix total de la visite
    prix_total = prix_entree + prix_guidage + prix_taxe
    
    # Créer ou mettre à jour la visite du jour
    result = db_query("""
        INSERT INTO visites_jour (
            jour_voyage_id, visite_id, nombre_personnes, nombre_voitures,
            prix_entree, prix_guidage, prix_taxe_communale, prix_total
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id
    """, (jour_id, visite_id, nombre_personnes, 0, prix_entree, prix_guidage, prix_taxe, prix_total), fetch_one=True)
    
    if result:
        # Recalculer les totaux automatiquement
        calculer_totaux_devis(devis_id)
        
        return jsonify({
            'success': True,
            'visite_id': result['id'],
            'prix_total': prix_total
        })
    else:
        return jsonify({'error': 'Erreur lors de l\'ajout de la visite'}), 500

@app.route('/api/devis/<int:devis_id>/jours/<int:jour_id>/location', methods=['POST'])
def ajouter_location_jour(devis_id, jour_id):
    """Ajoute une location de véhicule avec calcul du carburant à un jour de voyage"""
    data = request.get_json()
    
    type_voiture_id = data.get('type_voiture_id')
    kilometrage = float(data.get('kilometrage', 0))
    prix_carburant_pompe = float(data.get('prix_carburant_pompe', 0))
    prix_location = float(data.get('prix_location', 0))
    nombre_vehicules = int(data.get('nombre_vehicules', 1))
    
    if not type_voiture_id:
        return jsonify({'error': 'Type de voiture requis'}), 400
    
    # Récupérer la consommation du type de voiture
    type_voiture = db_query("""
        SELECT consommation_l_100km FROM types_voitures WHERE id = %s
    """, (type_voiture_id,), fetch_one=True)
    
    if not type_voiture:
        return jsonify({'error': 'Type de voiture non trouvé'}), 404
    
    consommation_l_100km = float(type_voiture['consommation_l_100km'])
    
    # Calculer la consommation totale
    consommation_totale = (kilometrage * consommation_l_100km) / 100
    
    # Calculer le prix total du carburant
    prix_carburant_total = consommation_totale * (prix_carburant_pompe + 500)
    
    # Créer ou mettre à jour la location
    result = db_query("""
        INSERT INTO locations_vehicules (
            jour_voyage_id, type_voiture_id, type_location, nombre_vehicules,
            prix_ariary, kilometrage, consommation_carburant,
            prix_carburant_pompe, prix_carburant_total
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id
    """, (jour_id, type_voiture_id, 'Location sans carburant', nombre_vehicules,
          prix_location, kilometrage, consommation_totale, prix_carburant_pompe, prix_carburant_total), fetch_one=True)
    
    if result:
        # Recalculer les totaux automatiquement
        calculer_totaux_devis(devis_id)
        
        return jsonify({
            'success': True,
            'location_id': result['id'],
            'consommation_totale': consommation_totale,
            'prix_carburant_total': prix_carburant_total
        })
    else:
        return jsonify({'error': 'Erreur lors de l\'ajout de la location'}), 500

def calculer_totaux_devis(devis_id):
    """Fonction utilitaire pour calculer les totaux d'un devis"""
    devis = db_query("SELECT * FROM devis WHERE id = %s", (devis_id,), fetch_one=True)
    
    if not devis:
        return None
    
    # Calculer le total depuis les coûts par catégorie
    couts = db_query("""
        SELECT SUM(montant_ariary) as total
        FROM couts_devis
        WHERE devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les hébergements
    hebergements = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0) + COALESCE(transfert_htl, 0)) as total
        FROM hebergements h
        JOIN jours_voyage jv ON h.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les transferts
    transferts = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0)) as total
        FROM transferts t
        JOIN jours_voyage jv ON t.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les locations HORS carburant (prix_ariary seulement)
    locations_hors_carburant = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0)) as total
        FROM locations_vehicules l
        JOIN jours_voyage jv ON l.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les guidages
    guidages = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0)) as total
        FROM guidages g
        JOIN jours_voyage jv ON g.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les réserves/parcs
    reserves = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0)) as total
        FROM reserves_parcs r
        JOIN jours_voyage jv ON r.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les repas
    repas = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0)) as total
        FROM repas r
        JOIN jours_voyage jv ON r.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les imprévus
    imprevus = db_query("""
        SELECT SUM(COALESCE(prix_ariary, 0)) as total
        FROM imprevus
        WHERE devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les visites
    visites = db_query("""
        SELECT SUM(COALESCE(prix_total, 0)) as total
        FROM visites_jour vj
        JOIN jours_voyage jv ON vj.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis le carburant (locations avec prix_carburant_total)
    carburant = db_query("""
        SELECT SUM(COALESCE(prix_carburant_total, 0)) as total
        FROM locations_vehicules l
        JOIN jours_voyage jv ON l.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les locations journalières SANS carburant
    locations_journalieres_sans_carburant = db_query("""
        SELECT SUM(COALESCE(prix_total, 0)) as total
        FROM locations_journalieres lj
        JOIN jours_voyage jv ON lj.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s AND lj.avec_carburant = FALSE
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les locations journalières AVEC carburant
    locations_journalieres_avec_carburant = db_query("""
        SELECT SUM(COALESCE(prix_total, 0)) as total
        FROM locations_journalieres lj
        JOIN jours_voyage jv ON lj.jour_voyage_id = jv.id
        WHERE jv.devis_id = %s AND lj.avec_carburant = TRUE
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les réserves/parcs (inclus dans les visites car ils ont guidage obligatoire)
    # Les réserves/parcs sont déjà inclus dans visites_jour via les visites
    
    # Calculer le total depuis les transferts aéroport
    transferts_aeroport = db_query("""
        SELECT SUM(COALESCE(prix_total, 0)) as total
        FROM transferts_aeroport
        WHERE devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer le total depuis les guides accompagnateurs
    guides_accompagnateurs = db_query("""
        SELECT SUM(COALESCE(prix_total, 0)) as total
        FROM guides_accompagnateurs
        WHERE devis_id = %s
    """, (devis_id,), fetch_one=True)
    
    # Calculer selon la nouvelle formule :
    # Prix total hébergement par jour + Total consommation en carburant par jour + 
    # Total des prix des visites (tous les visites et les entrées parc et réserves avec guidage obligatoire par jour) + 
    # Total des prix de location hors carburant + location journalière avec carburant + 
    # Total des prix du guide accompagnateur + la totalité des imprévus
    
    total_hebergements = float(hebergements['total']) if hebergements and hebergements['total'] else 0
    total_carburant = float(carburant['total']) if carburant and carburant['total'] else 0
    total_visites = float(visites['total']) if visites and visites['total'] else 0
    total_locations_hors_carburant = float(locations_hors_carburant['total']) if locations_hors_carburant and locations_hors_carburant['total'] else 0
    total_locations_journalieres_sans_carburant = float(locations_journalieres_sans_carburant['total']) if locations_journalieres_sans_carburant and locations_journalieres_sans_carburant['total'] else 0
    total_locations_journalieres_avec_carburant = float(locations_journalieres_avec_carburant['total']) if locations_journalieres_avec_carburant and locations_journalieres_avec_carburant['total'] else 0
    total_guides_accompagnateurs = float(guides_accompagnateurs['total']) if guides_accompagnateurs and guides_accompagnateurs['total'] else 0
    total_imprevus = float(imprevus['total']) if imprevus and imprevus['total'] else 0
    
    # Somme de tous les services selon la formule demandée
    somme_services = (
        total_hebergements +  # Prix total hébergement par jour
        total_carburant +  # Total consommation en carburant par jour
        total_visites +  # Total des prix des visites (tous les visites et les entrées parc et réserves avec guidage obligatoire par jour)
        total_locations_hors_carburant +  # Total des prix de location hors carburant
        total_locations_journalieres_sans_carburant +  # Location journalière sans carburant
        total_locations_journalieres_avec_carburant +  # Location journalière avec carburant
        total_guides_accompagnateurs +  # Total des prix du guide accompagnateur
        total_imprevus  # La totalité des imprévus
    )
    
    # Appliquer la marge
    marge_percent = float(devis.get('marge_percent', 0) or 0)
    if marge_percent > 0:
        total_ariary = somme_services * (1 + marge_percent / 100)
    else:
        total_ariary = somme_services
    
    # Calculer le total en Euro
    taux_change = float(devis['taux_change'])
    total_euro = total_ariary / taux_change if taux_change else 0
    
    # Calculer la marge en Ariary
    marge_ariary = total_ariary - somme_services
    
    # Mettre à jour le devis
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE devis
                SET total_ariary = %s, total_euro = %s, marge = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (total_ariary, total_euro, marge_ariary, devis_id))
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            print(f"Erreur lors de la mise à jour du devis: {e}")
        finally:
            conn.close()
    
    return {
        'total_ariary': total_ariary,
        'total_euro': round(total_euro, 2),
        'taux_change': taux_change,
        'marge_percent': marge_percent,
        'marge_ariary': marge_ariary,
        'somme_services': somme_services
    }

@app.route('/api/devis/<int:devis_id>/calculer', methods=['POST'])
def calculer_devis(devis_id):
    """Calcule les totaux d'un devis (API endpoint)"""
    result = calculer_totaux_devis(devis_id)
    
    if not result:
        return jsonify({'error': 'Devis non trouvé'}), 404
    
    return jsonify(result)

@app.route('/api/types_locations_journalieres', methods=['GET'])
def api_types_locations_journalieres():
    """Retourne la liste des types de locations journalières"""
    types = db_query("""
        SELECT id, nom, prix_journalier_sans_carburant, prix_journalier_avec_carburant
        FROM types_locations_journalieres
        WHERE actif = TRUE
        ORDER BY nom
    """, fetch_all=True)
    
    return jsonify([{
        'id': t['id'],
        'nom': t['nom'],
        'prix_journalier_sans_carburant': float(t['prix_journalier_sans_carburant']),
        'prix_journalier_avec_carburant': float(t['prix_journalier_avec_carburant'])
    } for t in (types or [])])

@app.route('/api/devis/<int:devis_id>/transfert_aeroport', methods=['POST'])
def ajouter_transfert_aeroport(devis_id):
    """Ajoute un transfert aéroport au devis"""
    data = request.get_json()
    
    type_transfert = data.get('type_transfert', 'Aéroport-Hôtel')
    nombre_trajets = int(data.get('nombre_trajets', 1))
    
    # Lire le prix depuis la base de données
    config = db_query("SELECT valeur FROM config_prix WHERE cle = 'transfert_aeroport_par_trajet'", fetch_one=True)
    prix_par_trajet = float(config['valeur']) if config else 250000  # Prix par défaut si non trouvé
    
    prix_total = prix_par_trajet * nombre_trajets
    
    result = db_query("""
        INSERT INTO transferts_aeroport (devis_id, type_transfert, nombre_trajets, prix_par_trajet, prix_total)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (devis_id, type_transfert, nombre_trajets, prix_par_trajet, prix_total), fetch_one=True)
    
    if result:
        calculer_totaux_devis(devis_id)
        return jsonify({'success': True, 'transfert_id': result['id'], 'prix_total': prix_total})
    else:
        return jsonify({'error': 'Erreur lors de l\'ajout du transfert'}), 500

@app.route('/api/devis/<int:devis_id>/guide_accompagnateur', methods=['POST'])
def ajouter_guide_accompagnateur(devis_id):
    """Ajoute un guide accompagnateur au devis"""
    data = request.get_json()
    
    nombre_guides = int(data.get('nombre_guides', 1))
    nombre_jours = int(data.get('nombre_jours', 1))
    
    # Lire le prix depuis la base de données
    config = db_query("SELECT valeur FROM config_prix WHERE cle = 'guide_accompagnateur_par_jour'", fetch_one=True)
    prix_par_jour = float(config['valeur']) if config else 280000  # Prix par défaut si non trouvé
    
    prix_total = prix_par_jour * nombre_guides * nombre_jours
    
    result = db_query("""
        INSERT INTO guides_accompagnateurs (devis_id, nombre_guides, nombre_jours, prix_par_jour, prix_total)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (devis_id, nombre_guides, nombre_jours, prix_par_jour, prix_total), fetch_one=True)
    
    if result:
        calculer_totaux_devis(devis_id)
        return jsonify({'success': True, 'guide_id': result['id'], 'prix_total': prix_total})
    else:
        return jsonify({'error': 'Erreur lors de l\'ajout du guide'}), 500

@app.route('/api/devis/<int:devis_id>/jours/<int:jour_id>/location_journaliere', methods=['POST'])
def ajouter_location_journaliere(devis_id, jour_id):
    """Ajoute une location journalière à un jour de voyage"""
    data = request.get_json()
    
    type_location_id = data.get('type_location_id')
    avec_carburant = data.get('avec_carburant', False)
    nombre_vehicules = int(data.get('nombre_vehicules', 1))
    nombre_jours = int(data.get('nombre_jours', 1))
    
    if not type_location_id:
        return jsonify({'error': 'Type de location requis'}), 400
    
    # Récupérer le prix du type de location
    type_location = db_query("""
        SELECT prix_journalier_sans_carburant, prix_journalier_avec_carburant
        FROM types_locations_journalieres WHERE id = %s
    """, (type_location_id,), fetch_one=True)
    
    if not type_location:
        return jsonify({'error': 'Type de location non trouvé'}), 404
    
    if avec_carburant:
        prix_journalier = float(type_location['prix_journalier_avec_carburant'])
    else:
        prix_journalier = float(type_location['prix_journalier_sans_carburant'])
    
    prix_total = prix_journalier * nombre_vehicules * nombre_jours
    
    result = db_query("""
        INSERT INTO locations_journalieres (
            jour_voyage_id, type_location_id, avec_carburant, nombre_vehicules, nombre_jours, prix_total
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (jour_id, type_location_id, avec_carburant, nombre_vehicules, nombre_jours, prix_total), fetch_one=True)
    
    if result:
        calculer_totaux_devis(devis_id)
        return jsonify({'success': True, 'location_id': result['id'], 'prix_total': prix_total})
    else:
        return jsonify({'error': 'Erreur lors de l\'ajout de la location'}), 500

@app.route('/api/devis/<int:devis_id>', methods=['DELETE'])
def supprimer_devis(devis_id):
    """Supprime un devis et toutes ses données associées"""
    # Vérifier que le devis existe
    devis = db_query("SELECT id, reference FROM devis WHERE id = %s", (devis_id,), fetch_one=True)
    
    if not devis:
        return jsonify({'error': 'Devis non trouvé'}), 404
    
    # Supprimer le devis (les données associées seront supprimées automatiquement grâce à ON DELETE CASCADE)
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM devis WHERE id = %s", (devis_id,))
        conn.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': f'Devis "{devis["reference"]}" supprimé avec succès'
        })
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la suppression du devis: {e}")
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/config_prix', methods=['GET'])
def api_config_prix():
    """Retourne les prix de configuration depuis la base de données"""
    configs = db_query("""
        SELECT cle, valeur, description FROM config_prix
    """, fetch_all=True)
    
    result = {}
    for c in (configs or []):
        result[c['cle']] = {
            'valeur': float(c['valeur']),
            'description': c['description']
        }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

