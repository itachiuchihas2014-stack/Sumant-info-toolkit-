import os
import requests
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "sumant_super_secret_osint_key"

# Users Database (Default 10 credits diye hain test karne ke liye)
users_db = {
    "Madarauchiha123": {"password": "123", "credits": 10, "history": []},
    "sumant": {"password": "123", "credits": 25, "history": []}
}

# 27 OSINT Tools List with Categories
TOOLS = [
    {"id": "number", "name": "Number Lookup", "icon": "📞", "cost": 2, "cat": "Phone", "api": "/api/number", "placeholder": "Enter 10-digit mobile number (e.g. 9876543210)"},
    {"id": "numleak", "name": "Number Leak (HiTeck+ICMR)", "icon": "🔍", "cost": 3, "cat": "Phone", "api": "/api/numleak", "placeholder": "Enter mobile number to check data breach"},
    {"id": "address", "name": "IP / Address Lookup", "icon": "📍", "cost": 2, "cat": "Address", "api": "/api/address", "placeholder": "Enter IP Address (e.g. 8.8.8.8 or 49.36.128.1)"},
    {"id": "pincode", "name": "Pincode Lookup", "icon": "📍", "cost": 1, "cat": "Address", "api": "/api/pincode", "placeholder": "Enter 6-digit India Pincode (e.g. 110001)"},
    {"id": "ifsc", "name": "IFSC Bank Lookup", "icon": "🏦", "cost": 1, "cat": "Banking", "api": "/api/ifsc", "placeholder": "Enter Bank IFSC Code (e.g. SBIN0000691)"},
    {"id": "upi", "name": "UPI ID Verification", "icon": "🏦", "cost": 2, "cat": "Banking", "api": "/api/upi", "placeholder": "Enter UPI ID (e.g. name@okaxis)"},
    {"id": "rc", "name": "Vehicle RC Details", "icon": "🚗", "cost": 3, "cat": "Vehicle", "api": "/api/rc", "placeholder": "Enter Vehicle Number (e.g. DL01AB1234)"},
    {"id": "challan", "name": "Vehicle Challan Check", "icon": "🚗", "cost": 2, "cat": "Vehicle", "api": "/api/challan", "placeholder": "Enter Vehicle Number"},
    {"id": "pan", "name": "PAN Card Verification", "icon": "🪪", "cost": 3, "cat": "Tax / PAN / GST", "api": "/api/pan", "placeholder": "Enter 10-digit PAN Number"},
    {"id": "gst", "name": "GSTIN Details Lookup", "icon": "🪪", "cost": 2, "cat": "Tax / PAN / GST", "api": "/api/gst", "placeholder": "Enter 15-digit GSTIN Number"},
    {"id": "aadhaar", "name": "Aadhaar Mask Check", "icon": "🆔", "cost": 3, "cat": "Identity", "api": "/api/aadhaar", "placeholder": "Enter 12-digit Aadhaar Number"},
    {"id": "username", "name": "Username OSINT (Socials)", "icon": "🆔", "cost": 2, "cat": "Identity", "api": "/api/username", "placeholder": "Enter Username (without @)"},
    {"id": "email", "name": "Email Breach Lookup", "icon": "🆔", "cost": 2, "cat": "Identity", "api": "/api/email", "placeholder": "Enter Email Address"},
    {"id": "truecaller", "name": "Deep Name Lookup", "icon": "📞", "cost": 3, "cat": "Phone", "api": "/api/deepname", "placeholder": "Enter Phone Number"},
    {"id": "sim", "name": "SIM Owner & Telecom Circle", "icon": "📞", "cost": 2, "cat": "Phone", "api": "/api/sim", "placeholder": "Enter Phone Number"},
    {"id": "whatsapp", "name": "WhatsApp Profile Status", "icon": "📞", "cost": 1, "cat": "Phone", "api": "/api/wa", "placeholder": "Enter Phone Number"},
    {"id": "fastag", "name": "FASTag Issuer Check", "icon": "🚗", "cost": 1, "cat": "Vehicle", "api": "/api/fastag", "placeholder": "Enter Vehicle Number"},
    {"id": "dl", "name": "Driving License Verify", "icon": "🚗", "cost": 2, "cat": "Vehicle", "api": "/api/dl", "placeholder": "Enter DL Number"},
    {"id": "bin", "name": "Card BIN Lookup", "icon": "🏦", "cost": 1, "cat": "Banking", "api": "/api/bin", "placeholder": "Enter first 6 digits of card (e.g. 457173)"},
    {"id": "crypto", "name": "Crypto Wallet Tracker", "icon": "🏦", "cost": 2, "cat": "Banking", "api": "/api/crypto", "placeholder": "Enter BTC/ETH/USDT Address"},
    {"id": "tan", "name": "TAN Verification", "icon": "🪪", "cost": 2, "cat": "Tax / PAN / GST", "api": "/api/tan", "placeholder": "Enter TAN Number"},
    {"id": "udyam", "name": "MSME Udyam Lookup", "icon": "🪪", "cost": 2, "cat": "Tax / PAN / GST", "api": "/api/udyam", "placeholder": "Enter Udyam Registration No"},
    {"id": "voter", "name": "Voter ID EPIC Lookup", "icon": "🆔", "cost": 2, "cat": "Identity", "api": "/api/voter", "placeholder": "Enter EPIC Voter ID Number"},
    {"id": "passport", "name": "Passport File Status", "icon": "🆔", "cost": 3, "cat": "Identity", "api": "/api/passport", "placeholder": "Enter File Number"},
    {"id": "domain", "name": "Domain WHOIS & DNS", "icon": "📍", "cost": 1, "cat": "Address", "api": "/api/domain", "placeholder": "Enter Domain (e.g. google.com)"},
    {"id": "mac", "name": "MAC Address Vendor", "icon": "📍", "cost": 1, "cat": "Address", "api": "/api/mac", "placeholder": "Enter MAC Address (e.g. 00:1A:2B:3C:4D:5E)"},
    {"id": "telegram", "name": "Telegram ID Resolver", "icon": "🆔", "cost": 2, "cat": "Identity", "api": "/api/tg", "placeholder": "Enter Telegram Username"}
]

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sumant OSINT Toolkit</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#141432] text-white font-sans min-h-screen flex items-center justify-center p-4">
    <div class="bg-[#1e1e3f] p-6 rounded-2xl border border-gray-700 w-full max-w-sm shadow-2xl">
        <h1 class="text-2xl font-extrabold text-[#00d8ff] text-center mb-2">🕵️ Sumant OSINT</h1>
        <p class="text-gray-400 text-xs text-center mb-6">Login to access 27 OSINT Tools</p>
        {% if error %}
        <div class="bg-red-500/20 border border-red-500 text-red-300 text-sm p-2.5 rounded-lg mb-4 text-center">{{ error }}</div>
        {% endif %}
        <form method="POST" class="space-y-4">
            <div>
                <label class="text-xs text-gray-300">Username</label>
                <input type="text" name="username" value="Madarauchiha123" required class="w-full mt-1 bg-[#141432] border border-gray-600 rounded-lg p-2.5 text-white focus:border-[#00d8ff] outline-none">
            </div>
            <div>
                <label class="text-xs text-gray-300">Password</label>
                <input type="password" name="password" value="123" required class="w-full mt-1 bg-[#141432] border border-gray-600 rounded-lg p-2.5 text-white focus:border-[#00d8ff] outline-none">
            </div>
            <button type="submit" class="w-full bg-[#00d8ff] text-black font-bold py-2.5 rounded-lg hover:bg-cyan-400 transition">🔐 Login</button>
        </form>
        <p class="text-gray-400 text-xs text-center mt-4">Demo Login pre-filled (Password: 123)</p>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sumant OSINT Toolkit</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#141432] text-white font-sans min-h-screen pb-12">
    <!-- Top Header -->
    <div class="bg-[#0b0b1e] p-4 border-b border-gray-800 sticky top-0 z-10">
        <div class="text-xl font-extrabold text-[#38bdf8] flex items-center gap-2">
            🕵️ Sumant OSINT Toolkit
        </div>
        <div class="flex flex-wrap gap-2.5 mt-3 items-center">
            <span id="credit-badge" class="bg-[#00d8ff] text-black font-extrabold px-3.5 py-1.5 rounded-lg text-sm shadow">
                💰 {{ credits }} Credits
            </span>
            <button onclick="buyCredits()" class="bg-[#1b1b38] hover:bg-[#25254d] border border-gray-700 px-3.5 py-1.5 rounded-lg text-sm">
                🛒 Buy (+10)
            </button>
            <button onclick="showHistory()" class="bg-[#1b1b38] hover:bg-[#25254d] border border-gray-700 px-3.5 py-1.5 rounded-lg text-sm">
                📜 History
            </button>
        </div>
        <div class="mt-3">
            <a href="/logout" class="text-gray-300 hover:text-white text-sm inline-flex items-center gap-1">
                🚪 Logout ({{ username }})
            </a>
        </div>
    </div>

    <!-- Center Hero -->
    <div class="p-4 text-center mt-3 max-w-lg mx-auto">
        <div class="flex items-center justify-center gap-2">
            <span class="text-3xl">👤</span>
            <h2 class="text-3xl font-extrabold text-[#00d8ff]">OSINT Toolkit</h2>
        </div>
        <p class="text-gray-300 text-sm mt-2 leading-relaxed">
            Welcome, <b>{{ username }}</b>! • {{ tools|length }} tools available •<br>
            Har tool ka alag credit cost hai
        </p>

        <!-- Category Filter Buttons (Exact Match to Screenshot) -->
        <div class="flex flex-wrap justify-center gap-2 mt-5">
            <button onclick="filterCategory('All')" class="cat-btn bg-white text-black font-semibold px-2.5 py-1 rounded text-sm flex items-center gap-1 shadow">🌐 All</button>
            <button onclick="filterCategory('Phone')" class="cat-btn bg-gray-200 text-black font-medium px-2.5 py-1 rounded text-sm flex items-center gap-1">📱 Phone</button>
            <button onclick="filterCategory('Address')" class="cat-btn bg-gray-200 text-black font-medium px-2.5 py-1 rounded text-sm flex items-center gap-1">📍 Address</button>
            <button onclick="filterCategory('Vehicle')" class="cat-btn bg-gray-200 text-black font-medium px-2.5 py-1 rounded text-sm flex items-center gap-1">🚗 Vehicle</button>
            <button onclick="filterCategory('Banking')" class="cat-btn bg-gray-200 text-black font-medium px-2.5 py-1 rounded text-sm flex items-center gap-1">🏦 Banking</button>
            <button onclick="filterCategory('Tax / PAN / GST')" class="cat-btn bg-gray-200 text-black font-medium px-2.5 py-1 rounded text-sm flex items-center gap-1">🪪 Tax / PAN / GST</button>
            <button onclick="filterCategory('Identity')" class="cat-btn bg-gray-200 text-black font-medium px-2.5 py-1 rounded text-sm flex items-center gap-1">🆔 Identity</button>
        </div>

        <!-- Tool Cards List -->
        <div id="tools-container" class="mt-6 space-y-3.5 text-left">
            {% for t in tools %}
            <div data-cat="{{ t.cat }}" onclick="openToolModal('{{ t.id }}', '{{ t.name }}', {{ t.cost }}, '{{ t.placeholder }}', '{{ t.api }}')" 
                 class="tool-card bg-[#21213e] hover:bg-[#29294d] p-4 rounded-xl border border-[#34345c] cursor-pointer active:scale-[0.98] transition shadow-md">
                <div class="font-bold text-lg text-white flex items-center gap-2">
                    <span>{{ t.icon }}</span> <span>{{ t.name }}</span>
                </div>
                <div class="text-[#38bdf8] text-sm mt-1 font-medium">💰 Cost: {{ t.cost }} credits</div>
                <div class="text-gray-400 text-xs mt-1 font-mono">{{ t.api }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Interactive Tool Modal -->
    <div id="tool-modal" class="fixed inset-0 bg-black/80 hidden items-center justify-center p-4 z-50">
        <div class="bg-[#1b1b38] border border-gray-600 rounded-2xl max-w-md w-full p-5 shadow-2xl">
            <div class="flex justify-between items-center border-b border-gray-700 pb-3">
                <h3 id="modal-title" class="text-lg font-bold text-[#00d8ff]">Tool Name</h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-white text-xl font-bold">&times;</button>
            </div>
            <div class="mt-4">
                <p id="modal-cost" class="text-xs text-yellow-400 mb-2 font-semibold"></p>
                <input id="modal-input" type="text" placeholder="Enter details..." 
                       class="w-full bg-[#111126] border border-gray-600 rounded-lg p-3 text-white text-sm focus:border-[#00d8ff] outline-none">
                <button id="search-btn" onclick="executeSearch()" 
                        class="w-full mt-3 bg-[#00d8ff] text-black font-extrabold py-2.5 rounded-lg hover:bg-cyan-400 transition">
                    🔍 Run OSINT Scan
                </button>
            </div>
            <!-- Output Box -->
            <div id="modal-result-box" class="mt-4 hidden">
                <div class="text-xs text-gray-400 mb-1">JSON Output / OSINT Result:</div>
                <pre id="modal-output" class="bg-[#0b0b19] text-green-400 p-3 rounded-lg text-xs overflow-x-auto border border-gray-700 max-h-60 whitespace-pre-wrap"></pre>
            </div>
        </div>
    </div>

    <script>
        let currentTool = {};

        function filterCategory(cat) {
            const cards = document.querySelectorAll('.tool-card');
            cards.forEach(card => {
                if (cat === 'All' || card.getAttribute('data-cat') === cat) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function openToolModal(id, name, cost, placeholder, api) {
            currentTool = { id, name, cost, api };
            document.getElementById('modal-title').innerText = name;
            document.getElementById('modal-cost').innerText = "💰 Cost: " + cost + " Credits | Endpoint: " + api;
            document.getElementById('modal-input').placeholder = placeholder;
            document.getElementById('modal-input').value = '';
            document.getElementById('modal-result-box').classList.add('hidden');
            document.getElementById('tool-modal').classList.remove('hidden');
            document.getElementById('tool-modal').classList.add('flex');
        }

        function closeModal() {
            document.getElementById('tool-modal').classList.add('hidden');
            document.getElementById('tool-modal').classList.remove('flex');
        }

        async function executeSearch() {
            const query = document.getElementById('modal-input').value.trim();
            if (!query) {
                alert("Bhai pehle number ya details toh daalo!");
                return;
            }
            const btn = document.getElementById('search-btn');
            btn.innerText = "⏳ Scanning Database...";
            btn.disabled = true;

            try {
                const res = await fetch('/api/run_tool', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: currentTool.id, name: currentTool.name, cost: currentTool.cost, query: query })
                });
                const data = await res.json();
                const outBox = document.getElementById('modal-result-box');
                const outPre = document.getElementById('modal-output');
                outBox.classList.remove('hidden');

                if (res.status !== 200) {
                    outPre.className = "bg-[#0b0b19] text-red-400 p-3 rounded-lg text-xs overflow-x-auto border border-red-700";
                    outPre.innerText = "❌ Error: " + data.error;
                } else {
                    document.getElementById('credit-badge').innerText = "💰 " + data.remaining_credits + " Credits";
                    outPre.className = "bg-[#0b0b19] text-green-400 p-3 rounded-lg text-xs overflow-x-auto border border-gray-700 max-h-60 whitespace-pre-wrap";
                    outPre.innerText = JSON.stringify(data.result, null, 2);
                }
            } catch (e) {
                alert("Network Error!");
            }
            btn.innerText = "🔍 Run OSINT Scan";
            btn.disabled = false;
        }

        async function buyCredits() {
            const res = await fetch('/api/buy', { method: 'POST' });
            const data = await res.json();
            document.getElementById('credit-badge').innerText = "💰 " + data.credits + " Credits";
            alert("✅ +10 Free Credits Added!");
        }

        async function showHistory() {
            const res = await fetch('/api/history');
            const data = await res.json();
            if (!data.history.length) {
                alert("📜 History abhi khali hai!");
            } else {
                alert("📜 Recent Searches:\\n\\n" + data.history.join("\\n"));
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    u = session['user']
    return render_template_string(DASHBOARD_HTML, username=u, credits=users_db[u]['credits'], tools=TOOLS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        if u in users_db and users_db[u]['password'] == p:
            session['user'] = u
            return redirect(url_for('index'))
        elif u and p:
            # Naya user auto-create kar do 10 credits ke sath
            users_db[u] = {"password": p, "credits": 10, "history": []}
            session['user'] = u
            return redirect(url_for('index'))
        else:
            error = "Invalid Username or Password!"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/buy', methods=['POST'])
def buy_credits():
    u = session.get('user')
    if not u:
        return jsonify({"error": "Unauthorized"}), 401
    users_db[u]['credits'] += 10
    return jsonify({"credits": users_db[u]['credits']})

@app.route('/api/history')
def get_history():
    u = session.get('user')
    if not u:
        return jsonify({"history": []})
    return jsonify({"history": users_db[u]['history'][-10:]})

@app.route('/api/run_tool', methods=['POST'])
def run_tool():
    u = session.get('user')
    if not u:
        return jsonify({"error": "Please login first"}), 401

    data = request.json
    tool_id = data.get('id')
    tool_name = data.get('name')
    cost = int(data.get('cost', 1))
    query = data.get('query', '').strip()

    if users_db[u]['credits'] < cost:
        return jsonify({"error": "Insufficient Credits! Upar '🛒 Buy (+10)' button daba kar credits add karo."}), 403

    # Deduct credits
    users_db[u]['credits'] -= cost
    users_db[u]['history'].append(f"{tool_name}: {query} (-{cost} cr)")

    # --- REAL LIVE OSINT API CALLS ---
    result_data = {}
    try:
        if tool_id == "pincode":
            r = requests.get(f"https://api.postalpincode.in/pincode/{query}", timeout=6).json()
            if r and r[0]['Status'] == 'Success':
                po = r[0]['PostOffice'][0]
                result_data = {
                    "Pincode": query,
                    "PostOffice": po['Name'],
                    "District": po['District'],
                    "State": po['State'],
                    "BranchType": po['BranchType'],
                    "DeliveryStatus": po['DeliveryStatus'],
                    "TotalBranchesFound": len(r[0]['PostOffice'])
                }
            else:
                result_data = {"status": "Not Found", "message": "Invalid Pincode"}

        elif tool_id == "ifsc":
            r = requests.get(f"https://ifsc.razorpay.com/{query.upper()}", timeout=6)
            if r.status_code == 200:
                result_data = r.json()
            else:
                result_data = {"status": "Not Found", "message": "Invalid IFSC Code"}

        elif tool_id in ["address", "domain"]:
            r = requests.get(f"http://ip-api.com/json/{query}", timeout=6).json()
            result_data = r

        elif tool_id == "bin":
            r = requests.get(f"https://lookup.binlist.net/{query[:6]}", timeout=6)
            if r.status_code == 200:
                result_data = r.json()
            else:
                result_data = {"BIN": query[:6], "Status": "Valid Format", "Note": "Rate limited by public BIN
