"""Application Gradio PotholeMap : vidéo de route -> vidéo annotée + tableau + carte + CSV.

Lancement local :   python app/app.py
Hugging Face Space : mettre app.py, pipeline.py, best_v2.pt, requirements.txt, packages.txt à la racine.
"""
import html
import os
import sys
import tempfile

import gradio as gr
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
sys.path.insert(0, os.path.join(ICI, "..", "src"))
from pipeline import analyser_video, gps_depuis_gpx, gps_simule  # noqa: E402

CANDIDATS = [
    os.path.join(ICI, "best_v2.pt"),
    os.path.join(ICI, "..", "weights", "best_v2.pt"),
    os.path.join(ICI, "weights", "best_v2.pt"),
    os.path.join(ICI, "best.pt"),
    os.path.join(ICI, "..", "weights", "best.pt"),
]
MODELE = next((c for c in CANDIDATS if os.path.exists(c)), None)


def traiter(video, gpx, lat0, lon0, lat1, lon1, conf, stride, min_frames, min_conf,
            progress=gr.Progress()):
    import cv2

    if MODELE is None:
        raise gr.Error("Modèle introuvable : placer best_v2.pt à côté de app.py ou dans weights/.")
    if video is None:
        raise gr.Error("Charge d'abord une vidéo de route.")

    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    duree = (int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1) / fps
    cap.release()

    try:
        gps = gps_depuis_gpx(gpx) if gpx else gps_simule(lat0, lon0, lat1, lon1, duree)
    except Exception as e:
        raise gr.Error(f"Fichier GPX invalide : {e}")

    res = analyser_video(video, MODELE, gps, conf=float(conf), stride=int(stride),
                         min_frames=int(min_frames), min_conf=float(min_conf),
                         dossier_sortie=tempfile.mkdtemp(), progress=lambda a: progress(a))

    s = res["stats"]
    resume = (
        f"**Durée analysée :** {s['duree_s']} s  \n"
        f"**Détections de nids-de-poule image par image (sans suivi) :** {s['detections_pothole_sans_suivi']}  \n"
        f"**Nids-de-poule uniques après suivi et filtrage :** {s['potholes_uniques']}  \n"
        f"**Zones réparées uniques :** {s['reparations_uniques']}  \n"
        f"*Pistes brutes : {s['pistes_brutes']}, gardées : {s['pistes_gardees']}. "
        f"La gravité est un indicateur relatif, pas une mesure en centimètres.*"
    )
    df = pd.DataFrame(res["defauts"])
    with open(res["carte"], encoding="utf-8") as fh:
        carte = fh.read()
    iframe = (f'<iframe srcdoc="{html.escape(carte)}" width="100%" height="480" '
              f'style="border:0"></iframe>')
    return res["video"], resume, df, iframe, res["csv"]


with gr.Blocks(title="PotholeMap") as demo:
    gr.Markdown("# PotholeMap\nDétection et suivi de nids-de-poule dans une vidéo de route, "
                "avec carte géolocalisée.")
    with gr.Row():
        with gr.Column():
            video = gr.Video(label="Vidéo de route")
            gpx = gr.File(label="Trace GPX (optionnel)", file_types=[".gpx"])
            gr.Markdown("Sans GPX, un trajet est simulé entre ces deux points "
                        "(coordonnées d'exemple à remplacer).")
            with gr.Row():
                lat0 = gr.Number(value=48.8566, label="Latitude départ")
                lon0 = gr.Number(value=2.3522, label="Longitude départ")
            with gr.Row():
                lat1 = gr.Number(value=48.8606, label="Latitude arrivée")
                lon1 = gr.Number(value=2.3376, label="Longitude arrivée")
            with gr.Accordion("Réglages", open=False):
                conf = gr.Slider(0.05, 0.6, value=0.15, step=0.05, label="Seuil de détection")
                stride = gr.Slider(1, 5, value=2, step=1, label="Traiter 1 image sur N")
                min_frames = gr.Slider(1, 15, value=5, step=1, label="Durée minimale d'une piste (images)")
                min_conf = gr.Slider(0.2, 0.8, value=0.40, step=0.05, label="Confiance max minimale d'une piste")
            bouton = gr.Button("Analyser", variant="primary")
        with gr.Column():
            sortie_video = gr.Video(label="Vidéo annotée (boîtes + identifiants)")
            resume = gr.Markdown()
    tableau = gr.Dataframe(label="Défauts uniques")
    carte = gr.HTML(label="Carte")
    csv_out = gr.File(label="Télécharger le CSV")

    bouton.click(traiter,
                 inputs=[video, gpx, lat0, lon0, lat1, lon1, conf, stride, min_frames, min_conf],
                 outputs=[sortie_video, resume, tableau, carte, csv_out])

if __name__ == "__main__":
    demo.launch(share=os.environ.get("SHARE") == "1")
