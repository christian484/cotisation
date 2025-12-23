-- Schéma de base de données pour le système de devis de voyage à Madagascar
-- Version 3 avec visites par localité, types de voitures et calcul de carburant

-- Table des clients
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    reference VARCHAR(100) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telephone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des itinéraires
CREATE TABLE IF NOT EXISTS itineraires (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    ordre INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des hôtels
CREATE TABLE IF NOT EXISTS hotels (
    id SERIAL PRIMARY KEY,
    itineraire_id INTEGER REFERENCES itineraires(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    prix_double DECIMAL(15, 2) NOT NULL DEFAULT 0,
    prix_triple DECIMAL(15, 2) DEFAULT 0,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(itineraire_id, nom)
);

-- Table des visites/lieux de visite par itinéraire
CREATE TABLE IF NOT EXISTS visites (
    id SERIAL PRIMARY KEY,
    itineraire_id INTEGER REFERENCES itineraires(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    prix_par_personne DECIMAL(15, 2) DEFAULT 0,
    prix_par_voiture DECIMAL(15, 2) DEFAULT 0, -- Pour les visites au prix par voiture
    type_prix VARCHAR(20) DEFAULT 'personne', -- 'personne' ou 'voiture'
    guidage_obligatoire BOOLEAN DEFAULT FALSE,
    guidage_prix_base DECIMAL(15, 2) DEFAULT 0, -- Prix de base pour le guidage
    guidage_nb_personnes_base INTEGER DEFAULT 4, -- Nombre de personnes pour le prix de base (ex: 1-4 personnes)
    guidage_type_calcul VARCHAR(50) DEFAULT 'par_groupe', -- 'par_groupe', 'par_personne'
    taxe_communale DECIMAL(15, 2) DEFAULT 0, -- Taxe communale obligatoire par personne
    ordre INTEGER DEFAULT 0,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(itineraire_id, nom)
);

-- Table des types de voitures
CREATE TABLE IF NOT EXISTS types_voitures (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    consommation_l_100km DECIMAL(5, 2) NOT NULL, -- Consommation en litres pour 100 km
    ordre INTEGER DEFAULT 0,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des devis
CREATE TABLE IF NOT EXISTS devis (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    reference VARCHAR(100) UNIQUE NOT NULL,
    date_cotation DATE NOT NULL,
    nombre_personnes INTEGER NOT NULL,
    nombre_adultes INTEGER DEFAULT 0,
    nombre_enfants INTEGER DEFAULT 0,
    nombre_bebes INTEGER DEFAULT 0,
    nombre_chambres INTEGER DEFAULT 0,
    taux_change DECIMAL(10, 2) NOT NULL,
    total_ariary DECIMAL(15, 2) DEFAULT 0,
    total_euro DECIMAL(10, 2) DEFAULT 0,
    marge DECIMAL(15, 2) DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'brouillon',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des catégories de coûts
CREATE TABLE IF NOT EXISTS categories_couts (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    ordre INTEGER DEFAULT 0
);

-- Table des coûts par catégorie pour chaque devis
CREATE TABLE IF NOT EXISTS couts_devis (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER REFERENCES devis(id) ON DELETE CASCADE,
    categorie_id INTEGER REFERENCES categories_couts(id),
    montant_ariary DECIMAL(15, 2) NOT NULL DEFAULT 0,
    montant_euro DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des jours de voyage (itinéraire)
CREATE TABLE IF NOT EXISTS jours_voyage (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER REFERENCES devis(id) ON DELETE CASCADE,
    numero_jour INTEGER NOT NULL,
    date_jour INTEGER,
    itineraire_id INTEGER REFERENCES itineraires(id),
    destination VARCHAR(255),
    ordre INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(devis_id, numero_jour)
);

-- Table des transferts
CREATE TABLE IF NOT EXISTS transferts (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_transfert VARCHAR(50),
    nombre_voitures INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    nombre_personnes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des locations de véhicules (modifiée pour inclure type de voiture et carburant)
CREATE TABLE IF NOT EXISTS locations_vehicules (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_voiture_id INTEGER REFERENCES types_voitures(id),
    type_location VARCHAR(50),
    nombre_vehicules INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    kilometrage INTEGER DEFAULT 0,
    consommation_carburant DECIMAL(10, 2) DEFAULT 0, -- Calculé automatiquement
    prix_carburant_pompe DECIMAL(10, 2) DEFAULT 0, -- Prix à la pompe (saisi manuellement)
    prix_carburant_total DECIMAL(15, 2) DEFAULT 0, -- Calculé: consommation * (prix_pompe + 500)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des guidages (modifiée pour gérer les règles de calcul)
CREATE TABLE IF NOT EXISTS guidages (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    visite_id INTEGER REFERENCES visites(id) ON DELETE SET NULL,
    type_guidage VARCHAR(100),
    nombre_personnes INTEGER DEFAULT 0,
    nombre_guides INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des visites effectuées par jour
CREATE TABLE IF NOT EXISTS visites_jour (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    visite_id INTEGER REFERENCES visites(id) ON DELETE CASCADE,
    nombre_personnes INTEGER DEFAULT 0,
    nombre_voitures INTEGER DEFAULT 0,
    prix_entree DECIMAL(15, 2) DEFAULT 0, -- Prix calculé pour l'entrée
    prix_guidage DECIMAL(15, 2) DEFAULT 0, -- Prix calculé pour le guidage
    prix_taxe_communale DECIMAL(15, 2) DEFAULT 0, -- Prix calculé pour la taxe communale
    prix_total DECIMAL(15, 2) DEFAULT 0, -- Prix total de la visite
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des réserves et parcs
CREATE TABLE IF NOT EXISTS reserves_parcs (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    nom_reserve VARCHAR(255),
    nom_parc VARCHAR(255),
    nombre_personnes INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des hébergements
CREATE TABLE IF NOT EXISTS hebergements (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    hotel_id INTEGER REFERENCES hotels(id) ON DELETE SET NULL,
    type_chambre VARCHAR(50),
    nom_hotel VARCHAR(255),
    nombre_chambres INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    transfert_htl DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des repas
CREATE TABLE IF NOT EXISTS repas (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_repas VARCHAR(50),
    nombre_personnes INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des imprévus
CREATE TABLE IF NOT EXISTS imprevus (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER REFERENCES devis(id) ON DELETE CASCADE,
    description VARCHAR(255),
    nombre INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_devis_client ON devis(client_id);
CREATE INDEX IF NOT EXISTS idx_devis_reference ON devis(reference);
CREATE INDEX IF NOT EXISTS idx_jours_voyage_devis ON jours_voyage(devis_id);
CREATE INDEX IF NOT EXISTS idx_jours_voyage_itineraire ON jours_voyage(itineraire_id);
CREATE INDEX IF NOT EXISTS idx_couts_devis_devis ON couts_devis(devis_id);
CREATE INDEX IF NOT EXISTS idx_transferts_jour ON transferts(jour_voyage_id);
CREATE INDEX IF NOT EXISTS idx_hebergements_jour ON hebergements(jour_voyage_id);
CREATE INDEX IF NOT EXISTS idx_hebergements_hotel ON hebergements(hotel_id);
CREATE INDEX IF NOT EXISTS idx_hotels_itineraire ON hotels(itineraire_id);
CREATE INDEX IF NOT EXISTS idx_visites_itineraire ON visites(itineraire_id);
CREATE INDEX IF NOT EXISTS idx_visites_jour_jour ON visites_jour(jour_voyage_id);
CREATE INDEX IF NOT EXISTS idx_visites_jour_visite ON visites_jour(visite_id);
CREATE INDEX IF NOT EXISTS idx_locations_type_voiture ON locations_vehicules(type_voiture_id);

-- Insertion des catégories de coûts par défaut
INSERT INTO categories_couts (nom, ordre) VALUES
    ('Pirogue', 1),
    ('Bateau', 2),
    ('Location', 3),
    ('Guidage', 4),
    ('Carburant', 5),
    ('Reserves', 6),
    ('Parcs', 7),
    ('hebergements', 8),
    ('Repas', 9),
    ('Imprevu', 10),
    ('Visites', 11),
    ('Taxes communales', 12)
ON CONFLICT (nom) DO NOTHING;

