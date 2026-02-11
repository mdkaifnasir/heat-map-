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
    <title>Maharashtra MLA Analysis Dashboard 2024</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            backdrop-filter: blur(12px);
            padding: 24px;
            border-radius: 20px;
            border: 1px solid var(--glass-border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: right 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow-y: auto;
        }}

        .analysis-panel.open {{
            right: 20px;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        h1, h2 {{
            margin: 0 0 8px 0;
            font-weight: 600;
            background: linear-gradient(to right, #7c3aed, #db2777);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        h1 {{ font-size: 22px; }}
        h2 {{ font-size: 18px; margin-bottom: 12px; }}

        p {{
            margin: 0;
            font-size: 14px;
            color: #475569;
            line-height: 1.5;
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
        }}

        .stats, .analysis-section {{
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}

        .stat-card, .analysis-card {{
            background: rgba(0, 0, 0, 0.03);
            padding: 12px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid transparent;
            transition: all 0.2s;
        }}

        .stat-value, .analysis-value {{
            display: block;
            font-size: 20px;
            font-weight: 600;
            color: var(--accent-color);
        }}

        .stat-label, .analysis-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
        }}

        .toggle-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1002;
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 12px;
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
            transition: all 0.3s;
        }}

        .toggle-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(124, 58, 237, 0.4);
        }}

        .toggle-btn.active {{
            background: #db2777;
            box-shadow: 0 4px 12px rgba(219, 39, 119, 0.3);
        }}

        .chart-container {{
            position: relative;
            height: 200px;
            width: 100%;
        }}

        .analysis-full-width {{
            grid-column: span 2;
        }}

        .district-rank-item {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }}

        .district-rank-item:last-child {{ border: none; }}

        .leaflet-popup-content-wrapper {{
            background: var(--card-bg) !important;
            backdrop-filter: blur(12px) !important;
            color: var(--text-color) !important;
            border-radius: 12px !important;
            border: 1px solid var(--glass-border) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }}

        .legend {{
            position: absolute;
            bottom: 30px;
            left: 20px;
            z-index: 1000;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            padding: 15px;
            border-radius: 15px;
            border: 1px solid var(--glass-border);
            font-size: 12px;
        }}

        .legend-item {{ display: flex; align-items: center; margin-bottom: 5px; }}
        .gradient-bar {{ width: 100px; height: 10px; background: linear-gradient(to right, blue, cyan, lime, yellow, red); border-radius: 5px; margin: 0 10px; }}

        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(0, 0, 0, 0.1); border-radius: 10px; }}
    </style>
</head>
<body>
    <button class="toggle-btn" id="toggle-analysis">📊 Show Analysis</button>

    <div class="overlay" id="main-overlay">
        <h1>MLA Analysis Dashboard</h1>
        <p>Maharashtra Election 2024 Insight Explorer</p>
        
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
                <span class="stat-label">Seats</span>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="dist-count-value">36</span>
                <span class="stat-label">Districts</span>
            </div>
        </div>
    </div>

    <div class="analysis-panel" id="analysis-panel">
        <h2>Extreme Detailed Analysis</h2>
        
        <div class="analysis-section">
            <div class="analysis-card analysis-full-width">
                <span class="analysis-label">Party Distribution (Top 5)</span>
                <div class="chart-container">
                    <canvas id="partyChart"></canvas>
                </div>
            </div>
            
            <div class="analysis-card">
                <span class="analysis-value" id="dominating-party">-</span>
                <span class="analysis-label">Majority Party</span>
            </div>
            <div class="analysis-card">
                <span class="analysis-value" id="avg-seats-dist">-</span>
                <span class="analysis-label">Avg Seats/Dist</span>
            </div>

            <div class="analysis-card analysis-full-width">
                <span class="analysis-label">Top Performance by District</span>
                <div id="district-rankings" style="margin-top: 10px;">
                    <!-- Ranks will be injected here -->
                </div>
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
        let myChart = null;

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

        // Analysis Toggle
        const toggleBtn = document.getElementById('toggle-analysis');
        const panel = document.getElementById('analysis-panel');
        toggleBtn.addEventListener('click', () => {{
            panel.classList.toggle('open');
            toggleBtn.classList.toggle('active');
            toggleBtn.textContent = panel.classList.contains('open') ? '✖ Close Analysis' : '📊 Show Analysis';
        }});

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
            const uniqueDists = [...new Set(filteredData.map(d => d.district))].length;
            document.getElementById('dist-count-value').textContent = uniqueDists;

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

            // Perform Analysis
            updateAnalysis(filteredData);

            // Zoom to results if appropriate (at least one result)
            if (filteredData.length > 0 && (searchTerm || selectedParty !== 'all')) {{
                const bounds = L.latLngBounds(filteredData.map(d => [d.lat, d.lng]));
                map.flyToBounds(bounds.pad(0.1), {{ duration: 0.8 }});
            }}
        }}

        function updateAnalysis(data) {{
            if (data.length === 0) return;

            // Party Distribution
            const partyCount = {{}};
            data.forEach(d => partyCount[d.party] = (partyCount[d.party] || 0) + 1);
            
            const sortedParties = Object.entries(partyCount).sort((a,b) => b[1] - a[1]);
            document.getElementById('dominating-party').textContent = sortedParties[0][0];

            // Chart Update
            const labels = sortedParties.map(p => p[0]).slice(0, 5);
            const values = sortedParties.map(p => p[1]).slice(0, 5);
            
            updateChart(labels, values);

            // District Stats
            const distCount = {{}};
            data.forEach(d => distCount[d.district] = (distCount[d.district] || 0) + 1);
            const avg = (data.length / Object.keys(distCount).length).toFixed(1);
            document.getElementById('avg-seats-dist').textContent = avg;

            // District Rankings (Top 5)
            const rankedDists = Object.entries(distCount).sort((a,b) => b[1] - a[1]).slice(0,5);
            const rankList = document.getElementById('district-rankings');
            rankList.innerHTML = rankedDists.map(d => `
                <div class="district-rank-item">
                    <span>${{d[0]}}</span>
                    <b style="color:#7c3aed">${{d[1]}} Seats</b>
                </div>
            `).join('');
        }}

        function updateChart(labels, data) {{
            const ctx = document.getElementById('partyChart').getContext('2d');
            if (myChart) myChart.destroy();
            
            myChart = new Chart(ctx, {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: data,
                        backgroundColor: ['#7c3aed', '#db2777', '#f59e0b', '#10b981', '#3b82f6'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    cutout: '70%'
                }}
            }});
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
