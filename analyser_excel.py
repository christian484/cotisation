#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse complète d'un fichier Excel
Analyse toutes les feuilles, lignes et colonnes
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

def analyser_fichier_excel(nom_fichier):
    """
    Analyse complète d'un fichier Excel
    
    Args:
        nom_fichier: Chemin vers le fichier Excel
    """
    print("=" * 80)
    print(f"ANALYSE DU FICHIER: {nom_fichier}")
    print("=" * 80)
    print(f"Date d'analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Ouvrir le fichier Excel
    try:
        xl_file = pd.ExcelFile(nom_fichier)
    except Exception as e:
        print(f"ERREUR: Impossible d'ouvrir le fichier: {e}")
        return None
    
    # Informations générales
    print(f"Nombre de feuilles: {len(xl_file.sheet_names)}")
    print(f"Feuilles disponibles: {xl_file.sheet_names}\n")
    
    resultats = {}
    
    # Analyser chaque feuille
    for sheet_name in xl_file.sheet_names:
        print("\n" + "=" * 80)
        print(f"FEUILLE: {sheet_name}")
        print("=" * 80)
        
        # Lire la feuille
        df = pd.read_excel(xl_file, sheet_name=sheet_name)
        
        # Informations de base
        nb_lignes, nb_colonnes = df.shape
        print(f"\nDimensions: {nb_lignes} lignes × {nb_colonnes} colonnes")
        print(f"Nombre total de cellules: {nb_lignes * nb_colonnes}")
        
        # Analyse des colonnes
        print(f"\n--- ANALYSE DES COLONNES ---")
        print(f"Nombre de colonnes: {nb_colonnes}")
        print(f"\nNoms des colonnes:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:3d}. {col}")
        
        # Analyse des lignes
        print(f"\n--- ANALYSE DES LIGNES ---")
        print(f"Nombre de lignes: {nb_lignes}")
        
        # Statistiques par colonne
        print(f"\n--- STATISTIQUES PAR COLONNE ---")
        for col in df.columns:
            print(f"\nColonne: {col}")
            print(f"  Type de données: {df[col].dtype}")
            print(f"  Valeurs non nulles: {df[col].notna().sum()} / {nb_lignes}")
            print(f"  Valeurs nulles: {df[col].isna().sum()} / {nb_lignes}")
            
            # Valeurs uniques (limitées pour éviter trop de sortie)
            valeurs_uniques = df[col].dropna().unique()
            nb_uniques = len(valeurs_uniques)
            print(f"  Valeurs uniques: {nb_uniques}")
            
            if nb_uniques <= 10 and nb_uniques > 0:
                print(f"  Liste des valeurs uniques: {list(valeurs_uniques)}")
            elif nb_uniques > 10:
                print(f"  Premières valeurs uniques: {list(valeurs_uniques[:10])}...")
            
            # Statistiques numériques si applicable
            if pd.api.types.is_numeric_dtype(df[col]):
                print(f"  Min: {df[col].min()}")
                print(f"  Max: {df[col].max()}")
                print(f"  Moyenne: {df[col].mean():.2f}")
                print(f"  Médiane: {df[col].median():.2f}")
                print(f"  Écart-type: {df[col].std():.2f}")
        
        # Analyse des valeurs nulles
        print(f"\n--- ANALYSE DES VALEURS NULLES ---")
        valeurs_nulles_par_col = df.isnull().sum()
        print("Nombre de valeurs nulles par colonne:")
        for col, count in valeurs_nulles_par_col.items():
            if count > 0:
                print(f"  {col}: {count} ({count/nb_lignes*100:.1f}%)")
        
        # Analyse des doublons
        print(f"\n--- ANALYSE DES DOUBLONS ---")
        lignes_dupliquees = df.duplicated().sum()
        print(f"Lignes complètement dupliquées: {lignes_dupliquees}")
        
        # Afficher toutes les données
        print(f"\n--- CONTENU COMPLET DE LA FEUILLE ---")
        print(f"\nToutes les {nb_lignes} lignes:")
        print(df.to_string())
        
        # Stocker les résultats
        resultats[sheet_name] = {
            'dimensions': {'lignes': nb_lignes, 'colonnes': nb_colonnes},
            'colonnes': list(df.columns),
            'types_donnees': {col: str(df[col].dtype) for col in df.columns},
            'valeurs_nulles': valeurs_nulles_par_col.to_dict(),
            'statistiques': {}
        }
        
        # Statistiques numériques détaillées
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                resultats[sheet_name]['statistiques'][col] = {
                    'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    'moyenne': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                    'mediane': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                    'ecart_type': float(df[col].std()) if not pd.isna(df[col].std()) else None
                }
    
    # Résumé final
    print("\n" + "=" * 80)
    print("RÉSUMÉ FINAL")
    print("=" * 80)
    print(f"\nFichier analysé: {nom_fichier}")
    print(f"Nombre total de feuilles: {len(xl_file.sheet_names)}")
    for sheet_name, stats in resultats.items():
        print(f"\nFeuille '{sheet_name}':")
        print(f"  - {stats['dimensions']['lignes']} lignes × {stats['dimensions']['colonnes']} colonnes")
        print(f"  - {len(stats['colonnes'])} colonnes")
    
    # Sauvegarder les résultats en JSON
    nom_resultat = Path(nom_fichier).stem + "_analyse.json"
    with open(nom_resultat, 'w', encoding='utf-8') as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nRésultats sauvegardés dans: {nom_resultat}")
    
    return resultats

if __name__ == "__main__":
    fichier = "Bases de datos internos.xlsx"
    
    if not Path(fichier).exists():
        print(f"ERREUR: Le fichier '{fichier}' n'existe pas!")
        exit(1)
    
    resultats = analyser_fichier_excel(fichier)
    
    print("\n" + "=" * 80)
    print("ANALYSE TERMINÉE")
    print("=" * 80)

