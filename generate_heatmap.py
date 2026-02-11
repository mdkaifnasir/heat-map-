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

# Professional Color Mapping
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

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maharashtra MLA Intelligence Dashboard 2024</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #f8fafc;
            --card-bg: rgba(255, 255, 255, 0.9);
            --accent-color: #7c3aed;
            --text-color: #1e293b;
            --glass-border: rgba(0, 0, 0, 0.1);
        }}

        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            overflow: hidden;
        }}

        #map {{
            height: 100vh;
            width: 100vw;
            z-index: 1;
        }}

        .overlay {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            padding: 24px;
            border-radius: 20px;
            border: 1px dashed var(--glass-border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            max-width: 320px;
            transition: all 0.3s ease;
        }}

        .analysis-panel {{
            position: absolute;
            top: 20px;
            right: -400px;
            bottom: 20px;
            width: 350px;
            z-index: 1001;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            padding: 24px;
            border-radius: 24px;
            border: 1px solid var(--glass-border);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
            transition: right 0.6s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow-y: auto;
        }}

        .analysis-panel.open {{
            right: 20px;
        }}

        h1, h2 {{
            margin: 0 0 8px 0;
            font-weight: 600;
            background: linear-gradient(135deg, #7c3aed, #2563eb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        h1 {{ font-size: 20px; letter-spacing: -0.5px; }}
        h2 {{ font-size: 18px; }}

        .filters {{
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .filter-group label {{
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 600;
            color: #94a3b8;
            margin-bottom: 4px;
            display: block;
        }}

        input[type="text"], select {{
            width: 100%;
            background: rgba(0, 0, 0, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 10px 12px;
            color: var(--text-color);
            font-family: inherit;
            box-sizing: border-box;
            outline: none;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }}

        .stat-box {{
            background: #fff;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            text-align: center;
        }}

        .stat-box span {{ display: block; }}
        .stat-num {{ font-size: 22px; font-weight: 600; color: var(--accent-color); }}
        .stat-tag {{ font-size: 10px; color: #64748b; text-transform: uppercase; }}

        .actions {{
            display: flex;
            gap: 10px;
            margin-top: 5px;
        }}

        .btn {{
            flex: 1;
            padding: 12px;
            border-radius: 12px;
            border: none;
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
        }}

        .btn-primary {{ background: var(--accent-color); color: white; }}
        .btn-outline {{ background: white; border: 1px solid var(--accent-color); color: var(--accent-color); }}

        #toggle-analysis {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1002;
            padding: 12px 24px;
            background: white;
            border: 1px solid var(--glass-border);
            border-radius: 30px;
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: all 0.3s;
        }}

        #toggle-analysis.active {{
            background: var(--accent-color);
            color: white;
        }}

        /* Responsive Mobile */
        @media (max-width: 768px) {{
            .overlay {{
                top: auto;
                bottom: 20px;
                left: 10px;
                right: 10px;
                max-width: none;
                border-radius: 24px;
            }}
            .analysis-panel {{
                width: 100%;
                height: 70vh;
                right: 0;
                bottom: -100%;
                top: auto;
                border-radius: 32px 32px 0 0;
                transition: bottom 0.5s ease;
            }}
            .analysis-panel.open {{ bottom: 0; }}
            #toggle-analysis {{ top: 10px; right: 10px; padding: 10px 18px; font-size: 12px; }}
        }}

        .chart-box {{
            height: 220px;
            width: 100%;
        }}

        .district-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        .district-table td {{ padding: 10px 0; border-bottom: 1px solid rgba(0,0,0,0.05); }}
        .district-table tr:last-child td {{ border: none; }}

        /* Leaflet Controls Customization */
        .leaflet-control-layers {{
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }}
    </style>
</head>
<body>
    <button id="toggle-analysis">📊 Analysis Dashboard</button>

    <div class="overlay" id="main-overlay">
        <h1>MLA Intel Hub</h1>
        <p style="font-size: 12px; color: #64748b; margin-top: -5px;">Maharashtra State 2024</p>
        
        <div class="filters">
            <div class="filter-group">
                <label>Dynamic Search</label>
                <input type="text" id="search-input" placeholder="Search Constituency or MLA...">
            </div>
            <div class="filter-group">
                <label>Filter by Party</label>
                <select id="party-filter">
                    <option value="all">All Political Units</option>
                </select>
            </div>
            <div class="actions">
                <button class="btn btn-outline" id="export-csv">📥 Export CSV</button>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <span class="stat-num" id="count-value">288</span>
                <span class="stat-tag">Seats</span>
            </div>
            <div class="stat-box">
                <span class="stat-num" id="dist-count-value">36</span>
                <span class="stat-tag">Districts</span>
            </div>
        </div>
    </div>

    <div class="analysis-panel" id="analysis-panel">
        <h2 style="display: flex; justify-content: space-between; align-items: center;">
            Strategic Insights
            <span style="font-size: 10px; color: #94a3b8; font-weight: normal;">Live Update</span>
        </h2>
        
        <div class="stat-box" style="padding: 20px;">
            <span class="stat-tag">Dominating Sentiment</span>
            <span class="stat-num" id="dominating-party" style="font-size: 28px;">-</span>
        </div>

        <div>
            <span class="stat-tag" style="margin-bottom: 10px; display: block;">Party Market Share</span>
            <div class="chart-box">
                <canvas id="partyChart"></canvas>
            </div>
            <p style="font-size: 10px; text-align: center; color: #94a3b8; margin-top: 10px;">Click segments to filter map</p>
        </div>

        <div>
            <span class="stat-tag" style="margin-bottom: 15px; display: block;">District Dominance (Top 5)</span>
            <table class="district-table" id="district-rankings"></table>
        </div>
    </div>

    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
    <script>
        const mapData = {data_json};
        const PARTY_COLORS = {party_colors_json};
        let myChart = null;

        // Initialize Filter UI
        const parties = ["all", ...new Set(mapData.map(d => d.party))].sort();
        const partyFilter = document.getElementById('party-filter');
        parties.filter(p => p !== "all").forEach(p => {{
            const opt = document.createElement('option');
            opt.value = p; opt.textContent = p;
            partyFilter.appendChild(opt);
        }});

        // Map Setup with Layer Control
        const lightMap = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png');
        const satelliteMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}');
        
        const map = L.map('map', {{ zoomControl: false, attributionControl: false, layers: [lightMap] }}).setView([19.7515, 75.7139], 7);
        
        const baseMaps = {{ "Clean Light": lightMap, "Geospatial Satellite": satelliteMap }};
        L.control.layers(baseMaps, null, {{ position: 'topright' }}).addTo(map);
        L.control.zoom({{ position: 'bottomleft' }}).addTo(map);

        const heat = L.heatLayer([], {{ radius: 35, blur: 25, maxZoom: 14, 
            gradient: {{0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}} 
        }}).addTo(map);
        const markerGroup = L.layerGroup().addTo(map);

        // Core Functions
        function getPartyColor(party) {{
            return PARTY_COLORS[party] || '#7c3aed';
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

            heat.setLatLngs(filteredData.map(d => [d.lat, d.lng, 1.0]));
            markerGroup.clearLayers();
            
            filteredData.forEach(d => {{
                const pColor = getPartyColor(d.party);
                const marker = L.circleMarker([d.lat, d.lng], {{
                    radius: 5, fillColor: pColor, color: '#fff', weight: 1.5, opacity: 0.8, fillOpacity: 0.9
                }});
                marker.bindPopup(`<div style="font-family: 'Outfit';">
                    <b style="color:${{pColor}}; font-size: 16px;">${{d.name}}</b><br>
                    <span style="font-size: 13px;">${{d.district}} District</span><hr style="opacity: 0.1">
                    <span style="font-size: 12px; font-weight: 600;">MLA: ${{d.member}}</span><br>
                    <span style="font-size: 11px; color: #64748b;">${{d.party}}</span>
                </div>`);
                markerGroup.addLayer(marker);
            }});

            updateAnalysis(filteredData);
            if (filteredData.length > 0 && (searchTerm || selectedParty !== 'all')) {{
                const bounds = L.latLngBounds(filteredData.map(d => [d.lat, d.lng]));
                map.flyToBounds(bounds.pad(0.2), {{ duration: 0.6 }});
            }}
        }}

        function updateAnalysis(data) {{
            if (data.length === 0) return;
            const partyCount = {{}};
            data.forEach(d => partyCount[d.party] = (partyCount[d.party] || 0) + 1);
            const sorted = Object.entries(partyCount).sort((a,b) => b[1] - a[1]);
            
            document.getElementById('dominating-party').textContent = sorted[0][0];
            document.getElementById('dominating-party').style.color = getPartyColor(sorted[0][0]);

            const labels = sorted.slice(0, 5).map(p => p[0]);
            const values = sorted.slice(0, 5).map(p => p[1]);
            const colors = labels.map(l => getPartyColor(l));

            const ctx = document.getElementById('partyChart').getContext('2d');
            if (myChart) myChart.destroy();
            myChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{ labels: labels, datasets: [{{ data: values, backgroundColor: colors, borderWidth: 0 }}] }},
                options: {{
                    responsive: true, maintainAspectRatio: false, cutout: '75%',
                    plugins: {{ legend: {{ display: false }} }},
                    onClick: (evt, elements) => {{
                        if (elements.length > 0) {{
                            const index = elements[0].index;
                            const party = labels[index];
                            document.getElementById('party-filter').value = party;
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
                    <td style="font-weight: 600;">${{d[0]}}</td>
                    <td style="text-align: right; color: var(--accent-color); font-weight: 600;">${{d[1]}} Seats</td>
                </tr>
            `).join('');
        }}

        // Controls
        document.getElementById('toggle-analysis').onclick = (e) => {{
            const panel = document.getElementById('analysis-panel');
            panel.classList.toggle('open');
            e.target.classList.toggle('active');
        }};

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
            a.setAttribute('hidden', '');
            a.setAttribute('href', url);
            a.setAttribute('download', 'maharashtra_mla_filtered.csv');
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }};

        updateDisplay();
    </script>
</body>
</html>
"""

final_html = html_template.format(
    data_json=json.dumps(data),
    party_colors_json=json.dumps(PARTY_COLORS)
)

with open(html_path, 'w') as f:
    f.write(final_html)

print(f"Successfully generated {{html_path}} with extreme features.")
