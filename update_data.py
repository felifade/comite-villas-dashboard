import csv
import json
import urllib.request
import subprocess
import os

url = "https://docs.google.com/spreadsheets/d/1sN4CdRS55hwOFjYKb8XHQWeebyYunkvMNf0HYG9K7bY/export?format=csv&gid=0"

print("Descargando últimos datos de Google Sheets...")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    csv_bytes = response.read()
    csv_content = csv_bytes.decode('utf-8', errors='replace')
except Exception as e:
    print("Error al descargar los datos de Google Sheets:", e)
    exit(1)

# Parsear CSV
lines = csv_content.splitlines()
reader = csv.reader(lines)
rows = list(reader)

print(f"Se descargaron {len(rows)} filas de datos.")

try:
    # 1. Extraer métricas globales
    balance = rows[0][3].strip() if len(rows[0]) > 3 else ""
    inputs = rows[0][6].strip() if len(rows[0]) > 6 else ""
    gastos = rows[0][8].strip() if len(rows[0]) > 8 else ""

    print(f"Métricas globales: Saldo={balance}, Ingresos={inputs}, Egresos={gastos}")

    # 2. Extraer cabeceras mensuales
    row2 = rows[2]
    row3 = rows[3]

    months = []
    for idx in range(5, len(row3)):
        month_name = row3[idx].strip()
        if not month_name:
            continue
        
        year = ""
        for y_idx in range(idx, 4, -1):
            if y_idx < len(row2) and row2[y_idx].strip() in ["2024", "2025", "2026"]:
                year = row2[y_idx].strip()
                break
        if not year:
            year = "2023"
            
        months.append({
            "col_idx": idx,
            "name": month_name,
            "year": year
        })

    # 3. Extraer casas
    houses = []
    for r_idx in range(5, 37):
        row = rows[r_idx]
        house_id = row[0].strip()
        status = row[1].strip()
        controls = row[2].strip() if len(row) > 2 else ""
        resident = row[3].strip() if len(row) > 3 else ""
        gate_coop = row[4].strip() if len(row) > 4 else ""
        
        monthly_payments = {}
        for m in months:
            val = row[m["col_idx"]].strip() if m["col_idx"] < len(row) else ""
            monthly_payments[f"{m['name']}_{m['year']}"] = val
            
        houses.append({
            "id": house_id,
            "status": status,
            "controls": controls,
            "resident": resident,
            "gate_coop": gate_coop,
            "payments": monthly_payments
        })

    # 4. Extraer gastos detallados
    amounts_row = rows[38]
    category_row = rows[37]
    desc_short_row = rows[39] if len(rows) > 39 else []
    desc_long_row = rows[40] if len(rows) > 40 else []
    desc_extra_row = rows[41] if len(rows) > 41 else []

    transfer_desc = desc_short_row[1].strip() if len(desc_short_row) > 1 else ""

    # Cargar base de datos local anterior para buscar descripciones históricas detalladas
    local_json_path = os.path.join(os.path.dirname(__file__), "comite_data.json")
    local_expenses = []
    if os.path.exists(local_json_path):
        try:
            with open(local_json_path, 'r', encoding='utf-8') as lf:
                local_data = json.load(lf)
                local_expenses = local_data.get("expenses", [])
        except:
            pass

    expenses = []
    for m in months:
        col = m["col_idx"]
        amount = amounts_row[col].strip() if col < len(amounts_row) else ""
        if not amount or amount == "$0.00" or amount == "0":
            continue
            
        header_desc = ""
        for h_col in range(col, 4, -1):
            if h_col < len(category_row) and category_row[h_col].strip() and category_row[h_col].strip() != "INFORME DE GASTOS":
                header_desc = category_row[h_col].strip()
                break
                
        desc_short = desc_short_row[col].strip() if col < len(desc_short_row) else ""
        desc_long = desc_long_row[col].strip() if col < len(desc_long_row) else ""
        desc_extra = desc_extra_row[col].strip() if col < len(desc_extra_row) else ""

        desc = []
        if header_desc:
            desc.append(header_desc)
        if desc_long:
            desc.append(desc_long)
        if desc_extra:
            desc.append(desc_extra)
            
        full_desc = " | ".join(desc) if desc else desc_short
        if not full_desc:
            if col == 5:
                full_desc = desc_short_row[3].strip() if len(desc_short_row) > 3 else ""

        # Usar descripción detallada anterior si la actual está vacía o es solo un número
        if not full_desc or full_desc.replace("$", "").replace(",", "").replace(".", "").strip().isdigit():
            for le in local_expenses:
                if le["month"] == m["name"] and le["year"] == m["year"] and le.get("description"):
                    full_desc = le["description"]
                    break

        expenses.append({
            "month": m["name"],
            "year": m["year"],
            "amount": amount,
            "description": full_desc
        })

    data = {
        "balance": balance,
        "inputs": inputs,
        "gastos": gastos,
        "transfer_from_previous": transfer_desc,
        "months": months,
        "houses": houses,
        "expenses": expenses
    }

    # Guardar en comite_data.json
    with open(local_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Guardado comite_data.json con éxito.")

    # Actualizar index.html incrustando los nuevos datos de fallback
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        start_marker = "        let COMITE_DATA = {"
        end_marker = "        let balanceChartInstance = null;"

        start_idx = html_content.find(start_marker)
        end_idx = html_content.find(end_marker)

        if start_idx != -1 and end_idx != -1:
            indented_json = json.dumps(data, indent=2, ensure_ascii=False)
            json_lines = indented_json.splitlines()
            indented_json_str = "\n".join("        " + line for line in json_lines)
            
            replacement = f"        let COMITE_DATA = {indented_json_str.strip()};\n\n"
            new_html_content = html_content[:start_idx] + replacement + html_content[end_idx:]
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_html_content)
            print("index.html actualizado y compilado con éxito.")
        else:
            print("Error: No se encontraron los marcadores de COMITE_DATA en index.html.")
    else:
        print("Error: No se encontró index.html.")

    # Realizar commit y push automático a GitHub
    print("Subiendo cambios a GitHub...")
    subprocess.run(["git", "add", "comite_data.json", "index.html"], check=True)
    subprocess.run(["git", "commit", "-m", "Auto-update: Sincronización de datos con Google Sheets"], capture_output=True)
    result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("¡Cambios subidos a GitHub exitosamente!")
    else:
        print("Error al hacer push a GitHub:", result.stderr)

except Exception as e:
    import traceback
    print("Error procesando los datos:")
    traceback.print_exc()
    exit(1)
