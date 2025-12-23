-- Script de migration vers la version 4 avec locations journalières, transferts aéroport et guides accompagnateurs

-- Table des types de locations journalières
CREATE TABLE IF NOT EXISTS types_locations_journalieres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    prix_journalier_sans_carburant DECIMAL(15, 2) DEFAULT 0,
    prix_journalier_avec_carburant DECIMAL(15, 2) DEFAULT 0,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des locations journalières par jour
CREATE TABLE IF NOT EXISTS locations_journalieres (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    type_location_id INTEGER REFERENCES types_locations_journalieres(id),
    avec_carburant BOOLEAN DEFAULT FALSE,
    nombre_vehicules INTEGER DEFAULT 1,
    nombre_jours INTEGER DEFAULT 1,
    prix_total DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des transferts aéroport
CREATE TABLE IF NOT EXISTS transferts_aeroport (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER REFERENCES devis(id) ON DELETE CASCADE,
    type_transfert VARCHAR(50) DEFAULT 'Aéroport-Hôtel', -- 'Aéroport-Hôtel' ou 'Hôtel-Aéroport'
    nombre_trajets INTEGER DEFAULT 1,
    prix_par_trajet DECIMAL(15, 2) DEFAULT 0,
    prix_total DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des guides accompagnateurs
CREATE TABLE IF NOT EXISTS guides_accompagnateurs (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER REFERENCES devis(id) ON DELETE CASCADE,
    nombre_guides INTEGER DEFAULT 1,
    nombre_jours INTEGER DEFAULT 1,
    prix_par_jour DECIMAL(15, 2) DEFAULT 0,
    prix_total DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajouter le champ marge_percent dans la table devis si elle n'existe pas
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'devis' AND column_name = 'marge_percent'
    ) THEN
        ALTER TABLE devis ADD COLUMN marge_percent DECIMAL(5, 2) DEFAULT 0;
    END IF;
END $$;

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_locations_journalieres_jour ON locations_journalieres(jour_voyage_id);
CREATE INDEX IF NOT EXISTS idx_transferts_aeroport_devis ON transferts_aeroport(devis_id);
CREATE INDEX IF NOT EXISTS idx_guides_accompagnateurs_devis ON guides_accompagnateurs(devis_id);

