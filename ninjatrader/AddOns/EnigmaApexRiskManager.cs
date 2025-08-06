// Enigma-Apex Risk Management Indicator for NinjaTrader 8
// Real-time risk monitoring and position sizing recommendations
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
    public class EnigmaApexRiskManager : Indicator
    {
        #region Variables
        private ClientWebSocket webSocket;
        private CancellationTokenSource cancellationToken;

        // Risk metrics
        private double accountBalance = 10000;
        private double dailyPnL = 0;
        private double weeklyPnL = 0;
        private double currentDrawdown = 0;
        private double riskScore = 50;
        private double kellyPercentage = 0.02;
        private double recommendedPositionSize = 0;

        // Risk limits
        private double maxDailyLoss = 1000;
        private double maxWeeklyLoss = 3000;
        private double maxDrawdown = 8.0;
        private double maxPositionRisk = 2.0;

        // Status tracking
        private bool isConnected = false;
        private DateTime lastRiskUpdate = DateTime.MinValue;
        private string riskStatus = "SAFE";
        private List<string> activeWarnings = new List<string>();
        #endregion

        #region Properties
        [NinjaScriptProperty]
        [Range(1, int.MaxValue)]
        [Display(Name = "WebSocket Port", Description = "Port for Enigma-Apex Risk Manager", Order = 1, GroupName = "Connection")]
        public int WebSocketPort { get; set; } = 8765;

        [NinjaScriptProperty]
        [Display(Name = "Server Address", Description = "Risk Manager server address", Order = 2, GroupName = "Connection")]
        public string ServerAddress { get; set; } = "localhost";

        [NinjaScriptProperty]
        [Range(100, 1000000)]
        [Display(Name = "Account Balance", Description = "Current account balance", Order = 3, GroupName = "Risk Settings")]
        public double AccountBalance { get; set; } = 10000;

        [NinjaScriptProperty]
        [Range(50, 5000)]
        [Display(Name = "Max Daily Loss", Description = "Maximum daily loss limit", Order = 4, GroupName = "Risk Settings")]
        public double MaxDailyLoss { get; set; } = 1000;

        [NinjaScriptProperty]
        [Range(1.0, 20.0)]
        [Display(Name = "Max Drawdown %", Description = "Maximum drawdown percentage", Order = 5, GroupName = "Risk Settings")]
        public double MaxDrawdownPercent { get; set; } = 8.0;

        [NinjaScriptProperty]
        [Range(0.5, 5.0)]
        [Display(Name = "Max Position Risk %", Description = "Maximum risk per position", Order = 6, GroupName = "Risk Settings")]
        public double MaxPositionRiskPercent { get; set; } = 2.0;

        [NinjaScriptProperty]
        [Display(Name = "Show Risk Panel", Description = "Display risk management panel", Order = 7, GroupName = "Display")]
        public bool ShowRiskPanel { get; set; } = true;

        [NinjaScriptProperty]
        [Display(Name = "Show Position Size", Description = "Display recommended position size", Order = 8, GroupName = "Display")]
        public bool ShowPositionSize { get; set; } = true;

        [NinjaScriptProperty]
        [Display(Name = "Risk Alerts", Description = "Enable risk alert notifications", Order = 9, GroupName = "Alerts")]
        public bool RiskAlerts { get; set; } = true;

        // Color properties
        [XmlIgnore]
        [Display(Name = "Safe Color", Description = "Color for safe risk status", Order = 10, GroupName = "Colors")]
        public Brush SafeColor { get; set; } = Brushes.LimeGreen;

        [XmlIgnore]
        [Display(Name = "Warning Color", Description = "Color for warning risk status", Order = 11, GroupName = "Colors")]
        public Brush WarningColor { get; set; } = Brushes.Orange;

        [XmlIgnore]
        [Display(Name = "Critical Color", Description = "Color for critical risk status", Order = 12, GroupName = "Colors")]
        public Brush CriticalColor { get; set; } = Brushes.Red;
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"Enigma-Apex Risk Management Indicator - Real-time risk monitoring and position sizing";
                Name = "EnigmaApexRiskManager";
                Calculate = Calculate.OnEachTick;
                IsOverlay = true;
                DisplayInDataBox = true;
                DrawOnPricePanel = true;
                IsSuspendedWhileInactive = false;

                // Initialize default values
                WebSocketPort = 8765;
                ServerAddress = "localhost";
                AccountBalance = 10000;
                MaxDailyLoss = 1000;
                MaxDrawdownPercent = 8.0;
                MaxPositionRiskPercent = 2.0;
                ShowRiskPanel = true;
                ShowPositionSize = true;
                RiskAlerts = true;
            }
            else if (State == State.DataLoaded)
            {
                // Initialize risk settings
                accountBalance = AccountBalance;
                maxDailyLoss = MaxDailyLoss;
                maxDrawdown = MaxDrawdownPercent;
                maxPositionRisk = MaxPositionRiskPercent;

                // Initialize WebSocket connection
                InitializeRiskManagerConnection();
            }
            else if (State == State.Terminated)
            {
                // Clean up WebSocket connection
                CleanupConnection();
            }
        }

        #region WebSocket Connection
        private async void InitializeRiskManagerConnection()
        {
            try
            {
                webSocket = new ClientWebSocket();
                cancellationToken = new CancellationTokenSource();

                string uri = $"ws://{ServerAddress}:{WebSocketPort}/risk";

                await webSocket.ConnectAsync(new Uri(uri), cancellationToken.Token);
                isConnected = true;

                // Send risk manager identification
                var identificationMessage = new
                {
                    type = "risk_manager_connect",
                    data = new
                    {
                        client_type = "ninja_risk_manager",
                        version = "1.0.0",
                        instrument = Instrument.MasterInstrument.Name,
                        account_balance = accountBalance,
                        risk_limits = new
                        {
                            max_daily_loss = maxDailyLoss,
                            max_drawdown = maxDrawdown,
                            max_position_risk = maxPositionRisk
                        }
                    }
                };

                string jsonMessage = JsonConvert.SerializeObject(identificationMessage);
                byte[] messageBytes = Encoding.UTF8.GetBytes(jsonMessage);

                await webSocket.SendAsync(new ArraySegment<byte>(messageBytes),
                    WebSocketMessageType.Text, true, cancellationToken.Token);

                // Start listening for risk updates
                _ = Task.Run(ListenForRiskUpdates);

                Print($"✅ Connected to Enigma-Apex Risk Manager at {uri}");
            }
            catch (Exception ex)
            {
                Print($"❌ Risk Manager connection failed: {ex.Message}");
                isConnected = false;
            }
        }

        private async Task ListenForRiskUpdates()
        {
            byte[] buffer = new byte[8192];

            try
            {
                while (webSocket.State == WebSocketState.Open && !cancellationToken.Token.IsCancellationRequested)
                {
                    var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken.Token);

                    if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        ProcessRiskUpdate(message);
                    }
                }
            }
            catch (Exception ex)
            {
                Print($"❌ Risk Manager listening error: {ex.Message}");
                isConnected = false;
            }
        }

        private void ProcessRiskUpdate(string message)
        {
            try
            {
                dynamic data = JsonConvert.DeserializeObject(message);

                if (data?.type == "risk_dashboard_update" && data?.data?.metrics != null)
                {
                    var metrics = data.data.metrics;

                    // Update risk metrics
                    accountBalance = metrics.account_balance ?? accountBalance;
                    dailyPnL = metrics.daily_pnl ?? 0;
                    weeklyPnL = metrics.weekly_pnl ?? 0;
                    currentDrawdown = metrics.current_drawdown ?? 0;
                    riskScore = metrics.risk_score ?? 50;
                    kellyPercentage = metrics.kelly_percentage ?? 0.02;

                    // Calculate recommended position size
                    CalculatePositionSize();

                    // Update risk status
                    UpdateRiskStatus(data.data);

                    lastRiskUpdate = DateTime.Now;

                    // Trigger UI update on main thread
                    Application.Current?.Dispatcher.BeginInvoke(new Action(() =>
                    {
                        UpdateRiskDisplay();
                    }));
                }
            }
            catch (Exception ex)
            {
                Print($"❌ Error processing risk update: {ex.Message}");
            }
        }

        private void CleanupConnection()
        {
            try
            {
                cancellationToken?.Cancel();
                webSocket?.CloseAsync(WebSocketCloseStatus.NormalClosure, "Risk Manager closing", CancellationToken.None);
                webSocket?.Dispose();
                cancellationToken?.Dispose();
            }
            catch (Exception ex)
            {
                Print($"❌ Risk Manager cleanup error: {ex.Message}");
            }
        }
        #endregion

        #region Risk Calculations
        private void CalculatePositionSize()
        {
            if (Close.Count == 0) return;

            double currentPrice = Close[0];
            double atr = CalculateATR(14); // 14-period ATR

            // Kelly Criterion position sizing
            double kellySize = accountBalance * kellyPercentage;

            // ATR-based position sizing
            double atrRisk = atr * 2; // 2 ATR stop loss
            double maxRiskDollar = accountBalance * (maxPositionRisk / 100);
            double atrPositionSize = maxRiskDollar / atrRisk;

            // Use the smaller of Kelly and ATR sizing
            recommendedPositionSize = Math.Min(kellySize, atrPositionSize);

            // Adjust for current risk level
            double riskAdjustment = 1.0;
            if (riskScore > 80) riskAdjustment = 0.5; // Reduce size for high risk
            else if (riskScore > 60) riskAdjustment = 0.75;
            else if (riskScore < 30) riskAdjustment = 1.25; // Increase size for low risk

            recommendedPositionSize *= riskAdjustment;

            // Ensure we don't exceed account balance
            recommendedPositionSize = Math.Min(recommendedPositionSize, accountBalance * 0.5);
        }

        private double CalculateATR(int period)
        {
            if (CurrentBar < period) return 0;

            double atrSum = 0;
            for (int i = 0; i < period; i++)
            {
                double tr = Math.Max(High[i] - Low[i],
                           Math.Max(Math.Abs(High[i] - Close[i + 1]),
                                   Math.Abs(Low[i] - Close[i + 1])));
                atrSum += tr;
            }

            return atrSum / period;
        }

        private void UpdateRiskStatus(dynamic riskData)
        {
            activeWarnings.Clear();

            // Determine risk status
            if (riskData?.violations != null && riskData.violations.Count > 0)
            {
                foreach (var violation in riskData.violations)
                {
                    string severity = violation.severity?.ToString() ?? "MEDIUM";
                    string message = violation.message?.ToString() ?? "Risk violation detected";

                    activeWarnings.Add($"{severity}: {message}");

                    if (severity == "CRITICAL")
                    {
                        riskStatus = "CRITICAL";
                    }
                    else if (severity == "HIGH" && riskStatus != "CRITICAL")
                    {
                        riskStatus = "WARNING";
                    }
                }
            }
            else
            {
                riskStatus = "SAFE";
            }

            // Additional risk checks
            if (currentDrawdown > maxDrawdown * 0.8) // 80% of max drawdown
            {
                if (!activeWarnings.Any(w => w.Contains("drawdown")))
                {
                    activeWarnings.Add($"WARNING: Approaching max drawdown ({currentDrawdown:F1}%)");
                    if (riskStatus == "SAFE") riskStatus = "WARNING";
                }
            }

            if (Math.Abs(dailyPnL) > maxDailyLoss * 0.8) // 80% of daily limit
            {
                if (!activeWarnings.Any(w => w.Contains("daily")))
                {
                    activeWarnings.Add($"WARNING: Approaching daily loss limit (${Math.Abs(dailyPnL):F0})");
                    if (riskStatus == "SAFE") riskStatus = "WARNING";
                }
            }
        }
        #endregion

        #region Display Updates
        private void UpdateRiskDisplay()
        {
            if (!ShowRiskPanel) return;

            // Determine display color based on risk status
            Brush statusColor = SafeColor;
            if (riskStatus == "WARNING") statusColor = WarningColor;
            else if (riskStatus == "CRITICAL") statusColor = CriticalColor;

            // Create risk panel text
            string riskPanelText = $"🛡️ RISK STATUS: {riskStatus}\n";
            riskPanelText += $"💰 Balance: ${accountBalance:F0}\n";
            riskPanelText += $"📈 Daily P&L: ${dailyPnL:F0}\n";
            riskPanelText += $"📉 Drawdown: {currentDrawdown:F1}%\n";
            riskPanelText += $"🎯 Risk Score: {riskScore:F0}/100";

            if (ShowPositionSize)
            {
                riskPanelText += $"\n💱 Rec. Size: ${recommendedPositionSize:F0}";
                riskPanelText += $"\n🎲 Kelly: {kellyPercentage:P1}";
            }

            // Draw risk panel
            Draw.TextFixed(this, "RiskPanel", riskPanelText,
                TextPosition.TopLeft, Brushes.White, new SimpleFont("Arial", 10),
                statusColor, statusColor, 5);

            // Draw position size recommendation
            if (ShowPositionSize && recommendedPositionSize > 0)
            {
                string sizeText = $"💱 Recommended Position Size: ${recommendedPositionSize:F0}";
                Draw.TextFixed(this, "PositionSize", sizeText,
                    TextPosition.BottomLeft, Brushes.White, new SimpleFont("Arial", 12),
                    Brushes.Navy, Brushes.Transparent, 0);
            }

            // Draw warnings if any
            if (activeWarnings.Count > 0)
            {
                string warningText = "⚠️ RISK WARNINGS:\n" + string.Join("\n", activeWarnings.Take(3));
                Draw.TextFixed(this, "RiskWarnings", warningText,
                    TextPosition.BottomRight, Brushes.White, new SimpleFont("Arial", 10),
                    Brushes.Red, Brushes.Yellow, 3);

                // Play alert sound for critical warnings
                if (RiskAlerts && riskStatus == "CRITICAL")
                {
                    PlaySound(@"C:\Program Files\NinjaTrader 8\sounds\Alert3.wav");
                }
            }

            // Connection status indicator
            string connectionText = isConnected ? "🟢 Risk Manager Connected" : "🔴 Risk Manager Disconnected";
            Draw.TextFixed(this, "ConnectionStatus", connectionText,
                TextPosition.TopRight, isConnected ? Brushes.LimeGreen : Brushes.Red,
                new SimpleFont("Arial", 8), Brushes.Transparent, Brushes.Transparent, 0);
        }
        #endregion

        protected override void OnBarUpdate()
        {
            // Update risk calculations on each bar
            if (IsFirstTickOfBar)
            {
                CalculatePositionSize();
                UpdateRiskDisplay();
            }

            // Connection health check
            if (CurrentBar % 50 == 0) // Check every 50 bars
            {
                if (!isConnected && webSocket?.State != WebSocketState.Open)
                {
                    Print("⚠️ Risk Manager connection lost. Attempting reconnection...");
                    _ = Task.Run(async () => await Task.Delay(3000).ContinueWith(t => InitializeRiskManagerConnection()));
                }
            }
        }

        protected override void OnMarketData(MarketDataEventArgs marketDataUpdate)
        {
            // Real-time position size updates
            if (marketDataUpdate.MarketDataType == MarketDataType.Last)
            {
                if ((DateTime.Now - lastRiskUpdate).TotalSeconds < 60) // Recent risk data
                {
                    CalculatePositionSize();
                    if (ShowPositionSize)
                    {
                        UpdateRiskDisplay();
                    }
                }
            }
        }

        #region Public Methods
        public double GetRecommendedPositionSize()
        {
            return recommendedPositionSize;
        }

        public string GetRiskStatus()
        {
            return riskStatus;
        }

        public double GetRiskScore()
        {
            return riskScore;
        }

        public bool IsRiskManagerConnected()
        {
            return isConnected && webSocket?.State == WebSocketState.Open;
        }

        public double GetCurrentDrawdown()
        {
            return currentDrawdown;
        }

        public double GetDailyPnL()
        {
            return dailyPnL;
        }

        public List<string> GetActiveWarnings()
        {
            return new List<string>(activeWarnings);
        }
        #endregion
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Indicators
{
    public partial class Indicator : NinjaTrader.Gui.NinjaScript.IndicatorRenderBase
    {
        private EnigmaApexRiskManager[] cacheEnigmaApexRiskManager;
        public EnigmaApexRiskManager EnigmaApexRiskManager(int webSocketPort, string serverAddress, double accountBalance, double maxDailyLoss, double maxDrawdownPercent, double maxPositionRiskPercent, bool showRiskPanel, bool showPositionSize, bool riskAlerts)
        {
            return EnigmaApexRiskManager(Input, webSocketPort, serverAddress, accountBalance, maxDailyLoss, maxDrawdownPercent, maxPositionRiskPercent, showRiskPanel, showPositionSize, riskAlerts);
        }

        public EnigmaApexRiskManager EnigmaApexRiskManager(ISeries<double> input, int webSocketPort, string serverAddress, double accountBalance, double maxDailyLoss, double maxDrawdownPercent, double maxPositionRiskPercent, bool showRiskPanel, bool showPositionSize, bool riskAlerts)
        {
            if (cacheEnigmaApexRiskManager != null)
                for (int idx = 0; idx < cacheEnigmaApexRiskManager.Length; idx++)
                    if (cacheEnigmaApexRiskManager[idx] != null && cacheEnigmaApexRiskManager[idx].WebSocketPort == webSocketPort && cacheEnigmaApexRiskManager[idx].ServerAddress == serverAddress && cacheEnigmaApexRiskManager[idx].AccountBalance == accountBalance && cacheEnigmaApexRiskManager[idx].MaxDailyLoss == maxDailyLoss && cacheEnigmaApexRiskManager[idx].MaxDrawdownPercent == maxDrawdownPercent && cacheEnigmaApexRiskManager[idx].MaxPositionRiskPercent == maxPositionRiskPercent && cacheEnigmaApexRiskManager[idx].ShowRiskPanel == showRiskPanel && cacheEnigmaApexRiskManager[idx].ShowPositionSize == showPositionSize && cacheEnigmaApexRiskManager[idx].RiskAlerts == riskAlerts && cacheEnigmaApexRiskManager[idx].EqualsInput(input))
                        return cacheEnigmaApexRiskManager[idx];
            return CacheIndicator<EnigmaApexRiskManager>(new EnigmaApexRiskManager() { WebSocketPort = webSocketPort, ServerAddress = serverAddress, AccountBalance = accountBalance, MaxDailyLoss = maxDailyLoss, MaxDrawdownPercent = maxDrawdownPercent, MaxPositionRiskPercent = maxPositionRiskPercent, ShowRiskPanel = showRiskPanel, ShowPositionSize = showPositionSize, RiskAlerts = riskAlerts }, input, ref cacheEnigmaApexRiskManager);
        }
    }
}

namespace NinjaTrader.NinjaScript.MarketAnalyzerColumns
{
    public partial class MarketAnalyzerColumn : MarketAnalyzerColumnBase
    {
        public Indicators.EnigmaApexRiskManager EnigmaApexRiskManager(int webSocketPort, string serverAddress, double accountBalance, double maxDailyLoss, double maxDrawdownPercent, double maxPositionRiskPercent, bool showRiskPanel, bool showPositionSize, bool riskAlerts)
        {
            return indicator.EnigmaApexRiskManager(Input, webSocketPort, serverAddress, accountBalance, maxDailyLoss, maxDrawdownPercent, maxPositionRiskPercent, showRiskPanel, showPositionSize, riskAlerts);
        }

        public Indicators.EnigmaApexRiskManager EnigmaApexRiskManager(ISeries<double> input, int webSocketPort, string serverAddress, double accountBalance, double maxDailyLoss, double maxDrawdownPercent, double maxPositionRiskPercent, bool showRiskPanel, bool showPositionSize, bool riskAlerts)
        {
            return indicator.EnigmaApexRiskManager(input, webSocketPort, serverAddress, accountBalance, maxDailyLoss, maxDrawdownPercent, maxPositionRiskPercent, showRiskPanel, showPositionSize, riskAlerts);
        }
    }
}

namespace NinjaTrader.NinjaScript.Strategies
{
    public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
    {
        public Indicators.EnigmaApexRiskManager EnigmaApexRiskManager(int webSocketPort, string serverAddress, double accountBalance, double maxDailyLoss, double maxDrawdownPercent, double maxPositionRiskPercent, bool showRiskPanel, bool showPositionSize, bool riskAlerts)
        {
            return indicator.EnigmaApexRiskManager(Input, webSocketPort, serverAddress, accountBalance, maxDailyLoss, maxDrawdownPercent, maxPositionRiskPercent, showRiskPanel, showPositionSize, riskAlerts);
        }

        public Indicators.EnigmaApexRiskManager EnigmaApexRiskManager(ISeries<double> input, int webSocketPort, string serverAddress, double accountBalance, double maxDailyLoss, double maxDrawdownPercent, double maxPositionRiskPercent, bool showRiskPanel, bool showPositionSize, bool riskAlerts)
        {
            return indicator.EnigmaApexRiskManager(input, webSocketPort, serverAddress, accountBalance, maxDailyLoss, maxDrawdownPercent, maxPositionRiskPercent, showRiskPanel, showPositionSize, riskAlerts);
        }
    }
}

#endregion
