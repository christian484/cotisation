-- Script de migration vers la version 2 avec itinéraires et hôtels
-- À exécuter si vous avez déjà une base de données existante

-- Créer la table des itinéraires si elle n'existe pas
CREATE TABLE IF NOT EXISTS itineraires (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    ordre INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer la table des hôtels si elle n'existe pas
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

-- Ajouter la colonne itineraire_id à jours_voyage si elle n'existe pas
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'jours_voyage' AND column_name = 'itineraire_id'
    ) THEN
        ALTER TABLE jours_voyage ADD COLUMN itineraire_id INTEGER REFERENCES itineraires(id);
    END IF;
END $$;

-- Modifier la colonne date_jour pour permettre NULL si nécessaire
ALTER TABLE jours_voyage ALTER COLUMN date_jour DROP NOT NULL;

-- Ajouter la colonne hotel_id à hebergements si elle n'existe pas
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hebergements' AND column_name = 'hotel_id'
    ) THEN
        ALTER TABLE hebergements ADD COLUMN hotel_id INTEGER REFERENCES hotels(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Créer les index si ils n'existent pas
CREATE INDEX IF NOT EXISTS idx_jours_voyage_itineraire ON jours_voyage(itineraire_id);
CREATE INDEX IF NOT EXISTS idx_hebergements_hotel ON hebergements(hotel_id);
CREATE INDEX IF NOT EXISTS idx_hotels_itineraire ON hotels(itineraire_id);

