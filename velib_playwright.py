# ici l'utilité de ce fichier python est simplement d'aller chercher toutes les lignes du tableau en simulant un 
# scroll de souris car sinon en utilisant justeun script bash, ce n'était pas possible d'accéder aux 1470 lignes
# du tableau mais uniquement aux 80 premières lignes. Ce code python aide uniquement à récupérer toutes les lignes
#  mais n'est pas un scrapper, le scrapper est bien le script bash.

from playwright.sync_api import sync_playwright
import sys
from datetime import datetime

# Utilise l'argument de ligne de commande, ou timestamp par défaut
if len(sys.argv) > 1:
    html_filename = sys.argv[1]
else:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"velib_page_{timestamp}.html"

def extract_rows(page):
    return page.query_selector_all(".odswidget-table__internal-table-row")

def extract_row_html(row):
    return row.inner_html()

def build_table_html(all_row_htmls):
    table = '<div class="odswidget-table">\n<table class="odswidget-table__internal-table">\n<tbody>\n'
    for row_html in all_row_htmls:
        table += f'<tr class="odswidget-table__internal-table-row">{row_html}</tr>\n'
    table += '</tbody>\n</table>\n</div>'
    return table

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://opendata.paris.fr/explore/embed/dataset/velib-disponibilite-en-temps-reel/table/?disjunctive.is_renting&disjunctive.is_installed&disjunctive.is_returning&disjunctive.name&disjunctive.nom_arrondissement_communes")
    page.wait_for_selector(".odswidget-table__internal-table-row")

    page.mouse.move(300, 300)

    seen_rows = set()
    all_row_htmls = []
    last_total = 0
    same_count = 0
    max_same = 5
    MAX_EXPECTED_ROWS = 1471

    print("Defilement automatique...")

    for _ in range(100):
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(500)

        current_rows = extract_rows(page)
        for row in current_rows:
            html = extract_row_html(row)
            if html not in seen_rows:
                seen_rows.add(html)
                all_row_htmls.append(html)

        current_total = len(all_row_htmls)
        print(f"Lignes collectees : {current_total}")

        if current_total >= MAX_EXPECTED_ROWS:
            print("Toutes les lignes ont ete recuperees.")
            break

        if current_total == last_total:
            same_count += 1
            if same_count >= max_same:
                print("Fin du chargement automatique (aucune nouvelle ligne).")
                break
        else:
            same_count = 0
            last_total = current_total

    final_html = build_table_html(all_row_htmls)

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"{len(all_row_htmls)} lignes sauvegardees dans {html_filename}")
    browser.close()

