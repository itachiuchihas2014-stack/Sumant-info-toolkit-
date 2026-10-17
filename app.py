import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Temporary user database (3 credits ke sath)
user_data = {"username": "itachiuchiha", "credits": 3}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sumant OSINT Toolkit</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#141432] text-white font-sans min-h-screen pb-10">
    <!-- Top Navbar -->
    <div class="bg-[#0d0d26] p-4 border-b border-gray-800">
        <h1 class="text-xl font-bold text-[#38bdf8] flex items-center gap-2">🕵️ Sumant OSINT Toolkit</h1>
        <div class="flex gap-3 mt-3 items-center">
            <span id="credit-badge" class="bg-[#00d8ff] text-black font-bold px-3 py-1.5 rounded-lg text-sm">💰 {{ credits }} Credits</span>
            <button class="bg-[#1e1e38] px-3 py-1.5 rounded-lg text-sm">🛒 Buy</button>
            <button class="bg-[#1e1e38] px-3 py-1.5 rounded-lg text-sm">📜 History</button>
        </div>
        <div class="mt-3 text-gray-400 text-sm">🚪 Logout ({{ username }})</div>
    </div>

    <!-- Main Section -->
    <div class="p-4 text-center mt-4">
        <h2 class="text-3xl font-extrabold text-[#00d8ff]">👤 OSINT Toolkit</h2>
        <p class="text-gray-400 text-sm mt-2">Welcome, <b>{{ username }}</b>! • Har tool ka alag credit cost hai</p>

        <!-- Tool Cards -->
        <div class="mt-6 space-y-4 text-left max-w-md mx-auto">
            <div onclick="useTool('Number Lookup', 2)" class="bg-[#232342] p-4 rounded-xl border border-gray-700 cursor-pointer active:scale-95 transition">
                <div class="font-bold text-lg">📞 Number Lookup</div>
                <div class="text-[#38bdf8] text-sm mt-1">💰 Cost: 2 credits</div>
                <div class="text-gray-500 text-xs mt-1">/api/number</div>
            </div>

            <div onclick="useTool('Number Leak (HiTeck+ICMR)', 3)" class="bg-[#232342] p-4 rounded-xl border border-gray-700 cursor-pointer active:scale-95 transition">
                <div class="font-bold text-lg">🔍 Number Leak (HiTeck+ICMR)</div>
                <div class="text-[#38bdf8] text-sm mt-1">💰 Cost: 3 credits</div>
                <div class="text-gray-500 text-xs mt-1">/api/numleak</div>
            </div>

            <div onclick="useTool('Address Lookup', 2)" class="bg-[#232342] p-4 rounded-xl border border-gray-700 cursor-pointer active:scale-95 transition">
                <div class="font-bold text-lg">📍 Address Lookup</div>
                <div class="text-[#38bdf8] text-sm mt-1">💰 Cost: 2 credits</div>
                <div class="text-gray-500 text-xs mt-1">/api/address</div>
            </div>

            <div onclick="useTool('Pincode', 1)" class="bg-[#232342] p-4 rounded-xl border border-gray-700 cursor-pointer active:scale-95 transition">
                <div class="font-bold text-lg">📍 Pincode</div>
                <div class="text-[#38bdf8] text-sm mt-1">💰 Cost: 1 credits</div>
                <div class="text-gray-500 text-xs mt-1">/api/pincode</div>
            </div>
        </div>
    </div>

    <script>
        async function useTool(toolName, cost) {
            const target = prompt(toolName + " ke liye details enter karo:");
            if (!target) return;

            const res = await fetch('/api/use', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tool: toolName, cost: cost, target: target})
            });
            const data = await res.json();
            
            if (res.status !== 200) {
                alert("❌ " + data.error);
            } else {
                document.getElementById('credit-badge').innerText = "💰 " + data.remaining + " Credits";
                alert("✅ Result for " + target + ":\\n" + data.result);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, username=user_data["username"], credits=user_data["credits"])

@app.route('/api/use', methods=['POST'])
def use_tool():
    data = request.json
    cost = data.get('cost', 1)
    target = data.get('target', '')
    tool = data.get('tool', '')

    if user_data["credits"] < cost:
        return jsonify({"error": "Credits khatam ho gaye! Recharge karo."}), 403

    user_data["credits"] -= cost
    return jsonify({
        "remaining": user_data["credits"],
        "result": f"{tool} data found for {target} (Demo Mode)"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
