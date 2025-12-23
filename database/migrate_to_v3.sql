-- Script de migration vers la version 3 avec visites, types de voitures et carburant
-- À exécuter si vous avez déjà une base de données existante

-- Créer la table des visites si elle n'existe pas
CREATE TABLE IF NOT EXISTS visites (
    id SERIAL PRIMARY KEY,
    itineraire_id INTEGER REFERENCES itineraires(id) ON DELETE CASCADE,
    nom VARCHAR(255) NOT NULL,
    prix_par_personne DECIMAL(15, 2) DEFAULT 0,
    prix_par_voiture DECIMAL(15, 2) DEFAULT 0,
    type_prix VARCHAR(20) DEFAULT 'personne',
    guidage_obligatoire BOOLEAN DEFAULT FALSE,
    guidage_prix_base DECIMAL(15, 2) DEFAULT 0,
    guidage_nb_personnes_base INTEGER DEFAULT 4,
    guidage_type_calcul VARCHAR(50) DEFAULT 'par_groupe',
    taxe_communale DECIMAL(15, 2) DEFAULT 0,
    ordre INTEGER DEFAULT 0,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(itineraire_id, nom)
);

-- Créer la table des types de voitures si elle n'existe pas
CREATE TABLE IF NOT EXISTS types_voitures (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    consommation_l_100km DECIMAL(5, 2) NOT NULL,
    ordre INTEGER DEFAULT 0,
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer la table des visites_jour si elle n'existe pas
CREATE TABLE IF NOT EXISTS visites_jour (
    id SERIAL PRIMARY KEY,
    jour_voyage_id INTEGER REFERENCES jours_voyage(id) ON DELETE CASCADE,
    visite_id INTEGER REFERENCES visites(id) ON DELETE CASCADE,
    nombre_personnes INTEGER DEFAULT 0,
    nombre_voitures INTEGER DEFAULT 0,
    prix_entree DECIMAL(15, 2) DEFAULT 0,
    prix_guidage DECIMAL(15, 2) DEFAULT 0,
    prix_taxe_communale DECIMAL(15, 2) DEFAULT 0,
    prix_total DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajouter les colonnes manquantes à locations_vehicules
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'locations_vehicules' AND column_name = 'type_voiture_id'
    ) THEN
        ALTER TABLE locations_vehicules ADD COLUMN type_voiture_id INTEGER REFERENCES types_voitures(id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'locations_vehicules' AND column_name = 'consommation_carburant'
    ) THEN
        ALTER TABLE locations_vehicules ADD COLUMN consommation_carburant DECIMAL(10, 2) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'locations_vehicules' AND column_name = 'prix_carburant_pompe'
    ) THEN
        ALTER TABLE locations_vehicules ADD COLUMN prix_carburant_pompe DECIMAL(10, 2) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'locations_vehicules' AND column_name = 'prix_carburant_total'
    ) THEN
        ALTER TABLE locations_vehicules ADD COLUMN prix_carburant_total DECIMAL(15, 2) DEFAULT 0;
    END IF;
END $$;

-- Ajouter la colonne visite_id à guidages si elle n'existe pas
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'guidages' AND column_name = 'visite_id'
    ) THEN
        ALTER TABLE guidages ADD COLUMN visite_id INTEGER REFERENCES visites(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Créer les index si ils n'existent pas
CREATE INDEX IF NOT EXISTS idx_visites_itineraire ON visites(itineraire_id);
CREATE INDEX IF NOT EXISTS idx_visites_jour_jour ON visites_jour(jour_voyage_id);
CREATE INDEX IF NOT EXISTS idx_visites_jour_visite ON visites_jour(visite_id);
CREATE INDEX IF NOT EXISTS idx_locations_type_voiture ON locations_vehicules(type_voiture_id);

-- Ajouter les nouvelles catégories de coûts
INSERT INTO categories_couts (nom, ordre) VALUES
    ('Visites', 11),
    ('Taxes communales', 12)
ON CONFLICT (nom) DO NOTHING;

