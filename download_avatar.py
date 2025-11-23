#!/usr/bin/env python3
"""
Script pour télécharger l'image d'avatar depuis une URL
Usage: python3 download_avatar.py <URL>
"""
import sys
import urllib.request
import os

def download_image(url, filename="avatar.png"):
    """Télécharge une image depuis une URL"""
    try:
        print(f"Téléchargement de {url}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Image téléchargée avec succès : {filename}")
        return True
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 download_avatar.py <URL>")
        print("Exemple: python3 download_avatar.py https://example.com/image.png")
        sys.exit(1)
    
    url = sys.argv[1]
    download_image(url)
