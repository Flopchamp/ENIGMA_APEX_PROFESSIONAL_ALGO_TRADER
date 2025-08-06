// Enigma-Apex Power Score Indicator for NinjaTrader 8
// Displays real-time Enigma power scores and signals on charts
// Version: 1.0.0

#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.DrawingTools;
using NinjaTrader.NinjaScript.Indicators;
using System.Net.WebSockets;
using System.Threading;
using Newtonsoft.Json;
#endregion

namespace NinjaTrader.NinjaScript.Indicators
{
    public class EnigmaApexPowerScore : Indicator
    {
        #region Variables
        private ClientWebSocket webSocket;
        private CancellationTokenSource cancellationToken;
        private double currentPowerScore = 0;
        private string currentSignalColor = "neutral";
        private string macvuState = "NEUTRAL";
        private int confluenceLevel = 0;
        private DateTime lastUpdateTime = DateTime.MinValue;
        private bool isConnected = false;

        // Visual elements
        private System.Windows.Controls.TextBlock powerScoreText;
        private System.Windows.Controls.TextBlock signalText;
        private System.Windows.Controls.Border indicatorPanel;
        #endregion

        #region Properties
        [NinjaScriptProperty]
        [Range(1, int.MaxValue)]
        [Display(Name = "WebSocket Port", Description = "Port for Enigma-Apex WebSocket connection", Order = 1, GroupName = "Connection")]
        public int WebSocketPort { get; set; } = 8765;

        [NinjaScriptProperty]
        [Display(Name = "Server Address", Description = "Enigma-Apex server address", Order = 2, GroupName = "Connection")]
        public string ServerAddress { get; set; } = "localhost";

        [NinjaScriptProperty]
        [Display(Name = "Show Power Score", Description = "Display power score on chart", Order = 3, GroupName = "Display")]
        public bool ShowPowerScore { get; set; } = true;

        [NinjaScriptProperty]
        [Display(Name = "Show Signal Arrows", Description = "Draw signal arrows on chart", Order = 4, GroupName = "Display")]
        public bool ShowSignalArrows { get; set; } = true;

        [NinjaScriptProperty]
        [Display(Name = "Power Score Threshold", Description = "Minimum power score to show signals", Order = 5, GroupName = "Filters")]
        public double PowerScoreThreshold { get; set; } = 60.0;

        [NinjaScriptProperty]
        [Display(Name = "Audio Alerts", Description = "Play sound on new signals", Order = 6, GroupName = "Alerts")]
        public bool AudioAlerts { get; set; } = true;

        // Color properties
        [XmlIgnore]
        [Display(Name = "Bullish Signal Color", Description = "Color for bullish signals", Order = 7, GroupName = "Colors")]
        public Brush BullishColor { get; set; } = Brushes.LimeGreen;

        [XmlIgnore]
        [Display(Name = "Bearish Signal Color", Description = "Color for bearish signals", Order = 8, GroupName = "Colors")]
        public Brush BearishColor { get; set; } = Brushes.Red;

        [XmlIgnore]
        [Display(Name = "Neutral Color", Description = "Color for neutral signals", Order = 9, GroupName = "Colors")]
        public Brush NeutralColor { get; set; } = Brushes.Gray;
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"Enigma-Apex Power Score Indicator - Real-time signal display from Enigma-Apex system";
                Name = "EnigmaApexPowerScore";
                Calculate = Calculate.OnEachTick;
                IsOverlay = true;
                DisplayInDataBox = true;
                DrawOnPricePanel = true;
                DrawHorizontalGridLines = true;
                DrawVerticalGridLines = true;
                PaintPriceMarkers = true;
                ScaleJustification = NinjaTrader.Gui.Chart.ScaleJustification.Right;
                IsSuspendedWhileInactive = false;

                // Initialize default values
                WebSocketPort = 8765;
                ServerAddress = "localhost";
                ShowPowerScore = true;
                ShowSignalArrows = true;
                PowerScoreThreshold = 60.0;
                AudioAlerts = true;
            }
            else if (State == State.DataLoaded)
            {
                // Initialize WebSocket connection
                InitializeWebSocketConnection();
            }
            else if (State == State.Terminated)
            {
                // Clean up WebSocket connection
                CleanupWebSocketConnection();
            }
        }

        #region WebSocket Connection
        private async void InitializeWebSocketConnection()
        {
            try
            {
                webSocket = new ClientWebSocket();
                cancellationToken = new CancellationTokenSource();

                string uri = $"ws://{ServerAddress}:{WebSocketPort}/ninja";

                await webSocket.ConnectAsync(new Uri(uri), cancellationToken.Token);
                isConnected = true;

                // Send identification message
                var identificationMessage = new
                {
                    type = "client_identification",
                    data = new
                    {
                        client_type = "ninja_indicator",
                        version = "1.0.0",
                        instrument = Instrument.MasterInstrument.Name
                    }
                };

                string jsonMessage = JsonConvert.SerializeObject(identificationMessage);
                byte[] messageBytes = Encoding.UTF8.GetBytes(jsonMessage);

                await webSocket.SendAsync(new ArraySegment<byte>(messageBytes),
                    WebSocketMessageType.Text, true, cancellationToken.Token);

                // Start listening for messages
                _ = Task.Run(ListenForMessages);

                Print($"✅ Connected to Enigma-Apex at {uri}");
            }
            catch (Exception ex)
            {
                Print($"❌ WebSocket connection failed: {ex.Message}");
                isConnected = false;
            }
        }

        private async Task ListenForMessages()
        {
            byte[] buffer = new byte[4096];

            try
            {
                while (webSocket.State == WebSocketState.Open && !cancellationToken.Token.IsCancellationRequested)
                {
                    var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken.Token);

                    if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        ProcessEnigmaMessage(message);
                    }
                }
            }
            catch (Exception ex)
            {
                Print($"❌ WebSocket listening error: {ex.Message}");
                isConnected = false;
            }
        }

        private void ProcessEnigmaMessage(string message)
        {
            try
            {
                dynamic data = JsonConvert.DeserializeObject(message);

                if (data?.type == "enigma_update" && data?.data?.enigma_data != null)
                {
                    var enigmaData = data.data.enigma_data;

                    // Update indicator values
                    currentPowerScore = enigmaData.power_score ?? 0;
                    currentSignalColor = enigmaData.signal_color ?? "neutral";
                    macvuState = enigmaData.macvu_state ?? "NEUTRAL";
                    confluenceLevel = enigmaData.confluence_level ?? 0;
                    lastUpdateTime = DateTime.Now;

                    // Trigger UI update on main thread
                    Application.Current?.Dispatcher.BeginInvoke(new Action(() =>
                    {
                        UpdateIndicatorDisplay();
                        DrawSignalOnChart();
                    }));
                }
            }
            catch (Exception ex)
            {
                Print($"❌ Error processing Enigma message: {ex.Message}");
            }
        }

        private void CleanupWebSocketConnection()
        {
            try
            {
                cancellationToken?.Cancel();
                webSocket?.CloseAsync(WebSocketCloseStatus.NormalClosure, "Indicator closing", CancellationToken.None);
                webSocket?.Dispose();
                cancellationToken?.Dispose();
            }
            catch (Exception ex)
            {
                Print($"❌ WebSocket cleanup error: {ex.Message}");
            }
        }
        #endregion

        #region Chart Drawing
        private void DrawSignalOnChart()
        {
            if (!ShowSignalArrows || currentPowerScore < PowerScoreThreshold)
                return;

            // Determine signal direction and color
            Brush signalBrush = NeutralColor;
            string arrowDirection = "neutral";

            if (currentSignalColor == "green" && macvuState == "BULLISH")
            {
                signalBrush = BullishColor;
                arrowDirection = "up";
            }
            else if (currentSignalColor == "red" && macvuState == "BEARISH")
            {
                signalBrush = BearishColor;
                arrowDirection = "down";
            }

            // Draw arrow at current bar
            if (arrowDirection != "neutral")
            {
                string signalText = $"Enigma {currentPowerScore:F0}%";

                if (arrowDirection == "up")
                {
                    Draw.ArrowUp(this, $"EnigmaSignal_{CurrentBar}", true, 0,
                        Low[0] - (2 * TickSize), signalBrush);

                    Draw.TextFixed(this, $"EnigmaText_{CurrentBar}",
                        $"🚀 BULLISH SIGNAL\nPower: {currentPowerScore:F0}%\nConfluence: {confluenceLevel}",
                        TextPosition.TopLeft, Brushes.White, new SimpleFont("Arial", 12),
                        signalBrush, Brushes.Transparent, 0);
                }
                else if (arrowDirection == "down")
                {
                    Draw.ArrowDown(this, $"EnigmaSignal_{CurrentBar}", true, 0,
                        High[0] + (2 * TickSize), signalBrush);

                    Draw.TextFixed(this, $"EnigmaText_{CurrentBar}",
                        $"🔻 BEARISH SIGNAL\nPower: {currentPowerScore:F0}%\nConfluence: {confluenceLevel}",
                        TextPosition.TopLeft, Brushes.White, new SimpleFont("Arial", 12),
                        signalBrush, Brushes.Transparent, 0);
                }

                // Play audio alert
                if (AudioAlerts)
                {
                    PlaySound(@"C:\Program Files\NinjaTrader 8\sounds\Alert1.wav");
                }

                Print($"🎯 Enigma Signal: {arrowDirection.ToUpper()} | Power: {currentPowerScore:F0}% | Confluence: {confluenceLevel}");
            }
        }

        private void UpdateIndicatorDisplay()
        {
            if (!ShowPowerScore)
                return;

            // Update power score display
            string displayText = $"Enigma Power: {currentPowerScore:F0}%";

            if (isConnected)
            {
                displayText += $" | {macvuState} | C{confluenceLevel}";
            }
            else
            {
                displayText += " | DISCONNECTED";
            }

            // Draw text on chart
            Brush textColor = NeutralColor;
            if (currentSignalColor == "green") textColor = BullishColor;
            else if (currentSignalColor == "red") textColor = BearishColor;

            Draw.TextFixed(this, "EnigmaPowerScore", displayText,
                TextPosition.TopRight, textColor, new SimpleFont("Arial", 10),
                Brushes.Transparent, Brushes.Transparent, 0);
        }
        #endregion

        protected override void OnBarUpdate()
        {
            // Update display on each bar
            if (ShowPowerScore && IsFirstTickOfBar)
            {
                UpdateIndicatorDisplay();
            }

            // Connection status check
            if (CurrentBar % 100 == 0) // Check every 100 bars
            {
                if (!isConnected && webSocket?.State != WebSocketState.Open)
                {
                    Print("⚠️ Enigma-Apex connection lost. Attempting reconnection...");
                    _ = Task.Run(async () => await Task.Delay(5000).ContinueWith(t => InitializeWebSocketConnection()));
                }
            }
        }

        protected override void OnMarketData(MarketDataEventArgs marketDataUpdate)
        {
            // Real-time updates for active trading
            if (marketDataUpdate.MarketDataType == MarketDataType.Last)
            {
                // Trigger display update if we have recent signal data
                if ((DateTime.Now - lastUpdateTime).TotalSeconds < 30)
                {
                    UpdateIndicatorDisplay();
                }
            }
        }

        #region Custom Methods
        public double GetCurrentPowerScore()
        {
            return currentPowerScore;
        }

        public string GetCurrentSignalColor()
        {
            return currentSignalColor;
        }

        public bool IsEnigmaConnected()
        {
            return isConnected && webSocket?.State == WebSocketState.Open;
        }

        public string GetConnectionStatus()
        {
            if (!isConnected) return "DISCONNECTED";
            if (webSocket?.State == WebSocketState.Open) return "CONNECTED";
            return "CONNECTING";
        }
        #endregion
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
    public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
    {
        private EnigmaApexPowerScore[] cacheEnigmaApexPowerScore;
        public EnigmaApexPowerScore EnigmaApexPowerScore(int webSocketPort, string serverAddress, bool showPowerScore, bool showSignalArrows, double powerScoreThreshold, bool audioAlerts)
        {
            return EnigmaApexPowerScore(Input, webSocketPort, serverAddress, showPowerScore, showSignalArrows, powerScoreThreshold, audioAlerts);
        }

        public EnigmaApexPowerScore EnigmaApexPowerScore(ISeries<double> input, int webSocketPort, string serverAddress, bool showPowerScore, bool showSignalArrows, double powerScoreThreshold, bool audioAlerts)
        {
            if (cacheEnigmaApexPowerScore != null)
                for (int idx = 0; idx < cacheEnigmaApexPowerScore.Length; idx++)
                    if (cacheEnigmaApexPowerScore[idx] != null && cacheEnigmaApexPowerScore[idx].WebSocketPort == webSocketPort && cacheEnigmaApexPowerScore[idx].ServerAddress == serverAddress && cacheEnigmaApexPowerScore[idx].ShowPowerScore == showPowerScore && cacheEnigmaApexPowerScore[idx].ShowSignalArrows == showSignalArrows && cacheEnigmaApexPowerScore[idx].PowerScoreThreshold == powerScoreThreshold && cacheEnigmaApexPowerScore[idx].AudioAlerts == audioAlerts && cacheEnigmaApexPowerScore[idx].EqualsInput(input))
                        return cacheEnigmaApexPowerScore[idx];
            return CacheIndicator<EnigmaApexPowerScore>(new EnigmaApexPowerScore() { WebSocketPort = webSocketPort, ServerAddress = serverAddress, ShowPowerScore = showPowerScore, ShowSignalArrows = showSignalArrows, PowerScoreThreshold = powerScoreThreshold, AudioAlerts = audioAlerts }, input, ref cacheEnigmaApexPowerScore);
        }
    }
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
    public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
    {
        public Indicators.EnigmaApexPowerScore EnigmaApexPowerScore(int webSocketPort, string serverAddress, bool showPowerScore, bool showSignalArrows, double powerScoreThreshold, bool audioAlerts)
        {
            return indicator.EnigmaApexPowerScore(Input, webSocketPort, serverAddress, showPowerScore, showSignalArrows, powerScoreThreshold, audioAlerts);
        }

        public Indicators.EnigmaApexPowerScore EnigmaApexPowerScore(ISeries<double> input, int webSocketPort, string serverAddress, bool showPowerScore, bool showSignalArrows, double powerScoreThreshold, bool audioAlerts)
        {
            return indicator.EnigmaApexPowerScore(input, webSocketPort, serverAddress, showPowerScore, showSignalArrows, powerScoreThreshold, audioAlerts);
        }
    }
}

namespace NinjaTrader.NinjaScript.Strategies
{
    public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
    {
        public Indicators.EnigmaApexPowerScore EnigmaApexPowerScore(int webSocketPort, string serverAddress, bool showPowerScore, bool showSignalArrows, double powerScoreThreshold, bool audioAlerts)
        {
            return indicator.EnigmaApexPowerScore(Input, webSocketPort, serverAddress, showPowerScore, showSignalArrows, powerScoreThreshold, audioAlerts);
        }

        public Indicators.EnigmaApexPowerScore EnigmaApexPowerScore(ISeries<double> input, int webSocketPort, string serverAddress, bool showPowerScore, bool showSignalArrows, double powerScoreThreshold, bool audioAlerts)
        {
            return indicator.EnigmaApexPowerScore(input, webSocketPort, serverAddress, showPowerScore, showSignalArrows, powerScoreThreshold, audioAlerts);
        }
    }
}

#endregion
