# 🛡️ Shielder — Multi-Project Guardian & Diagnostic Hub

> **Status:** Active & Operational  
> **Last Audit:** 2026-09-30 17:45:00  
> **Host Account:** `moslihayoub@gmail.com`  
> **Ecosystem:** `~/Downloads/ANT2.0` (12 tracked projects)

---

## 📅 Historique Récent (Changelog)

**[2026-09-30] Refonte UI/UX Shadcn & Mobile-First**
- **Charte Visuelle Shadcn** : Application stricte de la palette (Blanc, Bleu #2563eb, Noir #09090b) sur les graphiques Chart.js (Ecosystem & Tokens) respectant parfaitement le Light/Dark mode.
- **Correction Navbar (Web/Mobile)** : Suppression des `w-10` forcés qui tronquaient le texte. Navbar désormais 100% fluide, boutons icônes parfaitement carrés, et recherche extensible.
- **Tags & Badges** : Ajout d'espacements dynamiques (`gap-2`) et d'un padding élargi (`px-2.5 py-1`) pour éviter l'effet "bloc étouffé" au retour à la ligne sur mobile.
- **Bouton Assistant IA** : Ajustement dimensionnel (`w-14 h-14` sur mobile, `w-16 h-16` sur desktop) pour corriger l'effet d'écrasement.
- **Branding Shielder** : Injection officielle du logo `icon.svg` dans la Navbar, des métadonnées Favicon, et `apple-touch-icon`.
- **Intégration Jira** : Réparation du lien Kanban sur les projets (remplacement de l'icône `trello` obsolète par `kanban` valide de Lucide).

---

## 1. Quick Start

Run from **any terminal** or chat session:
```bash
# 1. Audit all 12 projects (takes ~3 seconds)
shielder check

# 2. Open visual dashboard in your browser
shielder dashboard

# 3. List all registered projects
shielder list
```

---

## 2. Tracked Projects Registry (ANT2.0 Ecosystem)

### 🅰️ Engineering Apps & Analysis (`ANT2.0/1_engineering_apps/`)
| Project | Stack | Database / Cloud | API Health | Jira Tag |
| :--- | :--- | :--- | :--- | :--- |
| **LayerB2B** *(OmniLayer)* | Next.js 15 | Supabase + GCP `omnilayerai` | Gemini + OpenRouter | `[LAYERB2B]` |
| **Operation** *(Fluxo)* | Next.js 14 | Supabase (100%) | Gemini + OpenRouter | `[FLUXO]` |
| **AI-Tool** *(parseliq-hr)* | React 19 / Vite | Local State (GCP `Tools AI`) | Gemini + OpenRouter | `[AITOOL]` |
| **Financial Calculator** | React 19 / Vite | Local State (GCP `App finance`) | Gemini + OpenRouter | `[FINANCE]` |
| **Autocash-sourcing** | React 19 / Vite | Local State | Nominal | `[AUTOCASH-SOURCING]` |
| **Portfolio** *(Ayoub MOSLIH)* | React 19 / Vite | Firebase Hosting | Gemini + OpenRouter | `[PORTFOLIO]` |
| **Agentic** | Python / HTML | Local State / Python server | Nominal | `[AGENTIC]` |
| **Autocash-DB** | Python / Office | Local Cache (4.6MB AST) | Nominal | `[AUTOCASH-DB]` |
| **Automation UX-PM** | Product / Office | Local Excel / SharePoint | Nominal | `[UX-PM]` |

### 🅱️ Product Studios & Creative AI (`ANT2.0/2_product_studios/`)
| Project | Moteur / Stack | Hub Créatif | Statut | Jira Tag |
| :--- | :--- | :--- | :--- | :--- |
| **Canva Studio** | Canva MCP | Cloud Canva | Opérationnel | `[STUDIO]` |
| **G-flow Studio** | Google Flow / Veo 2 | Cloud Google Flow | Opérationnel | `[STUDIO]` |
| **The Cosmic Spark** | Higgsfield / Seedance | Local Assets / Day 8 | Opérationnel | `[STUDIO]` |

---

## 3. Automation & Background Health Checks
To run Shielder automatically in the background (once per day or on interval), trigger Antigravity's scheduler:
* `/schedule` ➔ Exécute `shielder check` quotidiennement et alerte uniquement en cas d'anomalie critique.
