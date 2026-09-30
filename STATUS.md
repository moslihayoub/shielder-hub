# 🛡️ Shielder — Multi-Project Guardian & Diagnostic Hub

> **Status:** Active & Operational  
> **Last Audit:** 2026-09-30 14:10:00  
> **Host Account:** `moslihayoub@gmail.com`  
> **Ecosystem:** `~/Downloads/ANT2.0` (12 tracked projects)

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
| **LayerB2B** *(OmniLayer)* | Next.js 15 | Supabase + GCP `omnilayerai` | Gemini Key Active | `[LAYERB2B]` |
| **Operation** *(Fluxo)* | Next.js 14 | Supabase Realtime + Firebase | Gemini Key Active | `[FLUXO]` |
| **AI-Tool** *(parseliq-hr)* | React 19 / Vite | Local State (GCP `Tools AI`) | Gemini Key Active | `[AITOOL]` |
| **Financial Calculator** | React 19 / Vite | Local State (GCP `App finance`) | Gemini Key Active | `[FINANCE]` |
| **Autocash-sourcing** | React 19 / Vite | Local State | Nominal | `[AUTOCASH-SOURCING]` |
| **Portfolio** *(Ayoub MOSLIH)* | React 19 / Vite | Firebase Hosting | Gemini Key Active | `[PORTFOLIO]` |
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
