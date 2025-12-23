# Guide de Mise à Jour vers la Version 2

## 🚀 Nouveautés de la Version 2

- ✅ Gestion des itinéraires (Antananarivo, Antsirabe, etc.)
- ✅ Gestion des hôtels avec prix par itinéraire
- ✅ Interface pour ajouter des jours de voyage avec sélection d'itinéraire et d'hôtel
- ✅ Calcul automatique du prix d'hébergement selon l'hôtel et le type de chambre
- ✅ Clarification : "Double" = 1 chambre pour 2 personnes (grand lit)

## 📋 Étapes de Mise à Jour

### 1. Mettre à jour le schéma de la base de données

Si vous avez déjà une base de données existante, exécutez le script de migration :

```bash
psql -U postgres -d cotisation_madagascar -f database/migrate_to_v2.sql
```

Si vous créez une nouvelle base de données, utilisez le nouveau schéma :

```bash
psql -U postgres -d cotisation_madagascar -f database/schema_v2.sql
```

### 2. Insérer les données des itinéraires et hôtels

Exécutez le script pour insérer toutes les données depuis les captures d'écran :

```bash
python3 database/insert_itineraires_hotels.py
```

Ce script va :
- Créer tous les itinéraires (Antananarivo, Antsirabe, Miandrivazo, etc.)
- Insérer tous les hôtels avec leurs prix
- Associer chaque hôtel à son itinéraire

### 3. Vérifier l'installation

Testez que tout fonctionne :

```bash
python3 test_connection.py
```

### 4. Démarrer l'application

```bash
python3 app.py
```

## 🎯 Utilisation de la Nouvelle Interface

### Créer un Devis avec Jours de Voyage

1. **Créer un nouveau devis** (`/devis/nouveau`)
   - Remplir les informations de base (client, nombre de personnes, etc.)
   - Cliquer sur "Créer le Devis"

2. **Gérer les jours de voyage** (redirection automatique)
   - **Numéro du Jour** : Entrer 1 pour le 1er jour, 2 pour le 2ème jour, etc.
   - **Date** : Optionnel, jour du mois (17, 18, 19...)
   - **Itinéraire** : Sélectionner dans la liste déroulante (Antananarivo, Antsirabe, etc.)
   - **Hôtel** : La liste se met à jour automatiquement selon l'itinéraire choisi
   - **Type de Chambre** :
     - Double : 1 chambre pour 2 personnes (grand lit)
     - Triple : 1 chambre pour 3 personnes
   - **Nombre de Chambres** : Nombre de chambres nécessaires (pas nombre de personnes)
   - **Transfert Hôtel** : Frais de transfert optionnels

3. **Prix automatique** : Le prix total de l'hébergement est calculé automatiquement :
   - Prix chambre × Nombre de chambres + Transfert

### Exemple

Pour un voyage de 2 personnes à Antananarivo :
- Jour 1 : Antananarivo → Chalets des Roses → Double → 1 chambre
- Prix : 200,000 Ar (prix de la chambre double) × 1 = 200,000 Ar

Pour un voyage de 4 personnes à Antananarivo :
- Jour 1 : Antananarivo → Chalets des Roses → Double → 2 chambres
- Prix : 200,000 Ar × 2 = 400,000 Ar

## 📊 Structure des Données

### Itinéraires Disponibles

- Antananarivo
- Antsirabe
- Miandrivazo
- Descente du Tsiribihina
- Bekopaka
- Morondava
- Ifaty
- Ranohira
- Fianarantsoa
- PN Ranomafana
- Diego Suarez
- Ankarana
- Ankify
- Nosy Be
- Sainte Marie
- Akany ny Nofy

### Hôtels par Itinéraire

Chaque itinéraire a sa propre liste d'hôtels avec leurs prix. Les prix sont en Ariary et représentent le prix pour **1 chambre double** (2 personnes).

## 🔧 API Disponible

- `GET /api/itineraires` : Liste tous les itinéraires
- `GET /api/itineraires/<id>/hotels` : Liste les hôtels d'un itinéraire
- `GET /api/devis/<id>/jours` : Liste les jours d'un devis
- `POST /api/devis/<id>/jours` : Ajoute un jour de voyage
- `POST /api/devis/<id>/jours/<jour_id>/hebergement` : Ajoute un hébergement à un jour

## ⚠️ Notes Importantes

- **Double** = 1 chambre pour 2 personnes (grand lit), pas 2 chambres
- **Triple** = 1 chambre pour 3 personnes
- Le prix affiché est le prix par chambre
- Le calcul total = Prix chambre × Nombre de chambres

