# pip install streamlit yt_dlp

########
# Extraction d'une vidéo en images 25fps
########

import streamlit as st
import subprocess
import os
from yt_dlp import YoutubeDL

# Fonction pour vider le cache
def vider_cache():
    st.cache_data.clear()
    st.write("Cache vidé systématiquement au lancement du script")

# Appeler la fonction de vidage du cache au début du script
vider_cache()

# Fonction pour définir le répertoire de travail
def definir_repertoire_travail():
    repertoire = st.text_input("Définir le répertoire de travail", "", key="repertoire_travail")
    if not repertoire:
        st.write("Veuillez spécifier un chemin valide.")
        return ""
    repertoire = repertoire.strip()
    repertoire = os.path.abspath(repertoire)
    if not os.path.exists(repertoire):
        os.makedirs(repertoire)
        st.write(f"Le répertoire a été créé : {repertoire}")
    else:
        st.write(f"Le répertoire existe déjà : {repertoire}")
    return repertoire

# Fonction pour télécharger la vidéo avec yt-dlp (forcer le format .mp4)
def telecharger_video(url, repertoire):
    st.write("Téléchargement de la vidéo à partir de YouTube...")
    ydl_opts = {
        'outtmpl': os.path.join(repertoire, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4'
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get("title", "video")
        video_filename = f"{video_title}.mp4"
        video_path = os.path.join(repertoire, video_filename)
    st.write(f"Téléchargement terminé : {video_path}")
    return video_path, video_title

# Fonction pour extraire des images à 25fps dans un intervalle donné
def extraire_images_25fps_intervalle(video_path, repertoire, debut, fin, video_title):
    images_repertoire = os.path.join(repertoire, f"images_25fps_{video_title}")
    if not os.path.exists(images_repertoire):
        os.makedirs(images_repertoire)
        st.write(f"Répertoire créé pour les images : {images_repertoire}")
    else:
        st.write(f"Le répertoire pour les images existe déjà : {images_repertoire}")

    # Durée de l'intervalle
    duree = fin - debut

    st.write(f"Extraction des images à 25fps entre {debut}s et {fin}s...")
    cmd = [
        'ffmpeg', '-ss', str(debut), '-t', str(duree), '-i', video_path,
        '-vf', 'fps=25,scale=1920:1080', '-q:v', '1',
        os.path.join(images_repertoire, 'image_%04d.jpg')
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        st.write(f"Erreur lors de l'extraction des images : {result.stderr.decode('utf-8')}")
        return None

    st.write(f"Images extraites dans le répertoire : {images_repertoire}")
    return images_repertoire

# Interface Streamlit
st.title("Extraction d'images d'une vidéo YouTube à 25fps")

# Entrée pour l'URL de la vidéo
url = st.text_input("Entrez l'URL de la vidéo YouTube :")

# Entrées pour l'intervalle de temps
col1, col2 = st.columns(2)
debut = col1.number_input("Début de l'intervalle (en secondes) :", min_value=0, value=0)
fin = col2.number_input("Fin de l'intervalle (en secondes) :", min_value=1, value=10)

if url:
    repertoire_travail = definir_repertoire_travail()
    if repertoire_travail:
        video_path, video_title = telecharger_video(url, repertoire_travail)
        if video_path:
            if st.button("Extraire les images"):
                if debut >= fin:
                    st.write("Erreur : Le début de l'intervalle doit être inférieur à la fin.")
                else:
                    images_repertoire = extraire_images_25fps_intervalle(
                        video_path, repertoire_travail, debut, fin, video_title
                    )
                    if images_repertoire:
                        st.write(f"Extraction terminée. Les images sont disponibles dans : {images_repertoire}")
