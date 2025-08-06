// Enigma-Apex Automated Trading Strategy for NinjaTrader 8
// Professional algorithmic trading with risk management
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
using NinjaTrader.NinjaScript.Strategies;
#endregion

namespace NinjaTrader.NinjaScript.Strategies
{
    public class EnigmaApexAutoTrader : Strategy
    {
        #region Variables
        private EnigmaApexPowerScore enigmaPowerScore;
        private EnigmaApexRiskManager riskManager;

        // Strategy state
        private bool tradingEnabled = true;
        private bool enigmaSignalActive = false;
        private double lastSignalPowerScore = 0;
        private string lastSignalDirection = "";
        private DateTime lastTradeTime = DateTime.MinValue;
        private int consecutiveLosses = 0;

        // Performance tracking
        private double sessionPnL = 0;
        private int totalTrades = 0;
        private int winningTrades = 0;
        private double largestWin = 0;
        private double largestLoss = 0;
        private List<double> tradePnLs = new List<double>();

        // Risk management
        private double maxConsecutiveLosses = 3;
        private double cooldownMinutes = 15;
        private double emergencyStopLoss = 2.0; // 2% account
        #endregion

        #region Properties
        [NinjaScriptProperty]
        [Range(50, 100)]
        [Display(Name = "Min Power Score", Description = "Minimum Enigma power score to trade", Order = 1, GroupName = "Signal Filters")]
        public double MinPowerScore { get; set; } = 70;

        [NinjaScriptProperty]
        [Range(1, 5)]
        [Display(Name = "Min Confluence", Description = "Minimum confluence level required", Order = 2, GroupName = "Signal Filters")]
        public int MinConfluenceLevel { get; set; } = 2;

        [NinjaScriptProperty]
        [Display(Name = "Trade Bullish Signals", Description = "Enable bullish signal trading", Order = 3, GroupName = "Signal Filters")]
        public bool TradeBullishSignals { get; set; } = true;

        [NinjaScriptProperty]
        [Display(Name = "Trade Bearish Signals", Description = "Enable bearish signal trading", Order = 4, GroupName = "Signal Filters")]
        public bool TradeBearishSignals { get; set; } = true;

        [NinjaScriptProperty]
        [Range(0.1, 5.0)]
        [Display(Name = "Risk Per Trade %", Description = "Risk percentage per trade", Order = 5, GroupName = "Risk Management")]
        public double RiskPerTrade { get; set; } = 1.0;

        [NinjaScriptProperty]
        [Range(1.0, 10.0)]
        [Display(Name = "Reward Risk Ratio", Description = "Minimum reward to risk ratio", Order = 6, GroupName = "Risk Management")]
        public double RewardRiskRatio { get; set; } = 2.0;

        [NinjaScriptProperty]
        [Range(5, 60)]
        [Display(Name = "Stop Loss ATR", Description = "Stop loss in ATR multiples", Order = 7, GroupName = "Risk Management")]
        public double StopLossATR { get; set; } = 2.0;

        [NinjaScriptProperty]
        [Range(10, 120)]
        [Display(Name = "Max Trade Duration", Description = "Maximum trade duration in minutes", Order = 8, GroupName = "Risk Management")]
        public int MaxTradeDurationMinutes { get; set; } = 60;

        [NinjaScriptProperty]
        [Display(Name = "Use Dynamic Sizing", Description = "Use risk manager position sizing", Order = 9, GroupName = "Position Sizing")]
        public bool UseDynamicSizing { get; set; } = true;

        [NinjaScriptProperty]
        [Range(100, 100000)]
        [Display(Name = "Default Position Size", Description = "Default position size in dollars", Order = 10, GroupName = "Position Sizing")]
        public double DefaultPositionSize { get; set; } = 1000;

        [NinjaScriptProperty]
        [Range(1, 10)]
        [Display(Name = "Max Positions", Description = "Maximum concurrent positions", Order = 11, GroupName = "Position Sizing")]
        public int MaxPositions { get; set; } = 1;

        [NinjaScriptProperty]
        [Display(Name = "Trading Hours Only", Description = "Trade only during market hours", Order = 12, GroupName = "Time Filters")]
        public bool TradingHoursOnly { get; set; } = true;

        [NinjaScriptProperty]
        [Range(0, 23)]
        [Display(Name = "Start Hour", Description = "Trading start hour (24h format)", Order = 13, GroupName = "Time Filters")]
        public int StartHour { get; set; } = 9;

        [NinjaScriptProperty]
        [Range(0, 23)]
        [Display(Name = "End Hour", Description = "Trading end hour (24h format)", Order = 14, GroupName = "Time Filters")]
        public int EndHour { get; set; } = 16;

        [NinjaScriptProperty]
        [Display(Name = "Enable Logging", Description = "Enable detailed trade logging", Order = 15, GroupName = "Logging")]
        public bool EnableLogging { get; set; } = true;

        [NinjaScriptProperty]
        [Display(Name = "Visual Signals", Description = "Show trade signals on chart", Order = 16, GroupName = "Display")]
        public bool ShowVisualSignals { get; set; } = true;
        #endregion

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = @"Enigma-Apex Automated Trading Strategy - Professional algorithmic trading with advanced risk management";
                Name = "EnigmaApexAutoTrader";
                Calculate = Calculate.OnEachTick;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                IsFillLimitOnTouch = false;
                MaximumBarsLookBack = MaximumBarsLookBack.TwoHundredFiftySix;
                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 0;
                StartBehavior = StartBehavior.WaitUntilFlat;
                TimeInForce = TimeInForce.Gtc;
                TraceOrders = false;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelClose;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade = 50;
                IsInstantiatedOnEachOptimizationIteration = true;

                // Set default values
                MinPowerScore = 70;
                MinConfluenceLevel = 2;
                TradeBullishSignals = true;
                TradeBearishSignals = true;
                RiskPerTrade = 1.0;
                RewardRiskRatio = 2.0;
                StopLossATR = 2.0;
                MaxTradeDurationMinutes = 60;
                UseDynamicSizing = true;
                DefaultPositionSize = 1000;
                MaxPositions = 1;
                TradingHoursOnly = true;
                StartHour = 9;
                EndHour = 16;
                EnableLogging = true;
                ShowVisualSignals = true;
            }
            else if (State == State.DataLoaded)
            {
                // Initialize indicators
                enigmaPowerScore = EnigmaApexPowerScore(8765, "localhost", true, true, MinPowerScore, true);
                riskManager = EnigmaApexRiskManager(8765, "localhost", 10000, 1000, 8.0, RiskPerTrade, true, true, true);

                // Add indicators to chart
                AddChartIndicator(enigmaPowerScore);
                AddChartIndicator(riskManager);

                if (EnableLogging)
                {
                    Print($"🚀 Enigma-Apex AutoTrader initialized for {Instrument.MasterInstrument.Name}");
                    Print($"   Min Power Score: {MinPowerScore}");
                    Print($"   Risk Per Trade: {RiskPerTrade}%");
                    Print($"   Reward:Risk Ratio: {RewardRiskRatio}:1");
                }
            }
            else if (State == State.Terminated)
            {
                if (EnableLogging)
                {
                    LogSessionSummary();
                }
            }
        }

        protected override void OnBarUpdate()
        {
            // Ensure we have enough data
            if (CurrentBar < BarsRequiredToTrade) return;

            // Check if indicators are ready
            if (enigmaPowerScore == null || riskManager == null) return;

            // Update strategy state
            UpdateStrategyState();

            // Check for exit conditions first
            CheckExitConditions();

            // Check for new entry signals
            if (tradingEnabled && Position.MarketPosition == MarketPosition.Flat)
            {
                CheckEntryConditions();
            }

            // Update performance tracking
            UpdatePerformanceMetrics();
        }

        #region Strategy Logic
        private void UpdateStrategyState()
        {
            // Check risk manager status
            if (!riskManager.IsRiskManagerConnected())
            {
                if (tradingEnabled)
                {
                    tradingEnabled = false;
                    if (EnableLogging)
                        Print("⚠️ Trading disabled - Risk Manager disconnected");
                }
                return;
            }

            // Check risk status
            string riskStatus = riskManager.GetRiskStatus();
            if (riskStatus == "CRITICAL")
            {
                if (tradingEnabled)
                {
                    tradingEnabled = false;
                    if (EnableLogging)
                        Print("🚨 Trading disabled - CRITICAL risk status");

                    // Close all positions immediately
                    if (Position.MarketPosition != MarketPosition.Flat)
                    {
                        ExitLong("RiskStop", "");
                        ExitShort("RiskStop", "");
                    }
                }
                return;
            }

            // Re-enable trading if risk status improves
            if (!tradingEnabled && riskStatus == "SAFE")
            {
                tradingEnabled = true;
                if (EnableLogging)
                    Print("✅ Trading re-enabled - Risk status: SAFE");
            }

            // Check consecutive losses
            if (consecutiveLosses >= maxConsecutiveLosses)
            {
                TimeSpan timeSinceLastTrade = DateTime.Now - lastTradeTime;
                if (timeSinceLastTrade.TotalMinutes < cooldownMinutes)
                {
                    tradingEnabled = false;
                    return;
                }
                else
                {
                    consecutiveLosses = 0; // Reset after cooldown
                    tradingEnabled = true;
                }
            }

            // Check trading hours
            if (TradingHoursOnly)
            {
                int currentHour = DateTime.Now.Hour;
                if (currentHour < StartHour || currentHour >= EndHour)
                {
                    tradingEnabled = false;
                    return;
                }
            }
        }

        private void CheckEntryConditions()
        {
            if (!tradingEnabled) return;
            if (Position.MarketPosition != MarketPosition.Flat) return;

            // Get current Enigma signals
            double currentPowerScore = enigmaPowerScore.GetCurrentPowerScore();
            string currentSignalColor = enigmaPowerScore.GetCurrentSignalColor();

            // Check if we have a valid signal
            if (currentPowerScore < MinPowerScore) return;

            // Calculate position size
            double positionSize = CalculatePositionSize();
            if (positionSize <= 0) return;

            // Calculate ATR for stop loss
            double atr = CalculateATR(14);
            if (atr <= 0) return;

            // Check bullish signal
            if (TradeBullishSignals && currentSignalColor == "green")
            {
                double stopLoss = Close[0] - (StopLossATR * atr);
                double takeProfit = Close[0] + (StopLossATR * atr * RewardRiskRatio);

                if (IsValidEntry("LONG", stopLoss, takeProfit))
                {
                    EnterLong(Convert.ToInt32(positionSize), "EnigmaLong");
                    SetStopLoss("EnigmaLong", CalculationMode.Price, stopLoss, false);
                    SetProfitTarget("EnigmaLong", CalculationMode.Price, takeProfit);

                    lastSignalPowerScore = currentPowerScore;
                    lastSignalDirection = "LONG";
                    lastTradeTime = DateTime.Now;

                    if (EnableLogging)
                    {
                        Print($"🟢 LONG Entry: Power {currentPowerScore:F0}% | Size: {positionSize} | SL: {stopLoss:F2} | TP: {takeProfit:F2}");
                    }

                    if (ShowVisualSignals)
                    {
                        Draw.ArrowUp(this, $"LongEntry_{CurrentBar}", true, 0, Low[0] - 2 * TickSize, Brushes.LimeGreen);
                        Draw.Text(this, $"LongText_{CurrentBar}", $"LONG\n{currentPowerScore:F0}%", 0, Low[0] - 4 * TickSize, Brushes.LimeGreen);
                    }
                }
            }

            // Check bearish signal
            if (TradeBearishSignals && currentSignalColor == "red")
            {
                double stopLoss = Close[0] + (StopLossATR * atr);
                double takeProfit = Close[0] - (StopLossATR * atr * RewardRiskRatio);

                if (IsValidEntry("SHORT", stopLoss, takeProfit))
                {
                    EnterShort(Convert.ToInt32(positionSize), "EnigmaShort");
                    SetStopLoss("EnigmaShort", CalculationMode.Price, stopLoss, false);
                    SetProfitTarget("EnigmaShort", CalculationMode.Price, takeProfit);

                    lastSignalPowerScore = currentPowerScore;
                    lastSignalDirection = "SHORT";
                    lastTradeTime = DateTime.Now;

                    if (EnableLogging)
                    {
                        Print($"🔴 SHORT Entry: Power {currentPowerScore:F0}% | Size: {positionSize} | SL: {stopLoss:F2} | TP: {takeProfit:F2}");
                    }

                    if (ShowVisualSignals)
                    {
                        Draw.ArrowDown(this, $"ShortEntry_{CurrentBar}", true, 0, High[0] + 2 * TickSize, Brushes.Red);
                        Draw.Text(this, $"ShortText_{CurrentBar}", $"SHORT\n{currentPowerScore:F0}%", 0, High[0] + 4 * TickSize, Brushes.Red);
                    }
                }
            }
        }

        private void CheckExitConditions()
        {
            if (Position.MarketPosition == MarketPosition.Flat) return;

            // Time-based exit
            if (Position.MarketPosition != MarketPosition.Flat)
            {
                TimeSpan tradeTime = DateTime.Now - lastTradeTime;
                if (tradeTime.TotalMinutes >= MaxTradeDurationMinutes)
                {
                    ExitLong("TimeExit", "");
                    ExitShort("TimeExit", "");

                    if (EnableLogging)
                    {
                        Print($"⏰ Time exit after {tradeTime.TotalMinutes:F0} minutes");
                    }
                    return;
                }
            }

            // Emergency stop loss based on account percentage
            double accountBalance = riskManager.GetAccountBalance();
            if (accountBalance > 0)
            {
                double unrealizedPnL = Position.GetUnrealizedProfitLoss(PerformanceUnit.Currency, Close[0]);
                double accountRisk = Math.Abs(unrealizedPnL) / accountBalance * 100;

                if (accountRisk >= emergencyStopLoss)
                {
                    ExitLong("EmergencyStop", "");
                    ExitShort("EmergencyStop", "");

                    if (EnableLogging)
                    {
                        Print($"🚨 Emergency stop: Account risk {accountRisk:F1}%");
                    }
                }
            }
        }

        private bool IsValidEntry(string direction, double stopLoss, double takeProfit)
        {
            // Check if we already have maximum positions
            if (Position.MarketPosition != MarketPosition.Flat && MaxPositions <= 1)
                return false;

            // Validate stop loss and take profit levels
            if (direction == "LONG")
            {
                if (stopLoss >= Close[0] || takeProfit <= Close[0])
                    return false;
            }
            else if (direction == "SHORT")
            {
                if (stopLoss <= Close[0] || takeProfit >= Close[0])
                    return false;
            }

            // Check risk-reward ratio
            double risk = Math.Abs(Close[0] - stopLoss);
            double reward = Math.Abs(takeProfit - Close[0]);
            double actualRR = reward / risk;

            if (actualRR < RewardRiskRatio)
                return false;

            return true;
        }

        private double CalculatePositionSize()
        {
            double positionSize = DefaultPositionSize;

            if (UseDynamicSizing && riskManager != null)
            {
                double recommendedSize = riskManager.GetRecommendedPositionSize();
                if (recommendedSize > 0)
                {
                    positionSize = recommendedSize;
                }
            }

            // Apply risk per trade limit
            double accountBalance = riskManager?.GetAccountBalance() ?? 10000;
            double maxRiskSize = accountBalance * (RiskPerTrade / 100);

            return Math.Min(positionSize, maxRiskSize);
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
        #endregion

        #region Performance Tracking
        protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            if (execution.Order != null && execution.Order.OrderState == OrderState.Filled)
            {
                if (execution.Order.IsEntry)
                {
                    totalTrades++;
                    if (EnableLogging)
                    {
                        Print($"📈 Trade #{totalTrades} entered: {execution.Order.Name} at {price:F2}");
                    }
                }
                else if (execution.Order.IsExit)
                {
                    double tradePnL = execution.Order.Filled * (execution.Price - execution.Order.AverageFillPrice) *
                                    (marketPosition == MarketPosition.Long ? 1 : -1) * Instrument.MasterInstrument.PointValue;

                    tradePnLs.Add(tradePnL);
                    sessionPnL += tradePnL;

                    if (tradePnL > 0)
                    {
                        winningTrades++;
                        largestWin = Math.Max(largestWin, tradePnL);
                        consecutiveLosses = 0; // Reset consecutive losses
                    }
                    else
                    {
                        largestLoss = Math.Min(largestLoss, tradePnL);
                        consecutiveLosses++;
                    }

                    if (EnableLogging)
                    {
                        double winRate = totalTrades > 0 ? (winningTrades / (double)totalTrades) * 100 : 0;
                        Print($"💰 Trade closed: P&L ${tradePnL:F2} | Session P&L: ${sessionPnL:F2} | Win Rate: {winRate:F1}%");

                        if (consecutiveLosses >= 2)
                        {
                            Print($"⚠️ Consecutive losses: {consecutiveLosses}");
                        }
                    }
                }
            }
        }

        private void UpdatePerformanceMetrics()
        {
            // Update session performance display
            if (ShowVisualSignals && CurrentBar % 50 == 0) // Update every 50 bars
            {
                double winRate = totalTrades > 0 ? (winningTrades / (double)totalTrades) * 100 : 0;
                string performanceText = $"📊 ENIGMA AUTO-TRADER\n";
                performanceText += $"Session P&L: ${sessionPnL:F0}\n";
                performanceText += $"Trades: {totalTrades} | Win Rate: {winRate:F1}%\n";
                performanceText += $"Risk Status: {riskManager?.GetRiskStatus() ?? "Unknown"}";

                Brush textColor = sessionPnL >= 0 ? Brushes.LimeGreen : Brushes.Red;

                Draw.TextFixed(this, "PerformanceDisplay", performanceText,
                    TextPosition.BottomLeft, Brushes.White, new SimpleFont("Arial", 10),
                    textColor, Brushes.Transparent, 5);
            }
        }

        private void LogSessionSummary()
        {
            Print("\n" + "=" * 50);
            Print("📊 ENIGMA-APEX AUTO-TRADER SESSION SUMMARY");
            Print("=" * 50);
            Print($"Instrument: {Instrument.MasterInstrument.Name}");
            Print($"Total Trades: {totalTrades}");
            Print($"Winning Trades: {winningTrades}");
            Print($"Win Rate: {(totalTrades > 0 ? (winningTrades / (double)totalTrades) * 100 : 0):F1}%");
            Print($"Session P&L: ${sessionPnL:F2}");
            Print($"Largest Win: ${largestWin:F2}");
            Print($"Largest Loss: ${largestLoss:F2}");

            if (tradePnLs.Count > 0)
            {
                double avgTrade = tradePnLs.Average();
                Print($"Average Trade: ${avgTrade:F2}");

                if (tradePnLs.Count > 1)
                {
                    double stdDev = Math.Sqrt(tradePnLs.Select(x => Math.Pow(x - avgTrade, 2)).Average());
                    Print($"Standard Deviation: ${stdDev:F2}");
                }
            }

            Print("=" * 50);
        }
        #endregion
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace NinjaTrader.NinjaScript.Strategies
{
    public partial class Strategy : NinjaTrader.Gui.NinjaScript.StrategyRenderBase
    {
        private EnigmaApexAutoTrader[] cacheEnigmaApexAutoTrader;
        public EnigmaApexAutoTrader EnigmaApexAutoTrader(double minPowerScore, int minConfluenceLevel, bool tradeBullishSignals, bool tradeBearishSignals, double riskPerTrade, double rewardRiskRatio, double stopLossATR, int maxTradeDurationMinutes, bool useDynamicSizing, double defaultPositionSize, int maxPositions, bool tradingHoursOnly, int startHour, int endHour, bool enableLogging, bool showVisualSignals)
        {
            return EnigmaApexAutoTrader(Input, minPowerScore, minConfluenceLevel, tradeBullishSignals, tradeBearishSignals, riskPerTrade, rewardRiskRatio, stopLossATR, maxTradeDurationMinutes, useDynamicSizing, defaultPositionSize, maxPositions, tradingHoursOnly, startHour, endHour, enableLogging, showVisualSignals);
        }

        public EnigmaApexAutoTrader EnigmaApexAutoTrader(ISeries<double> input, double minPowerScore, int minConfluenceLevel, bool tradeBullishSignals, bool tradeBearishSignals, double riskPerTrade, double rewardRiskRatio, double stopLossATR, int maxTradeDurationMinutes, bool useDynamicSizing, double defaultPositionSize, int maxPositions, bool tradingHoursOnly, int startHour, int endHour, bool enableLogging, bool showVisualSignals)
        {
            if (cacheEnigmaApexAutoTrader != null)
                for (int idx = 0; idx < cacheEnigmaApexAutoTrader.Length; idx++)
                    if (cacheEnigmaApexAutoTrader[idx] != null && cacheEnigmaApexAutoTrader[idx].MinPowerScore == minPowerScore && cacheEnigmaApexAutoTrader[idx].MinConfluenceLevel == minConfluenceLevel && cacheEnigmaApexAutoTrader[idx].TradeBullishSignals == tradeBullishSignals && cacheEnigmaApexAutoTrader[idx].TradeBearishSignals == tradeBearishSignals && cacheEnigmaApexAutoTrader[idx].RiskPerTrade == riskPerTrade && cacheEnigmaApexAutoTrader[idx].RewardRiskRatio == rewardRiskRatio && cacheEnigmaApexAutoTrader[idx].StopLossATR == stopLossATR && cacheEnigmaApexAutoTrader[idx].MaxTradeDurationMinutes == maxTradeDurationMinutes && cacheEnigmaApexAutoTrader[idx].UseDynamicSizing == useDynamicSizing && cacheEnigmaApexAutoTrader[idx].DefaultPositionSize == defaultPositionSize && cacheEnigmaApexAutoTrader[idx].MaxPositions == maxPositions && cacheEnigmaApexAutoTrader[idx].TradingHoursOnly == tradingHoursOnly && cacheEnigmaApexAutoTrader[idx].StartHour == startHour && cacheEnigmaApexAutoTrader[idx].EndHour == endHour && cacheEnigmaApexAutoTrader[idx].EnableLogging == enableLogging && cacheEnigmaApexAutoTrader[idx].ShowVisualSignals == showVisualSignals && cacheEnigmaApexAutoTrader[idx].EqualsInput(input))
                        return cacheEnigmaApexAutoTrader[idx];
            return CacheIndicator<EnigmaApexAutoTrader>(new EnigmaApexAutoTrader() { MinPowerScore = minPowerScore, MinConfluenceLevel = minConfluenceLevel, TradeBullishSignals = tradeBullishSignals, TradeBearishSignals = tradeBearishSignals, RiskPerTrade = riskPerTrade, RewardRiskRatio = rewardRiskRatio, StopLossATR = stopLossATR, MaxTradeDurationMinutes = maxTradeDurationMinutes, UseDynamicSizing = useDynamicSizing, DefaultPositionSize = defaultPositionSize, MaxPositions = maxPositions, TradingHoursOnly = tradingHoursOnly, StartHour = startHour, EndHour = endHour, EnableLogging = enableLogging, ShowVisualSignals = showVisualSignals }, input, ref cacheEnigmaApexAutoTrader);
        }
    }
}

#endregion
