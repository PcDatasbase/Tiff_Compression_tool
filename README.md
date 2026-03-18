# Tiff Compression Tool

Outil graphique pour compresser des images TIFF (fichiers uniques ou sequences multipages) en mode sans perte, verifier automatiquement l'integrite des donnees et conserver uniquement la version validee.

## Fonctionnalites

- Selection d'un fichier TIFF unique ou d'un dossier complet.
- Recherche recursive des fichiers `.tif` et `.tiff` dans un dossier.
- Compression sans perte avec deux methodes disponibles:
	- ZIP (Deflate)
	- LZW
- Detection des fichiers deja compresses (evite une recompression inutile).
- Verification automatique post-compression:
	- egalite des pixels
	- dimensions
	- metadonnees ImageJ essentielles
	- statistiques globales (min, max, moyenne, ecart-type)
	- hash de fichier different (attendu pour un fichier recompresse)
- Gestion automatique des fichiers apres verification:
	- si verification OK: suppression de l'original, conservation du fichier compresse
	- si verification echoue: suppression du fichier compresse, conservation de l'original
- Interface graphique simple avec barre de progression et journal des resultats.

## Prerequis

- Windows (scripts `.bat` fournis)
- Python 3.9+

## Installation (Windows)

Option recommandee:

```bat
install_windows.bat
```

Ce script fait automatiquement:
1. Creation de l'environnement virtuel `.venv`
2. Installation des dependances depuis `requirements.txt`

Installation manuelle (equivalente):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Lancement

Avec le script Windows:

```bat
run_tiff_compression.bat
```

Ou en Python:

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

## Utilisation rapide

1. Cliquer sur `Select File` pour traiter un seul fichier TIFF, ou `Select Folder` pour traiter un dossier.
2. Choisir la methode de compression (`ZIP` ou `LZW`) (Laissez par défaut, l'autre methode de compression sera utile uniquement si la première échoue).
3. Cliquer sur `Compress`.
4. Suivre l'avancement dans la barre de progression et la zone de resultats.
5. Verifier dans le journal quel fichier a ete conserve pour chaque traitement.

## Comportement de traitement

Pour chaque fichier TIFF:

1. Verification de l'etat de compression initial.
2. Si deja compresse: fichier ignore (conserve tel quel).
3. Sinon:
	 - creation d'un fichier compresse suffixe par `_zip` ou `_lzw`
	 - verification complete de l'integrite
	 - application des regles de conservation/suppression des fichiers

Exemple:
- `image.tif` compresse en ZIP devient `image_zip.tif`
- `stack.tiff` compresse en LZW devient `stack_lzw.tif`

## Structure du projet

```text
Tiff_Compression_tool/
|- run.py
|- install_windows.bat
|- run_tiff_compression.bat
|- requirements.txt
|- app/
|  |- tiff_compression_gui.py
|  |- tiff_compression.py
|  |- compression_check.py
```

## Dependances principales

- tifffile
- numpy
- pillow
- matplotlib
