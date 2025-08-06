"""
🚀 MANUAL SIGNAL INPUT INTERFACE
Web-based signal entry system for Enigma-Apex Trading Platform
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import asyncio
import websockets
import json
import sqlite3
from datetime import datetime
import threading
import webbrowser
from typing import Dict, Any
import os

app = Flask(__name__, template_folder='../templates')

class SignalInputManager:
    def __init__(self):
        self.websocket_url = "ws://localhost:8765"
        self.db_path = "trading_database.db"
        self.signals_sent = 0
        
    async def send_signal_to_server(self, signal_data: Dict[str, Any]) -> bool:
        """Send signal to WebSocket server"""
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                message = {
                    'type': 'manual_signal',
                    'source': 'web_interface',
                    'data': signal_data,
                    'timestamp': datetime.now().isoformat()
                }
                await websocket.send(json.dumps(message))
                print(f"✅ Signal sent to server: {signal_data['signal_type']} at {signal_data['power_score']}%")
                return True
        except Exception as e:
            print(f"❌ Failed to send signal: {e}")
            return False
    
    def log_signal_to_database(self, signal_data: Dict[str, Any]) -> None:
        """Log signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO signals (
                    signal_type, power_score, confidence_level, timeframe, 
                    symbol, entry_price, stop_loss, take_profit, source, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_data['signal_type'],
                signal_data['power_score'],
                signal_data.get('confidence', 'C2'),
                signal_data.get('timeframe', 'M15'),
                signal_data.get('symbol', 'ES'),
                signal_data.get('entry_price', 0),
                signal_data.get('stop_loss', 0),
                signal_data.get('take_profit', 0),
                'manual_web_input',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            print(f"✅ Signal logged to database")
        except Exception as e:
            print(f"❌ Database logging failed: {e}")

signal_manager = SignalInputManager()

@app.route('/')
def index():
    """Main signal input interface"""
    return render_template('signal_input.html')

@app.route('/submit_signal', methods=['POST'])
def submit_signal():
    """Handle signal submission"""
    try:
        # Get form data
        signal_data = {
            'signal_type': request.form.get('signal_type', 'bullish').lower(),
            'power_score': int(request.form.get('power_score', 75)),
            'confidence': request.form.get('confidence', 'C2'),
            'timeframe': request.form.get('timeframe', 'M15'),
            'symbol': request.form.get('symbol', 'ES').upper(),
            'entry_price': float(request.form.get('entry_price', 0)),
            'stop_loss': float(request.form.get('stop_loss', 0)),
            'take_profit': float(request.form.get('take_profit', 0)),
            'notes': request.form.get('notes', '')
        }
        
        # Validate data
        if not (0 <= signal_data['power_score'] <= 100):
            return jsonify({'error': 'Power score must be between 0-100'}), 400
        
        if signal_data['signal_type'] not in ['bullish', 'bearish']:
            return jsonify({'error': 'Signal type must be bullish or bearish'}), 400
        
        # Send to WebSocket server asynchronously
        def send_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(signal_manager.send_signal_to_server(signal_data))
            loop.close()
            if success:
                signal_manager.log_signal_to_database(signal_data)
                signal_manager.signals_sent += 1
        
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=send_async)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Signal sent successfully! {signal_data["signal_type"].upper()} at {signal_data["power_score"]}%',
            'signal_data': signal_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to process signal: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        # Test WebSocket connection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def test_connection():
            try:
                async with websockets.connect("ws://localhost:8765") as websocket:
                    return True
            except:
                return False
        
        websocket_status = loop.run_until_complete(test_connection())
        loop.close()
        
        return jsonify({
            'websocket_server': 'connected' if websocket_status else 'disconnected',
            'signals_sent': signal_manager.signals_sent,
            'database': 'operational',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Trading dashboard with recent signals"""
    try:
        conn = sqlite3.connect(signal_manager.db_path)
        cursor = conn.cursor()
        
        # Get recent signals
        cursor.execute('''
            SELECT signal_type, power_score, confidence_level, timeframe, 
                   symbol, timestamp 
            FROM signals 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        
        recent_signals = cursor.fetchall()
        conn.close()
        
        return render_template('dashboard.html', signals=recent_signals)
    except Exception as e:
        return render_template('dashboard.html', signals=[], error=str(e))

def create_templates():
    """Create HTML templates for the web interface"""
    import os
    
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    # Signal input template
    signal_input_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enigma-Apex Signal Input</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #2a2a2a; padding: 30px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #00ff88; margin: 0; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #ccc; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #555; background: #3a3a3a; color: #fff; border-radius: 5px; box-sizing: border-box; }
        .form-row { display: flex; gap: 20px; }
        .form-row .form-group { flex: 1; }
        .signal-type { display: flex; gap: 10px; }
        .signal-type input[type="radio"] { width: auto; margin-right: 5px; }
        .signal-type label { display: inline; margin-bottom: 0; }
        .submit-btn { background: #00ff88; color: #000; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%; }
        .submit-btn:hover { background: #00cc6a; }
        .status { margin-top: 20px; padding: 10px; border-radius: 5px; text-align: center; }
        .success { background: #00ff8844; border: 1px solid #00ff88; }
        .error { background: #ff004444; border: 1px solid #ff0044; }
        .power-score { font-size: 24px; text-align: center; color: #00ff88; }
        .dashboard-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #4a4a4a; color: #fff; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Guardian Enigma-Apex Signal Input</h1>
            <p>Manual Trading Signal Entry Interface</p>
            <a href="/dashboard" class="dashboard-link">📊 View Dashboard</a>
        </div>
        
        <form id="signalForm">
            <div class="form-group">
                <label>Signal Type:</label>
                <div class="signal-type">
                    <label><input type="radio" name="signal_type" value="bullish" checked> 🟢 BULLISH</label>
                    <label><input type="radio" name="signal_type" value="bearish"> 🔴 BEARISH</label>
                </div>
            </div>
            
            <div class="form-group">
                <label for="power_score">Power Score (0-100):</label>
                <input type="range" id="power_score" name="power_score" min="0" max="100" value="75" oninput="updatePowerScore(this.value)">
                <div id="power_display" class="power-score">75%</div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="confidence">Confidence Level:</label>
                    <select id="confidence" name="confidence">
                        <option value="C1">C1 - Low Confidence</option>
                        <option value="C2" selected>C2 - Medium Confidence</option>
                        <option value="C3">C3 - High Confidence</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="timeframe">Timeframe:</label>
                    <select id="timeframe" name="timeframe">
                        <option value="M5">5 Minutes</option>
                        <option value="M15" selected>15 Minutes</option>
                        <option value="M30">30 Minutes</option>
                        <option value="H1">1 Hour</option>
                        <option value="H4">4 Hours</option>
                        <option value="D1">Daily</option>
                    </select>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="symbol">Symbol:</label>
                    <input type="text" id="symbol" name="symbol" value="ES" placeholder="ES, NQ, EUR/USD">
                </div>
                
                <div class="form-group">
                    <label for="entry_price">Entry Price:</label>
                    <input type="number" id="entry_price" name="entry_price" step="0.01" placeholder="0.00">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="stop_loss">Stop Loss:</label>
                    <input type="number" id="stop_loss" name="stop_loss" step="0.01" placeholder="0.00">
                </div>
                
                <div class="form-group">
                    <label for="take_profit">Take Profit:</label>
                    <input type="number" id="take_profit" name="take_profit" step="0.01" placeholder="0.00">
                </div>
            </div>
            
            <div class="form-group">
                <label for="notes">Notes (Optional):</label>
                <textarea id="notes" name="notes" rows="3" placeholder="Additional signal notes..."></textarea>
            </div>
            
            <button type="submit" class="submit-btn">📤 Send Signal to NinjaTrader</button>
        </form>
        
        <div id="status"></div>
    </div>
    
    <script>
        function updatePowerScore(value) {
            document.getElementById('power_display').textContent = value + '%';
        }
        
        document.getElementById('signalForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const statusDiv = document.getElementById('status');
            
            try {
                const response = await fetch('/submit_signal', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    statusDiv.innerHTML = '<div class="status success">✅ ' + result.message + '</div>';
                    // Reset form
                    this.reset();
                    document.getElementById('power_score').value = 75;
                    updatePowerScore(75);
                } else {
                    statusDiv.innerHTML = '<div class="status error">❌ ' + result.error + '</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div class="status error">❌ Connection error: ' + error.message + '</div>';
            }
        });
    </script>
</body>
</html>
    '''
    
    # Dashboard template
    dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enigma-Apex Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #00ff88; margin: 0; }
        .back-link { display: inline-block; margin-bottom: 20px; padding: 10px 20px; background: #4a4a4a; color: #fff; text-decoration: none; border-radius: 5px; }
        .signals-table { width: 100%; border-collapse: collapse; background: #2a2a2a; border-radius: 10px; overflow: hidden; }
        .signals-table th, .signals-table td { padding: 15px; text-align: left; border-bottom: 1px solid #444; }
        .signals-table th { background: #333; color: #00ff88; }
        .bullish { color: #00ff88; }
        .bearish { color: #ff4444; }
        .no-signals { text-align: center; padding: 50px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Enigma-Apex Dashboard</h1>
            <p>Recent Trading Signals</p>
        </div>
        
        <a href="/" class="back-link">← Back to Signal Input</a>
        
        {% if signals %}
        <table class="signals-table">
            <thead>
                <tr>
                    <th>Signal Type</th>
                    <th>Power Score</th>
                    <th>Confidence</th>
                    <th>Timeframe</th>
                    <th>Symbol</th>
                    <th>Timestamp</th>
                </tr>
            </thead>
            <tbody>
                {% for signal in signals %}
                <tr>
                    <td class="{{ signal[0] }}">
                        {{ '🟢 BULLISH' if signal[0] == 'bullish' else '🔴 BEARISH' }}
                    </td>
                    <td>{{ signal[1] }}%</td>
                    <td>{{ signal[2] }}</td>
                    <td>{{ signal[3] }}</td>
                    <td>{{ signal[4] }}</td>
                    <td>{{ signal[5] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="no-signals">
            <h3>No signals found</h3>
            <p>Start by submitting your first signal!</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
    '''
    
    # Write templates
    with open('templates/signal_input.html', 'w', encoding='utf-8') as f:
        f.write(signal_input_html)
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("✅ HTML templates created successfully")

def main():
    """Main function to run the web interface"""
    print("🚀 Starting Enigma-Apex Manual Signal Input Interface...")
    
    # Create templates
    create_templates()
    
    # Start the Flask app
    print("✅ Web interface starting on http://localhost:5000")
    print("📊 Dashboard available at http://localhost:5000/dashboard")
    print("🔗 Make sure WebSocket server is running on localhost:8765")
    
    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open('http://localhost:5000')).start()
    
    # Run Flask app
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
