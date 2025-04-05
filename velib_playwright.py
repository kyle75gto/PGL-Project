from playwright.sync_api import sync_playwright

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

MAX_EXPECTED_ROWS = 1471

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://opendata.paris.fr/explore/embed/dataset/velib-disponibilite-en-temps-reel/table/?disjunctive.is_renting&disjunctive.is_installed&disjunctive.is_returning&disjunctive.name&disjunctive.nom_arrondissement_communes")
    page.wait_for_selector(".odswidget-table__internal-table-row")

    page.mouse.move(300, 300)

    seen_rows = set()
    all_row_htmls = []

    print("Défilement réel avec la souris...")

    for _ in range(100):  # 100 scrolls max (on s'arrête avant si complet)
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(500)

        current_rows = extract_rows(page)

        for row in current_rows:
            html = extract_row_html(row)
            if html not in seen_rows:
                seen_rows.add(html)
                all_row_htmls.append(html)

        current_total = len(all_row_htmls)
        print(f"Lignes collectées : {current_total}")

        if current_total >= MAX_EXPECTED_ROWS:
            print("Toutes les lignes ont été récupérées.")
            break

    final_html = build_table_html(all_row_htmls)
    with open("velib_page.html", "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"{len(all_row_htmls)} lignes sauvegardées dans velib_page.html")
    browser.close()
