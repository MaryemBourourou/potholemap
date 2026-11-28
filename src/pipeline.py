"""PotholeMap : détection (YOLOv8) + suivi (ByteTrack) + gravité + GPS + carte Folium.

Utilisation en ligne de commande :
    python src/pipeline.py --video clip1.mp4 --modele weights/best_v2.pt \
        --lat0 48.8566 --lon0 2.3522 --lat1 48.8606 --lon1 2.3376

Utilisation depuis Python (ou depuis l'application Gradio) :
    from pipeline import analyser_video, gps_simule
    res = analyser_video("clip1.mp4", "weights/best_v2.pt", gps_simule(...))
"""
import argparse
import csv
import glob
import os
import subprocess
from collections import Counter

import numpy as np

# --------------------------------------------------------------------------
# Paramètres de gravité
# --------------------------------------------------------------------------
# Seuils sur l'aire relative de la boîte (fraction de l'image).
# Valeurs provisoires : environ la moitié et 1,4 fois l'aire médiane d'un
# nid-de-poule mesurée en validation (0,41 à 0,44 % de l'image).
# À ajuster après avoir regardé vos clips, et à justifier dans le rapport.
SEUILS_AIRE = (0.002, 0.006)
COULEURS = {"faible": "green", "moyen": "orange", "élevé": "red", "réparé": "gray"}


def seuils_gravite(labels_dir, id_classe):
    """(Optionnel) Calcule les terciles d'aire des boîtes d'une classe dans des labels YOLO."""
    aires = []
    for f in glob.glob(os.path.join(labels_dir, "*.txt")):
        for ligne in open(f):
            p = ligne.split()
            if len(p) >= 5 and int(p[0]) == id_classe:
                aires.append(float(p[3]) * float(p[4]))
    return tuple(float(x) for x in np.quantile(aires, [1 / 3, 2 / 3]))


def niveau_gravite(classe, aire_rel, conf_max):
    """Gravité relative (pas une mesure en centimètres)."""
    if classe == "pothole_repair":
        return "réparé"
    a1, a2 = SEUILS_AIRE
    n = 0 if aire_rel < a1 else (1 if aire_rel < a2 else 2)
    if conf_max < 0.5:          # détection peu sûre : on baisse d'un niveau
        n = max(0, n - 1)
    return ["faible", "moyen", "élevé"][n]


# --------------------------------------------------------------------------
# GPS
# --------------------------------------------------------------------------
def gps_simule(lat0, lon0, lat1, lon1, duree):
    """Trajet en ligne droite entre deux points, parcouru pendant `duree` secondes."""
    def f(t):
        a = min(max(t / max(duree, 1e-6), 0.0), 1.0)
        return lat0 + a * (lat1 - lat0), lon0 + a * (lon1 - lon0)
    return f


def gps_depuis_gpx(chemin, decalage_s=0.0):
    """Lit un fichier GPX. Hypothèse : l'enregistrement GPX démarre en même temps
    que la vidéo (sinon, corriger avec `decalage_s`)."""
    import gpxpy
    with open(chemin, encoding="utf-8") as fh:
        g = gpxpy.parse(fh)
    pts = [p for tr in g.tracks for seg in tr.segments for p in seg.points]
    if len(pts) < 2:
        raise ValueError("Le fichier GPX contient moins de 2 points.")
    t0 = pts[0].time
    ts = np.array([(p.time - t0).total_seconds() for p in pts]) - decalage_s
    la = np.array([p.latitude for p in pts])
    lo = np.array([p.longitude for p in pts])

    def f(t):
        return float(np.interp(t, ts, la)), float(np.interp(t, ts, lo))
    return f


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------
def vers_h264(src, dst):
    """Convertit en H.264 (lisible dans un navigateur / Gradio). Si ffmpeg manque, garde src."""
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                        "-vcodec", "libx264", "-pix_fmt", "yuv420p", dst], check=True)
        return dst
    except Exception:
        return src


def creer_carte(defauts, gps, duree, chemin):
    import folium
    traj = [gps(t) for t in np.linspace(0, duree, 40)]
    m = folium.Map(location=traj[len(traj) // 2], zoom_start=17)
    folium.PolyLine(traj, color="blue", weight=3, opacity=0.6,
                    tooltip="Trajet").add_to(m)
    for d in defauts:
        folium.CircleMarker(
            [d["lat"], d["lon"]], radius=8,
            color=COULEURS[d["gravite"]], fill=True, fill_opacity=0.8,
            popup=f'#{d["id"]} {d["classe"]} - {d["gravite"]} (t={d["temps_s"]} s)',
        ).add_to(m)
    m.save(chemin)
    return chemin


# --------------------------------------------------------------------------
# Pipeline principal
# --------------------------------------------------------------------------
def analyser_video(video, modele, gps, conf=0.15, stride=1, min_frames=5,
                   min_conf=0.40, imgsz=640, dossier_sortie="sorties", progress=None):
    """Détecte, suit, filtre, géolocalise. Renvoie un dictionnaire de résultats.

    conf       : seuil de détection (bas pour garder du rappel, le filtre de pistes nettoie)
    stride     : on traite 1 image sur `stride`
    min_frames : une piste doit durer au moins ce nombre d'images traitées
    min_conf   : une piste doit avoir au moins une détection à cette confiance
    """
    import cv2
    from ultralytics import YOLO

    os.makedirs(dossier_sortie, exist_ok=True)
    model = YOLO(modele)            # nouveau modèle à chaque appel : le tracker repart de zéro
    noms = model.names

    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    cap.release()
    duree = total / fps

    brut = os.path.join(dossier_sortie, "annotee_brut.mp4")
    writer = None
    pistes = {}
    dets_sans_suivi = 0

    flux = model.track(source=video, tracker="bytetrack.yaml", persist=True, conf=conf,
                       imgsz=imgsz, vid_stride=stride, stream=True, verbose=False)
    for i, r in enumerate(flux):
        frame = r.plot()
        if writer is None:
            h, w = frame.shape[:2]
            writer = cv2.VideoWriter(brut, cv2.VideoWriter_fourcc(*"mp4v"),
                                     max(fps / stride, 1.0), (w, h))
        writer.write(frame)
        if progress and i % 10 == 0:
            progress(min(0.95, i * stride / total))
        if r.boxes is None or len(r.boxes) == 0:
            continue
        classes = r.boxes.cls.int().tolist()
        dets_sans_suivi += sum(1 for c in classes if noms[c] == "pothole")
        if r.boxes.id is None:
            continue
        ids = r.boxes.id.int().tolist()
        confs = r.boxes.conf.tolist()
        boites = r.boxes.xywhn.tolist()
        for tid, c, s, b in zip(ids, classes, confs, boites):
            p = pistes.setdefault(tid, {"votes": Counter(), "images": 0,
                                        "conf_max": 0.0, "aires": [], "premiere": i})
            p["votes"][c] += 1
            p["images"] += 1
            p["conf_max"] = max(p["conf_max"], s)
            p["aires"].append(b[2] * b[3])
    if writer is not None:
        writer.release()

    # Filtrage des pistes et géolocalisation
    defauts = []
    for tid, p in pistes.items():
        if p["images"] < min_frames or p["conf_max"] < min_conf:
            continue
        classe = noms[p["votes"].most_common(1)[0][0]]      # classe majoritaire
        t = p["premiere"] * stride / fps
        lat, lon = gps(t)
        aire_mediane = float(np.median(p["aires"]))
        defauts.append({
            "id": tid,
            "classe": classe,
            "gravite": niveau_gravite(classe, aire_mediane, p["conf_max"]),
            "score": round(aire_mediane * p["conf_max"] * 100, 3),
            "confiance_max": round(p["conf_max"], 3),
            "aire_rel": round(aire_mediane, 5),
            "nb_images": p["images"],
            "temps_s": round(t, 2),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
        })
    defauts.sort(key=lambda d: d["temps_s"])

    chemin_csv = os.path.join(dossier_sortie, "defauts.csv")
    cols = ["id", "classe", "gravite", "score", "confiance_max", "aire_rel",
            "nb_images", "temps_s", "lat", "lon"]
    with open(chemin_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(defauts)

    chemin_carte = creer_carte(defauts, gps, duree, os.path.join(dossier_sortie, "carte.html"))
    video_finale = vers_h264(brut, os.path.join(dossier_sortie, "annotee.mp4"))
    if progress:
        progress(1.0)

    return {
        "video": video_finale,
        "csv": chemin_csv,
        "carte": chemin_carte,
        "defauts": defauts,
        "stats": {
            "duree_s": round(duree, 1),
            "detections_pothole_sans_suivi": dets_sans_suivi,
            "pistes_brutes": len(pistes),
            "pistes_gardees": len(defauts),
            "potholes_uniques": sum(1 for d in defauts if d["classe"] == "pothole"),
            "reparations_uniques": sum(1 for d in defauts if d["classe"] == "pothole_repair"),
        },
    }


def main():
    ap = argparse.ArgumentParser(description="PotholeMap : analyse d'une vidéo de route")
    ap.add_argument("--video", required=True)
    ap.add_argument("--modele", default="weights/best_v2.pt")
    ap.add_argument("--gpx", default=None, help="Trace GPX (sinon trajet simulé)")
    ap.add_argument("--lat0", type=float); ap.add_argument("--lon0", type=float)
    ap.add_argument("--lat1", type=float); ap.add_argument("--lon1", type=float)
    ap.add_argument("--conf", type=float, default=0.15)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--min_frames", type=int, default=5)
    ap.add_argument("--min_conf", type=float, default=0.40)
    ap.add_argument("--out", default="sorties")
    a = ap.parse_args()

    import cv2
    cap = cv2.VideoCapture(a.video)
    duree = (int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1) / (cap.get(cv2.CAP_PROP_FPS) or 30.0)
    cap.release()

    if a.gpx:
        gps = gps_depuis_gpx(a.gpx)
    else:
        if None in (a.lat0, a.lon0, a.lat1, a.lon1):
            ap.error("Sans --gpx, il faut --lat0 --lon0 --lat1 --lon1 (trajet simulé).")
        gps = gps_simule(a.lat0, a.lon0, a.lat1, a.lon1, duree)

    res = analyser_video(a.video, a.modele, gps, conf=a.conf, stride=a.stride,
                         min_frames=a.min_frames, min_conf=a.min_conf, dossier_sortie=a.out)
    print("Statistiques :", res["stats"])
    print("Fichiers     :", res["video"], res["csv"], res["carte"])


if __name__ == "__main__":
    main()
