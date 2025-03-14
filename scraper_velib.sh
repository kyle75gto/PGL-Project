URL="https://opendata.paris.fr/explore/embed/dataset/velib-disponibilite-en-temps-reel/table/?disjunctive.is_renting&disjunctive.is_installed&disjunctive.is_returning&disjunctive.name&disjunctive.nom_arrondissement_communes&sort=duedate"
HTML_FILE="velib_page.html"
CSV_FILE="velib_data.csv"
CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"


# 📌 1️⃣ Utiliser Chrome Headless pour capturer le vrai HTML avec JavaScript exécuté
"$CHROME_PATH" --headless --disable-gpu --virtual-time-budget=5000 --dump-dom "$URL" > "$HTML_FILE"

if [ ! -s "$HTML_FILE" ]; then
    echo "❌ ERREUR : Chrome n'a pas récupéré le HTML."
    exit 1
fi

# 📌 3️⃣ Extraire les Identifiants des stations
grep -oP '<span title="\K\d+' "$HTML_FILE" > station_ids.txt

# 📌 4️⃣ Extraire les Noms des stations
grep -oP '<span title="\K[^"]+' "$HTML_FILE" | sed -n '2~2p' > station_names.txt

# 📌 5️⃣ Extraire les Coordonnées géographiques
grep -oP '<span class="geotooltip[^>]+>\K[0-9\., ]+(?=</span>)' "$HTML_FILE" | sed 's/ /,/g' > station_coords.txt

# 📌 6️⃣ Fusionner les fichiers en CSV
echo "Identifiant,Nom Station,Coordonnées" > "$CSV_FILE"
paste -d ',' station_ids.txt station_names.txt station_coords.txt >> "$CSV_FILE"

# Nettoyage des fichiers temporaires
rm station_ids.txt station_names.txt station_coords.txt

echo "✅ Extraction terminée ! Fichier disponible : $CSV_FILE"