"""
db.py — Couche base de données Supabase pour ECRA Sourcing
Toutes les interactions avec Supabase passent par ce module.
"""
import streamlit as st
from datetime import datetime

def get_client():
    """Retourne le client Supabase ou None si non configuré."""
    try:
        from supabase import create_client
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        return None

def db_available():
    return get_client() is not None

# ── SESSIONS ────────────────────────────────────────────────────────

def save_session(state: dict) -> str | None:
    """Crée ou met à jour une session. Retourne l'UUID ou None."""
    client = get_client()
    if not client:
        return None
    try:
        payload = {
            "vendeur":          state.get("vendeur") or "Inconnu",
            "etape":            state.get("etape", 1),
            "produit":          state.get("produit", ""),
            "lien_fournisseur": state.get("lien_fournisseur", ""),
            "sous_niche":       state.get("sous_niche", ""),
            "probleme":         state.get("probleme", ""),
            "cible":            state.get("cible", ""),
            "benefice":         state.get("benefice", ""),
            "gt_go":            state.get("gt_go"),
            "gt_kw1":           state.get("gt_kw1", ""),
            "gt_kw2":           state.get("gt_kw2", ""),
            "gt_note":          state.get("gt_note", ""),
            "bsr_go":           state.get("bsr_go"),
            "bsr_note":         state.get("bsr_note", ""),
            "wh_go":            state.get("wh_go"),
            "wh_note":          state.get("wh_note", ""),
            "minea_go":         state.get("minea_go"),
            "minea_note":       state.get("minea_note", ""),
            "scores":           state.get("scores", {}),
            "source":           state.get("source", ""),
            "commentaire":      state.get("commentaire", ""),
            "updated_at":       datetime.utcnow().isoformat(),
        }
        session_id = state.get("_session_id")
        if session_id:
            client.table("sessions").update(payload).eq("id", session_id).execute()
            return session_id
        else:
            res = client.table("sessions").insert(payload).execute()
            return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.warning(f"Erreur sauvegarde DB : {e}")
        return None

def load_session(session_id: str) -> dict | None:
    """Charge une session par UUID."""
    client = get_client()
    if not client:
        return None
    try:
        res = client.table("sessions").select("*").eq("id", session_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.warning(f"Erreur chargement session : {e}")
        return None

def list_sessions(vendeur: str = None, limit: int = 20) -> list:
    """Liste les sessions récentes, filtrées par vendeur si fourni."""
    client = get_client()
    if not client:
        return []
    try:
        q = client.table("sessions").select(
            "id, vendeur, etape, produit, updated_at"
        ).order("updated_at", desc=True).limit(limit)
        if vendeur:
            q = q.ilike("vendeur", f"%{vendeur}%")
        res = q.execute()
        return res.data or []
    except Exception as e:
        return []

def delete_session(session_id: str) -> bool:
    client = get_client()
    if not client:
        return False
    try:
        client.table("sessions").delete().eq("id", session_id).execute()
        return True
    except Exception:
        return False

# ── PRODUITS ─────────────────────────────────────────────────────────

def save_produit(session_id: str, produit: dict) -> str | None:
    """Insère ou met à jour un produit dans la DB."""
    client = get_client()
    if not client:
        return None
    try:
        payload = {
            "session_id":       session_id,
            "vendeur":          produit.get("vendeur", ""),
            "produit":          produit.get("produit", ""),
            "lien_fournisseur": produit.get("lien_fournisseur", ""),
            "sous_niche":       produit.get("sous_niche", ""),
            "probleme":         produit.get("probleme", ""),
            "cible":            produit.get("cible", ""),
            "benefice":         produit.get("benefice", ""),
            "gt":               produit.get("gt", ""),
            "gt_kw1":           produit.get("gt_kw1", ""),
            "gt_kw2":           produit.get("gt_kw2", ""),
            "bsr":              produit.get("bsr", ""),
            "wh":               produit.get("wh", ""),
            "minea":            produit.get("minea", ""),
            "pre_screen":       produit.get("pre_screen", ""),
            "scores":           {k: produit.get(k, 0) for k in [
                "demande_marche","potentiel_pub","marge_brute","momentum_tendance",
                "saturation","faisabilite_logistique","differenciation",
                "brandabilite","scalabilite","private_label"
            ]},
            "score":            produit.get("score", 0),
            "verdict":          produit.get("verdict", ""),
            "source":           produit.get("source", ""),
            "commentaire":      produit.get("commentaire", ""),
        }
        # Update if produit_db_id exists, else insert
        produit_id = produit.get("_produit_id")
        if produit_id:
            client.table("produits").update(payload).eq("id", produit_id).execute()
            return produit_id
        else:
            res = client.table("produits").insert(payload).execute()
            return res.data[0]["id"] if res.data else None
    except Exception as e:
        st.warning(f"Erreur sauvegarde produit : {e}")
        return None

def list_produits(session_id: str) -> list:
    """Récupère tous les produits d'une session."""
    client = get_client()
    if not client:
        return []
    try:
        res = client.table("produits").select("*").eq(
            "session_id", session_id
        ).order("created_at").execute()
        return res.data or []
    except Exception:
        return []

def all_produits_for_vendeur(vendeur: str) -> list:
    """Récupère tous les produits d'un vendeur toutes sessions confondues."""
    client = get_client()
    if not client:
        return []
    try:
        res = client.table("produits").select("*").eq(
            "vendeur", vendeur
        ).order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        return []
