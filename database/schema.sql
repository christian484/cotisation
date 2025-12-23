-- Schéma de base de données pour le système de devis de voyage à Madagascar

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
    statut VARCHAR(50) DEFAULT 'brouillon', -- brouillon, envoyé, accepté, refusé
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
    date_jour INTEGER NOT NULL, -- Jour du mois (17, 18, etc.)
    destination VARCHAR(255),
    ordre INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(devis_id, numero_jour)
);

-- Table des transferts
CREATE TABLE IF NOT EXISTS transferts (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_transfert VARCHAR(50), -- Transfert, Pirogue, Bateau
    nombre_voitures INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    nombre_personnes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des locations de véhicules
CREATE TABLE IF NOT EXISTS locations_vehicules (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_location VARCHAR(50), -- Location sans carburant
    nombre_vehicules INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
    kilometrage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des guidages
CREATE TABLE IF NOT EXISTS guidages (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_guidage VARCHAR(100),
    nombre_guides INTEGER DEFAULT 0,
    prix_ariary DECIMAL(15, 2) DEFAULT 0,
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
    type_chambre VARCHAR(50), -- Double, Triple
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
    type_repas VARCHAR(50), -- PD (Petit-déjeuner), DN (Déjeuner), DJ (Dîner), Vinette
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
CREATE INDEX IF NOT EXISTS idx_couts_devis_devis ON couts_devis(devis_id);
CREATE INDEX IF NOT EXISTS idx_transferts_jour ON transferts(jour_voyage_id);
CREATE INDEX IF NOT EXISTS idx_hebergements_jour ON hebergements(jour_voyage_id);

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
    ('Imprevu', 10)
ON CONFLICT (nom) DO NOTHING;

