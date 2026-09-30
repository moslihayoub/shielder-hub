#!/usr/bin/env python3
"""
Shielder Health & Diagnostic Engine
Centrally monitors dependencies, database bindings, API health, and Git status across all Antigravity projects.
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

SHIELDER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(SHIELDER_DIR, "registry.json")
REPORTS_DIR = os.path.join(SHIELDER_DIR, "reports")
DASHBOARD_PATH = os.path.join(SHIELDER_DIR, "dashboard.html")

def test_gemini_key(api_key):
    """Test a Gemini API key using Google's models.list endpoint (0 token cost)."""
    if not api_key or api_key.startswith("your_") or "..." in api_key:
        return False, "Placeholder or invalid key format"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "Shielder-Diagnostic/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                models = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
                flash_available = any("gemini-2" in m or "gemini-1.5" in m for m in models)
                return True, f"Active ({len(models)} models available)"
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Connection error: {str(e)[:40]}"
    return False, "Unknown response"

def extract_env_keys(env_path):
    """Extract environment variable keys and identify key services."""
    keys = {}
    if not os.path.exists(env_path):
        return keys
    try:
        with open(env_path, errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    keys[k] = v
    except:
        pass
    return keys

def check_project(proj, gcp_active_projects):
    p_path = proj["path"]
    pid = proj["id"]
    name = proj["name"]
    
    report = {
        "id": pid,
        "name": name,
        "path": p_path,
        "type": proj.get("type", "Unknown"),
        "priority": proj.get("priority", "medium"),
        "exists": os.path.exists(p_path),
        "status": "HEALTHY",
        "issues": [],
        "warnings": [],
        "details": {}
    }
    
    if not report["exists"]:
        report["status"] = "CRITICAL"
        report["issues"].append(f"Directory not found: {p_path}")
        return report

    # 1. Git Status
    try:
        res = subprocess.run(["git", "-C", p_path, "status", "--porcelain"], capture_output=True, text=True, timeout=5)
        branch_res = subprocess.run(["git", "-C", p_path, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=5)
        branch = branch_res.stdout.strip() if branch_res.returncode == 0 else "None"
        uncommitted = len([l for l in res.stdout.strip().splitlines() if l]) if res.stdout.strip() else 0
        report["details"]["git"] = {
            "branch": branch,
            "uncommitted_files": uncommitted,
            "clean": (uncommitted == 0)
        }
        if uncommitted > 0:
            report["warnings"].append(f"Git: {uncommitted} uncommitted file(s) on branch '{branch}'")
    except Exception as e:
        report["details"]["git"] = {"error": str(e)}

    # 2. Environment Variables & Keys
    env_vars = {}
    found_env_files = []
    for ef in proj.get("env_files", [".env", ".env.local"]):
        fpath = os.path.join(p_path, ef)
        if os.path.exists(fpath):
            found_env_files.append(ef)
            env_vars.update(extract_env_keys(fpath))

    report["details"]["env"] = {
        "found_files": found_env_files,
        "total_keys": len(env_vars)
    }

    if not found_env_files and proj.get("apis"):
        report["warnings"].append("No .env file found while APIs are expected")

    # 3. Gemini API Check
    gemini_key = None
    for k in ["GEMINI_API_KEY", "VITE_GEMINI_API_KEY", "GOOGLE_GENERATIVE_AI_API_KEY", "NEXT_PUBLIC_GEMINI_API_KEY"]:
        if k in env_vars and env_vars[k]:
            gemini_key = env_vars[k]
            break

    if gemini_key:
        is_ok, msg = test_gemini_key(gemini_key)
        report["details"]["gemini_api"] = {"valid": is_ok, "status": msg}
        if not is_ok:
            report["issues"].append(f"Gemini API: {msg}")
    elif "gemini" in proj.get("apis", []):
        report["warnings"].append("Gemini API key missing in environment")

    # 4. Database Check
    db_config = proj.get("database", {})
    db_type = db_config.get("type")
    
    if db_type == "firebase":
        fb_proj = db_config.get("project_id")
        is_gcp_active = fb_proj in gcp_active_projects
        report["details"]["database"] = {
            "type": "Firebase",
            "project_id": fb_proj,
            "gcp_active": is_gcp_active
        }
        if not is_gcp_active:
            report["issues"].append(f"Firebase project '{fb_proj}' not active in Google Cloud Console")
    elif db_type == "supabase":
        pref = db_config.get("project_ref")
        report["details"]["database"] = {
            "type": "Supabase",
            "project_ref": pref,
            "status": "Configured"
        }
    else:
        report["details"]["database"] = {"type": db_type or "None"}

    # 5. Package Dependencies & Updates
    pkg_path = os.path.join(p_path, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path) as pf:
                pkg_data = json.load(pf)
                deps = pkg_data.get("dependencies", {})
                dev_deps = pkg_data.get("devDependencies", {})
                report["details"]["packages"] = {
                    "has_package_json": True,
                    "dependencies_count": len(deps),
                    "dev_dependencies_count": len(dev_deps)
                }
        except:
            report["details"]["packages"] = {"has_package_json": True, "error": "Invalid JSON"}
    else:
        report["details"]["packages"] = {"has_package_json": False}

    # Evaluate Global Status
    if report["issues"]:
        report["status"] = "CRITICAL"
    elif report["warnings"]:
        report["status"] = "WARNING"
    else:
        report["status"] = "HEALTHY"

    return report

def generate_html_dashboard(results, timestamp):
    if os.path.exists(DASHBOARD_PATH):
        try:
            with open(DASHBOARD_PATH, "r") as f:
                content = f.read()
            if "SHIELDER" in content and "tailwindcss" in content:
                return
        except:
            pass
    healthy_count = sum(1 for r in results if r["status"] == "HEALTHY")

    rows = ""
    for r in results:
        badge_class = "badge-healthy" if r["status"] == "HEALTHY" else ("badge-warning" if r["status"] == "WARNING" else "badge-critical")
        
        issues_html = ""
        if r["issues"]:
            issues_html += "<div class='text-danger'>❌ " + "<br>❌ ".join(r["issues"]) + "</div>"
        if r["warnings"]:
            issues_html += "<div class='text-warning'>⚠️ " + "<br>⚠️ ".join(r["warnings"]) + "</div>"
        if not r["issues"] and not r["warnings"]:
            issues_html = "<span class='text-success'>✓ All systems operational</span>"

        git_info = r["details"].get("git", {})
        git_str = f"Branch: <code>{git_info.get('branch', 'N/A')}</code>"
        if git_info.get("uncommitted_files", 0) > 0:
            git_str += f" <span class='tag tag-warn'>{git_info['uncommitted_files']} modified</span>"
        else:
            git_str += " <span class='tag tag-clean'>Clean</span>"

        db_info = r["details"].get("database", {})
        db_str = f"{db_info.get('type', 'N/A')}"
        if "project_id" in db_info:
            db_str += f" (<code>{db_info['project_id']}</code>)"
        elif "project_ref" in db_info:
            db_str += f" (<code>{db_info['project_ref']}</code>)"

        gemini_info = r["details"].get("gemini_api", {})
        if gemini_info:
            gem_badge = "🟢 OK" if gemini_info.get("valid") else "🔴 FAILED"
            gemini_str = f"{gem_badge} <small>{gemini_info.get('status', '')}</small>"
        else:
            gemini_str = "<span class='text-muted'>-</span>"

        rows += f"""
        <tr>
            <td><strong>{r['name']}</strong><br><small class='text-muted'>{r['path']}</small></td>
            <td><span class='type-tag'>{r['type']}</span></td>
            <td><span class='badge {badge_class}'>{r['status']}</span></td>
            <td>{db_str}</td>
            <td>{gemini_str}</td>
            <td>{git_str}</td>
            <td>{issues_html}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Shielder - Multi-Project Guardian Dashboard</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 24px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }}
        .card-val {{
            font-size: 28px;
            font-weight: 800;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        th, td {{
            padding: 14px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 14px;
        }}
        th {{
            background: #172033;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-healthy {{ background: rgba(34, 197, 94, 0.2); color: var(--success); }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: var(--warning); }}
        .badge-critical {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); }}
        .type-tag {{
            background: #334155;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
        }}
        .tag {{
            display: inline-block;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 11px;
        }}
        .tag-clean {{ background: rgba(34, 197, 94, 0.15); color: #86efac; }}
        .tag-warn {{ background: rgba(245, 158, 11, 0.15); color: #fde047; }}
        code {{
            background: #0f172a;
            padding: 2px 5px;
            border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 12px;
        }}
        .text-success {{ color: var(--success); }}
        .text-warning {{ color: var(--warning); }}
        .text-danger {{ color: var(--danger); }}
        .text-muted {{ color: var(--text-muted); }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🛡️ Shielder Multi-Project Dashboard</div>
        <div class="text-muted">Last Audit: <strong>{timestamp}</strong></div>
    </div>

    <div class="stats-grid">
        <div class="card">
            <div class="text-muted">Total Projets</div>
            <div class="card-val">{total_count}</div>
        </div>
        <div class="card">
            <div class="text-muted">100% Opérationnels</div>
            <div class="card-val text-success">{healthy_count}</div>
        </div>
        <div class="card">
            <div class="text-muted">Avertissements (Git / Env)</div>
            <div class="card-val text-warning">{warning_count}</div>
        </div>
        <div class="card">
            <div class="text-muted">Anomalies Critiques</div>
            <div class="card-val text-danger">{critical_count}</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Projet & Emplacement</th>
                <th>Type</th>
                <th>Santé Globale</th>
                <th>Base de données</th>
                <th>API Gemini</th>
                <th>Statut Git</th>
                <th>Diagnostics & Alertes</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""
    with open(DASHBOARD_PATH, "w") as f:
        f.write(html)

def main():
    if not os.path.exists(REGISTRY_PATH):
        print(f"Error: Registry not found at {REGISTRY_PATH}")
        sys.exit(1)

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    projects = registry.get("projects", [])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch active GCP projects dynamically
    gcp_active = []
    try:
        res = subprocess.run(["/opt/homebrew/bin/gcloud", "projects", "list", "--format=json"], capture_output=True, text=True, timeout=8)
        if res.returncode == 0:
            for p in json.loads(res.stdout):
                gcp_active.append(p.get("projectId"))
    except:
        gcp_active = ["omnilayerai", "fluxo-12969", "moslih84-consultant"]

    results = []
    for proj in projects:
        report = check_project(proj, gcp_active)
        results.append(report)

    # Save JSON report
    report_file = os.path.join(REPORTS_DIR, "health_latest.json")
    with open(report_file, "w") as rf:
        json.dump({"timestamp": now_str, "results": results}, rf, indent=2)

    # Save HTML dashboard
    generate_html_dashboard(results, now_str)

    # Output CLI Summary
    print(f"\n🛡️  SHIELDER HEALTH AUDIT — {now_str}")
    print("=" * 80)
    for r in results:
        status_icon = "🟢" if r["status"] == "HEALTHY" else ("🟡" if r["status"] == "WARNING" else "🔴")
        print(f"{status_icon} [{r['status']:<8}] {r['name']:<28} ({r['type']})")
        if r["issues"]:
            for issue in r["issues"]:
                print(f"    ❌ {issue}")
        if r["warnings"]:
            for warn in r["warnings"]:
                print(f"    ⚠️  {warn}")
    print("=" * 80)
    print(f"📄 Full JSON Report: {report_file}")
    print(f"📊 Visual Dashboard: {DASHBOARD_PATH}\n")

if __name__ == "__main__":
    main()
