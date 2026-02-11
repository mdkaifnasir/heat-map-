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

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Maharashtra MLA Heatmap 2024</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f8fafc;
            --card-bg: rgba(255, 255, 255, 0.85);
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
            border: 1px solid var(--glass-border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            max-width: 320px;
            animation: fadeIn 0.8s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        h1 {{
            margin: 0 0 8px 0;
            font-size: 22px;
            font-weight: 600;
            background: linear-gradient(to right, #7c3aed, #db2777);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        p {{
            margin: 0;
            font-size: 14px;
            color: #475569;
            line-height: 1.5;
        }}

        .stats {{
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}

        .stat-card {{
            background: rgba(0, 0, 0, 0.03);
            padding: 12px;
            border-radius: 12px;
            text-align: center;
        }}

        .stat-value {{
            display: block;
            font-size: 20px;
            font-weight: 600;
            color: var(--accent-color);
        }}

        .stat-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
        }}

        .leaflet-popup-content-wrapper {{
            background: var(--card-bg) !important;
            backdrop-filter: blur(12px) !important;
            color: var(--text-color) !important;
            border-radius: 12px !important;
            border: 1px solid var(--glass-border) !important;
            padding: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }}

        .leaflet-popup-tip {{
            background: var(--card-bg) !important;
        }}

        .custom-popup b {{
            color: var(--accent-color);
            display: block;
            margin-bottom: 4px;
            font-size: 16px;
        }}

        .custom-popup span {{
            font-size: 13px;
            color: #475569;
        }}

        .filters {{
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .filter-group label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94a3b8;
        }}

        input[type="text"], select {{
            background: rgba(0, 0, 0, 0.05);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 10px;
            color: var(--text-color);
            font-family: inherit;
            font-size: 13px;
            transition: border-color 0.2s;
        }}

        input[type="text"]:focus, select:focus {{
            outline: none;
            border-color: var(--accent-color);
            background: rgba(255, 255, 255, 0.9);
        }}

        .legend {{
            position: absolute;
            bottom: 30px;
            right: 20px;
            z-index: 1000;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            padding: 15px;
            border-radius: 15px;
            border: 1px solid var(--glass-border);
            font-size: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}

        .gradient-bar {{
            width: 100px;
            height: 10px;
            background: linear-gradient(to right, blue, cyan, lime, yellow, red);
            border-radius: 5px;
            margin: 0 10px;
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(0, 0, 0, 0.1);
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="overlay">
        <h1>Maharashtra MLA Heatmap</h1>
        <p>Visualizing the density and distribution of 288 constituencies across the state based on the 2024 Election data.</p>
        
        <div class="filters">
            <div class="filter-group">
                <label>Search Constituency/MLA</label>
                <input type="text" id="search-input" placeholder="Search name...">
            </div>
            <div class="filter-group">
                <label>Political Party</label>
                <select id="party-filter">
                    <option value="all">All Parties</option>
                </select>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <span class="stat-value" id="count-value">288</span>
                <span class="stat-label">Results</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">36</span>
                <span class="stat-label">Districts</span>
            </div>
        </div>
    </div>

    <div class="legend">
        <div class="legend-item">
            <span>Low Density</span>
            <div class="gradient-bar"></div>
            <span>High Density</span>
        </div>
    </div>

    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
    <script>
        const mapData = {data_json};
        
        // Get unique parties
        const parties = ["all", ...new Set(mapData.map(d => d.party))].sort();
        const partyFilter = document.getElementById('party-filter');
        parties.forEach(p => {{
            if (p === "all") return;
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            partyFilter.appendChild(opt);
        }});

        const map = L.map('map', {{
            zoomControl: false,
            attributionControl: false
        }}).setView([19.7515, 75.7139], 7);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            maxZoom: 19
        }}).addTo(map);

        L.control.zoom({{
            position: 'bottomleft'
        }}).addTo(map);

        const heat = L.heatLayer([], {{
            radius: 35,
            blur: 25,
            maxZoom: 10,
            gradient: {{0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}}
        }}).addTo(map);

        const markerGroup = L.layerGroup().addTo(map);

        function updateDisplay() {{
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            const selectedParty = document.getElementById('party-filter').value;
            
            const filteredData = mapData.filter(d => {{
                const matchesSearch = d.name.toLowerCase().includes(searchTerm) || 
                                    d.member.toLowerCase().includes(searchTerm);
                const matchesParty = selectedParty === 'all' || d.party === selectedParty;
                return matchesSearch && matchesParty;
            }});

            // Update stats
            document.getElementById('count-value').textContent = filteredData.length;

            // Update Heatmap
            heat.setLatLngs(filteredData.map(d => [d.lat, d.lng, 1.0]));

            // Update Markers
            markerGroup.clearLayers();
            filteredData.forEach(d => {{
                const marker = L.circleMarker([d.lat, d.lng], {{
                    radius: 4,
                    fillColor: '#7c3aed',
                    color: '#fff',
                    weight: 1,
                    opacity: 0.5,
                    fillOpacity: 0.8
                }});

                marker.bindPopup(`
                    <div class="custom-popup">
                        <b>${{d.name}}</b>
                        <span>District: ${{d.district}}</span><br>
                        <span>MLA: ${{d.member}}</span><br>
                        <span>Party: ${{d.party}}</span>
                    </div>
                `);
                
                markerGroup.addLayer(marker);
            }});

            // Zoom to results if appropriate (at least one result)
            if (filteredData.length > 0 && (searchTerm || selectedParty !== 'all')) {{
                const bounds = L.latLngBounds(filteredData.map(d => [d.lat, d.lng]));
                map.flyToBounds(bounds.pad(0.1), {{ duration: 0.8 }});
            }}
        }}

        document.getElementById('search-input').addEventListener('input', updateDisplay);
        document.getElementById('party-filter').addEventListener('change', updateDisplay);

        // Initial render
        updateDisplay();
    </script>
</body>
</html>
"""

final_html = html_template.format(data_json=json.dumps(data))
with open(html_path, 'w') as f:
    f.write(final_html)

print(f"Successfully generated {{html_path}} with {{len(data)}} records.")
