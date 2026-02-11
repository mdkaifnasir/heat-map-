import csv
import json

data = []
csv_path = '/Applications/XAMPP/xamppfiles/htdocs/Get-the-Data/maharashtra_mlas_2024_final.csv'
html_path = '/Applications/XAMPP/xamppfiles/htdocs/Get-the-Data/heatmap.html'

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Latitude'] and row['Longitude']:
            try:
                data.append({
                    'lat': float(row['Latitude']),
                    'lng': float(row['Longitude']),
                    'name': row['Constituency Name'],
                    'district': row['District'],
                    'member': row['Member Name'],
                    'party': row['Party']
                })
            except ValueError:
                continue

# Professional Color Mapping (Enterprise Style)
PARTY_COLORS = {
    'BJP': '#FF9933',
    'SHS': '#FF7722',
    'SHS-UBT': '#E35F21',
    'INC': '#19AAED',
    'NCP': '#00B2B2',
    'NCP(SP)': '#0080FF',
    'SP': '#228B22',
    'AIMIM': '#000000',
    'CPI(M)': '#FF0000',
    'Independent': '#808080'
}

# Party Logo Mapping (Official Public Icons)
PARTY_LOGOS = {
    'BJP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Logo_of_the_Bharatiya_Janata_Party.svg/512px-Logo_of_the_Bharatiya_Janata_Party.svg.png',
    'SHS': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Logo_of_Shiv_Sena.svg/512px-Logo_of_Shiv_Sena.svg.png',
    'SHS-UBT': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Shiv_Sena_%28UBT%29_Flaming_Torch_Symbol.png/512px-Shiv_Sena_%28UBT%29_Flaming_Torch_Symbol.png',
    'INC': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Indian_National_Congress_hand_logo.svg/512px-Indian_National_Congress_hand_logo.svg.png',
    'NCP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Nationalist_Congress_Party_logo.svg/512px-Nationalist_Congress_Party_logo.svg.png',
    'NCP(SP)': 'https://upload.wikimedia.org/wikipedia/en/thumb/e/e7/Nationalist_Congress_Party_%28Sharadchandra_Pawar%29_Logo.jpg/512px-Nationalist_Congress_Party_%28Sharadchandra_Pawar%29_Logo.jpg',
    'SP': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Samajwadi_Party.png/512px-Samajwadi_Party.png',
    'AIMIM': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/All_India_Majlis-e-Ittehadul_Muslimeen_logo.svg/512px-All_India_Majlis-e-Ittehadul_Muslimeen_logo.svg.png',
    'CPI(M)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/CPI-M-flag.svg/512px-CPI-M-flag.svg.png',
    'Independent': 'https://cdn-icons-png.flaticon.com/512/1144/1144760.png'
}

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maharashtra MLA Intelligence Report 2024</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bi-blue: #001F3F;
            --bi-gold: #FFD700;
            --bi-grey: #F3F2F1;
            --bi-border: #EDEBE9;
            --bi-text: #323130;
            --bi-accent: #0078D4;
        }}

        body, html {{
            margin: 0; padding: 0; height: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bi-grey);
            color: var(--bi-text);
            overflow: hidden;
        }}

        /* Grid Layout */
        .container {{
            display: grid;
            grid-template-areas: 
                "header header header"
                "slicers canvas visuals";
            grid-template-columns: 260px 1fr 340px;
            grid-template-rows: 48px 1fr;
            height: 100vh;
            width: 100vw;
        }}

        /* Header */
        header {{
            grid-area: header;
            background-color: var(--bi-blue);
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            z-index: 1000;
        }}

        .brand {{ font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 10px; }}
        .report-name {{ font-size: 14px; opacity: 0.8; }}

        /* Left Side (Slicers) */
        .slicers {{
            grid-area: slicers;
            background: white;
            border-right: 1px solid var(--bi-border);
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        .slicer-tile {{
            border: 1px solid var(--bi-border);
            border-radius: 4px;
            background: #FAF9F8;
        }}

        .slicer-header {{
            background: #E1DFDD;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            border-bottom: 1px solid var(--bi-border);
        }}

        .slicer-content {{ padding: 10px; }}

        input[type="text"], select {{
            width: 100%;
            border: 1px solid var(--bi-border);
            padding: 8px;
            font-family: inherit;
            font-size: 13px;
            box-sizing: border-box;
            outline-color: var(--bi-accent);
        }}

        /* Main Canvas (Map) */
        .canvas {{
            grid-area: canvas;
            position: relative;
            background: #FFF;
        }}

        #map {{ height: 100%; width: 100%; }}

        /* Right Side (Visuals) */
        .visuals {{
            grid-area: visuals;
            background: white;
            border-left: 1px solid var(--bi-border);
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .card-tile {{
            background: white;
            border: 1px solid var(--bi-border);
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            position: relative;
        }}

        .card-header {{
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 600;
            border-bottom: 1px solid var(--bi-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .card-body {{ padding: 12px; min-height: 100px; }}

        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: 600; color: var(--bi-accent); display: block; }}
        .metric-label {{ font-size: 11px; color: #605E5C; text-transform: uppercase; }}

        .chart-container {{ height: 200px; width: 100%; }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}

        .data-table tr:nth-child(even) {{ background: #FAF9F8; }}
        .data-table td {{ padding: 8px 4px; border-bottom: 1px solid var(--bi-border); }}

        /* Logo Styling */
        .party-logo-main {{
            width: 60px;
            height: 60px;
            object-fit: contain;
            margin: 0 auto 10px auto;
            display: block;
        }}
        .party-logo-small {{
            width: 20px;
            height: 20px;
            object-fit: contain;
            vertical-align: middle;
            margin-right: 5px;
        }}

        /* BI Specific Visuals */
        .color-bar {{ height: 4px; width: 100%; position: absolute; top: 0; left: 0; }}

        /* Export Button */
        #export-csv {{
            background: var(--bi-accent);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 2px;
            font-size: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: opacity 0.2s;
        }}
        #export-csv:hover {{ opacity: 0.9; }}

        /* Responsive */
        @media (max-width: 1024px) {{
            .container {{
                grid-template-areas: 
                    "header header"
                    "slicers canvas"
                    "visuals visuals";
                grid-template-columns: 240px 1fr;
                grid-template-rows: 48px 1fr auto;
            }}
            .visuals {{ border-left: none; border-top: 1px solid var(--bi-border); flex-direction: row; flex-wrap: wrap; }}
            .card-tile {{ flex: 1; min-width: 250px; }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <header>
            <div class="brand">
                <div style="background: var(--bi-gold); width: 24px; height: 24px; border-radius: 4px;"></div>
                Maharashtra Intelligence Report
            </div>
            <div class="report-name">Election Dashboard 2024 / Live Analysis</div>
            <button id="export-csv">Export Current View (.csv)</button>
        </header>

        <section class="slicers">
            <div class="slicer-tile">
                <div class="slicer-header">Search Filters</div>
                <div class="slicer-content">
                    <input type="text" id="search-input" placeholder="Search Constituency or MLA...">
                </div>
            </div>

            <div class="slicer-tile">
                <div class="slicer-header">Party Slicer</div>
                <div class="slicer-content">
                    <select id="party-filter">
                        <option value="all">All Political Parties</option>
                    </select>
                </div>
            </div>

            <div class="card-tile">
                <div class="card-header">Report Summary</div>
                <div class="card-body" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="metric">
                        <span class="metric-value" id="count-value">288</span>
                        <span class="metric-label">Seats</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value" id="dist-count-value">36</span>
                        <span class="metric-label">Districts</span>
                    </div>
                </div>
            </div>
        </section>

        <main class="canvas">
            <div id="map"></div>
        </main>

        <section class="visuals">
            <div class="card-tile">
                <div class="color-bar" style="background: var(--bi-accent);"></div>
                <div class="card-header">Party Distribution (Top 5)</div>
                <div class="card-body">
                    <div class="chart-container">
                        <canvas id="partyChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="card-tile">
                <div class="color-bar" style="background: #107C10;"></div>
                <div class="card-header">Dominating Political Power</div>
                <div class="card-body metric">
                    <img id="dominating-logo" src="" class="party-logo-main" style="display: none;">
                    <span class="metric-value" id="dominating-party" style="font-size: 24px;">-</span>
                    <span class="metric-label">Majority Unit</span>
                </div>
            </div>

            <div class="card-tile">
                <div class="color-bar" style="background: #D83B01;"></div>
                <div class="card-header">District Rankings</div>
                <div class="card-body">
                    <table class="data-table" id="district-rankings"></table>
                </div>
            </div>
        </section>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
    <script>
        const mapData = {data_json};
        const PARTY_COLORS = {party_colors_json};
        const PARTY_LOGOS = {party_logos_json};
        let myChart = null;

        // Initialize Slicers
        const parties = ["all", ...new Set(mapData.map(d => d.party))].sort();
        const partyFilter = document.getElementById('party-filter');
        parties.filter(p => p !== "all").forEach(p => {{
            const opt = document.createElement('option');
            opt.value = p; opt.textContent = p;
            partyFilter.appendChild(opt);
        }});

        // Map Setup
        const lightMap = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png');
        const satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
        
        const map = L.map('map', {{ zoomControl: false, attributionControl: false, layers: [lightMap] }}).setView([19.7515, 75.7139], 7);
        
        const baseMaps = {{ "Road": lightMap, "Satellite": satelliteMap }};
        L.control.layers(baseMaps, null, {{ position: 'topright' }}).addTo(map);
        L.control.zoom({{ position: 'bottomleft' }}).addTo(map);

        const heat = L.heatLayer([], {{ radius: 30, blur: 20, maxZoom: 14, 
            gradient: {{0.4: 'rgba(0,120,212,0.4)', 0.6: 'cyan', 0.8: 'gold', 1.0: 'crimson'}} 
        }}).addTo(map);
        const markerGroup = L.layerGroup().addTo(map);

        function getPartyLogo(party) {{
            return PARTY_LOGOS[party] || 'https://cdn-icons-png.flaticon.com/512/1144/1144760.png';
        }}

        function handleImageError(img, party) {{
            img.style.display = 'none';
            const parent = img.parentElement;
            if (parent && !parent.querySelector('.party-fallback')) {{
                const fallback = document.createElement('div');
                fallback.className = 'party-fallback';
                fallback.style.background = PARTY_COLORS[party] || '#0078D4';
                fallback.style.color = 'white';
                fallback.style.borderRadius = '4px';
                fallback.style.width = '48px';
                fallback.style.height = '48px';
                fallback.style.display = 'flex';
                fallback.style.alignItems = 'center';
                fallback.style.justifyContent = 'center';
                fallback.style.fontSize = '12px';
                fallback.style.fontWeight = '600';
                fallback.style.margin = '0 auto 10px';
                fallback.textContent = party.substring(0, 3);
                parent.prepend(fallback);
            }}
        }}

        function updateDisplay() {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const selectedParty = document.getElementById('party-filter').value;
            
            const filteredData = mapData.filter(d => {{
                const matchesSearch = d.name.toLowerCase().includes(searchTerm) || d.member.toLowerCase().includes(searchTerm);
                const matchesParty = selectedParty === 'all' || d.party === selectedParty;
                return matchesSearch && matchesParty;
            }});

            document.getElementById('count-value').textContent = filteredData.length;
            document.getElementById('dist-count-value').textContent = [...new Set(filteredData.map(d => d.district))].length;

            heat.setLatLngs(filteredData.map(d => [d.lat, d.lng, 0.8]));
            markerGroup.clearLayers();
            
            filteredData.forEach(d => {{
                const pColor = PARTY_COLORS[d.party] || '#0078D4';
                const pLogo = getPartyLogo(d.party);
                const marker = L.circleMarker([d.lat, d.lng], {{
                    radius: 5, fillColor: pColor, color: '#fff', weight: 1, opacity: 0.8, fillOpacity: 0.9
                }});
                marker.bindPopup(`<div style="font-family: 'Segoe UI'; min-width: 150px; text-align: center;">
                    <img src="${{pLogo}}" class="party-logo-small" onerror="handleImageError(this, '${{d.party}}')">
                    <b style="color:${{pColor}}; font-size: 14px; display: block;">${{d.name}}</b>
                    <span style="font-size: 12px; color: #605E5C;">${{d.district}}</span><hr style="border: 0; border-top: 1px solid #EDEBE9;">
                    <span style="font-size: 12px; font-weight: 600;">MLA: ${{d.member}}</span><br>
                    <span style="font-size: 11px; color: #605E5C;">${{d.party}}</span>
                </div>`);
                markerGroup.addLayer(marker);
            }});

            updateAnalysis(filteredData);
            if (filteredData.length > 0 && (searchTerm || selectedParty !== 'all')) {{
                const bounds = L.latLngBounds(filteredData.map(d => [d.lat, d.lng]));
                map.flyToBounds(bounds.pad(0.3), {{ duration: 0.8 }});
            }}
        }}

        function updateAnalysis(data) {{
            if (data.length === 0) {{
                 if (myChart) myChart.destroy();
                 document.getElementById('dominating-party').textContent = '-';
                 document.getElementById('dominating-logo').style.display = 'none';
                 const existingFallback = document.querySelector('.card-body .party-fallback');
                 if (existingFallback) existingFallback.remove();
                 document.getElementById('district-rankings').innerHTML = '';
                 return;
            }}
            const partyCount = {{}};
            data.forEach(d => partyCount[d.party] = (partyCount[d.party] || 0) + 1);
            const sorted = Object.entries(partyCount).sort((a,b) => b[1] - a[1]);
            
            const mainParty = sorted[0][0];
            const pLogo = getPartyLogo(mainParty);
            
            document.getElementById('dominating-party').textContent = mainParty;
            document.getElementById('dominating-party').style.color = PARTY_COLORS[mainParty] || '#0078D4';
            
            const domLogo = document.getElementById('dominating-logo');
            domLogo.src = pLogo;
            domLogo.style.display = 'block';
            domLogo.onerror = () => handleImageError(domLogo, mainParty);
            const existingFallback = domLogo.parentElement.querySelector('.party-fallback');
            if (existingFallback) existingFallback.remove();

            const labels = sorted.slice(0, 5).map(p => p[0]);
            const values = sorted.slice(0, 5).map(p => p[1]);
            const colors = labels.map(l => PARTY_COLORS[l] || '#0078D4');

            const ctx = document.getElementById('partyChart').getContext('2d');
            if (myChart) myChart.destroy();
            myChart = new Chart(ctx, {{
                type: 'bar',
                data: {{ 
                    labels: labels, 
                    datasets: [{{ 
                        label: 'Seats',
                        data: values, 
                        backgroundColor: colors,
                        borderRadius: 4
                    }}] 
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true, maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ x: {{ grid: {{ display: false }} }}, y: {{ grid: {{ display: false }} }} }},
                    onClick: (evt, elements) => {{
                        if (elements.length > 0) {{
                            const index = elements[0].index;
                            document.getElementById('party-filter').value = labels[index];
                            updateDisplay();
                        }}
                    }}
                }}
            }});

            const distCount = {{}};
            data.forEach(d => distCount[d.district] = (distCount[d.district] || 0) + 1);
            const rankedDist = Object.entries(distCount).sort((a,b) => b[1] - a[1]).slice(0,5);
            document.getElementById('district-rankings').innerHTML = rankedDist.map(d => `
                <tr>
                    <td style="font-weight: 600; color: #323130;">${{d[0]}}</td>
                    <td style="text-align: right; color: var(--bi-accent); font-weight: 600;">${{d[1]}}</td>
                </tr>
            `).join('');
        }}

        document.getElementById('search-input').oninput = updateDisplay;
        document.getElementById('party-filter').onchange = updateDisplay;

        document.getElementById('export-csv').onclick = () => {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const selectedParty = document.getElementById('party-filter').value;
            const filtered = mapData.filter(d => {{
                const matchesSearch = d.name.toLowerCase().includes(searchTerm) || d.member.toLowerCase().includes(searchTerm);
                const matchesParty = selectedParty === 'all' || d.party === selectedParty;
                return matchesSearch && matchesParty;
            }});

            let csv = 'Constituency,District,MLA,Party,Latitude,Longitude\\n';
            filtered.forEach(d => {{
                csv += `"${{d.name}}","${{d.district}}","${{d.member}}","${{d.party}}",${{d.lat}},${{d.lng}}\\n`;
            }});

            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('hidden', ''); a.setAttribute('href', url);
            a.setAttribute('download', 'powerbi_logo_report_export.csv');
            document.body.appendChild(a);
            a.click(); document.body.removeChild(a);
        }};

        updateDisplay();
    </script>
</body>
</html>
"""

final_html = html_template.format(
    data_json=json.dumps(data),
    party_colors_json=json.dumps(PARTY_COLORS),
    party_logos_json=json.dumps(PARTY_LOGOS)
)

with open(html_path, 'w') as f:
    f.write(final_html)

print(f"Successfully generated Power BI report with logos at {{html_path}}.")
