
from app.analysis.entry_exit import (
    generate_trade_setup,
    generate_final_decision,
    identify_market_bias,
)

from app.analysis.volume import (
    calculate_time_slot_average_volume,
    classify_volume_strength,
)

from app.analysis.ema import calculate_ema
from app.analysis.rsi import calculate_rsi
from app.analysis.vwap import calculate_vwap
from app.analysis.candle_aggregator import aggregate_5min_to_15min
from app.analysis.support_resistance import identify_support_resistance
from app.analysis.breakout import detect_breakout

from app.schemas.market import Candle


class TechnicalAnalysisService:

    def analyze(
        self,
        historical_candles: list[Candle],
        today_candles: list[Candle],
    ) -> dict:

        if not historical_candles:
            raise ValueError("Historical candles are required")

        if not today_candles:
            raise ValueError(
                "At least one completed 5-minute candle is required"
            )

        # 1. Combine historical and today's 5-minute candles
        combined_candles = historical_candles + today_candles

        # 2. Calculate common session VWAP from original 5-minute candles
        today_vwap_values = calculate_vwap(
            [c.high for c in today_candles],
            [c.low for c in today_candles],
            [c.close for c in today_candles],
            [c.volume for c in today_candles]
        )

        today_vwap = (
            today_vwap_values[-1]
            if today_vwap_values
            else None
        )

        # 3. Analyse 5-minute timeframe
        analysis_5min = self.analyze_timeframe(
            candles=combined_candles,
            today_candles=today_candles,
            historical_candles=historical_candles,
            today_vwap=today_vwap
        )

        # 4. Aggregate historical and today's candles separately
        historical_15min = aggregate_5min_to_15min(
            historical_candles
        )

        today_15min = aggregate_5min_to_15min(
            today_candles
        )

        combined_15min = historical_15min + today_15min

        # 5. Analyse 15-minute timeframe
        if today_15min:

            analysis_15min = self.analyze_timeframe(
                candles=combined_15min,
                today_candles=today_15min,
                historical_candles=historical_15min,
                today_vwap=today_vwap
            )

        else:

            analysis_15min = {
                "last_price": None,
                "ema_9": None,
                "ema_21": None,
                "rsi_14": None,
                "vwap": today_vwap,
                "volume_analysis": None,
                "support_resistance": None,
                "breakout_analysis": None,
                "trade_setup": {
                    "trade_setup": False,
                    "reason": "No completed 15-minute candle available"
                }
            }

        # 6. Interpret both timeframes
        interpretation_5min = self.interpret_analysis(
            analysis_5min
        )

        if analysis_15min["last_price"] is not None:

            interpretation_15min = self.interpret_analysis(
                analysis_15min
            )

        else:

            interpretation_15min = {
                "trend": "UNAVAILABLE",
                "momentum": "UNAVAILABLE",
                "rsi_condition": "UNAVAILABLE",
                "price_position": "UNAVAILABLE"
            }

        result_5min = {
            "indicators": analysis_5min,
            "interpretation": interpretation_5min
        }

        result_15min = {
            "indicators": analysis_15min,
            "interpretation": interpretation_15min
        }

        # 7. Generate final trading decision
        if today_15min:

            final_decision = generate_final_decision(
                result_5min,
                result_15min
            )

            market_bias = identify_market_bias(
                result_5min,
                result_15min
            )

        else:

            final_decision = {
                "decision": "WAIT",
                "reason": "Waiting for a completed 15-minute candle"
            }

            market_bias = {
                "market_bias": "NEUTRAL",
                "action": "WAIT",
                "reason": "Waiting for 15-minute confirmation"
            }

        return {
            "5min_analysis": result_5min,
            "15min_analysis": result_15min,
            "market_bias": market_bias,
            "final_decision": final_decision
        }

    @staticmethod
    def analyze_timeframe(
        candles: list[Candle],
        today_candles: list[Candle],
        historical_candles: list[Candle],
        today_vwap: float | None
    ) -> dict:

        # 1. Validate warm-up data
        if len(candles) < 21:
            raise ValueError(
                "At least 21 combined candles are required"
            )

        # 2. Prepare combined historical + today's data
        closes = [c.close for c in candles]

        # 3. Calculate EMA and RSI
        ema_9 = calculate_ema(closes, 9)
        ema_21 = calculate_ema(closes, 21)
        rsi_14 = calculate_rsi(closes, 14)

        # 4. Use common session VWAP
        vwap = today_vwap

        current_price = (
            today_candles[-1].close
            if today_candles
            else None
        )

        # 5. Calculate time-of-day adjusted average volume
        current_volume = (
            today_candles[-1].volume
            if today_candles
            else None
        )

        average_volume = None
        rvol = None
        volume_strength = None

        if today_candles and historical_candles:

            average_volume = calculate_time_slot_average_volume(
                historical_candles=historical_candles,
                current_candle=today_candles[-1],
                lookback_sessions=5
            )

        if (
            current_volume is not None
            and average_volume is not None
            and average_volume > 0
        ):

            rvol = current_volume / average_volume

            volume_strength = classify_volume_strength(
                rvol
            )

        volume_analysis = {
            "current_volume": current_volume,
            "average_volume": average_volume,
            "rvol": rvol,
            "volume_strength": volume_strength
        }

        # 6. Identify support and resistance
        support_resistance = identify_support_resistance(
            candles[:-1],
            lookback=20
        )

        # 7. Initialize breakout analysis
        breakout_analysis = None

        trade_setup = {
            "trade_setup": False,
            "reason": "Insufficient current-session data"
        }

        # 8. Detect breakout with volume confirmation
        if (
            len(today_candles) >= 2
            and average_volume is not None
            and average_volume > 0
        ):

            breakout_analysis = detect_breakout(
                previous_candle=today_candles[-2],
                current_candle=today_candles[-1],
                support=support_resistance["support"],
                resistance=support_resistance["resistance"],
                average_volume=average_volume
            )

            trade_setup = generate_trade_setup(
                breakout_analysis=breakout_analysis,
                current_candle=today_candles[-1],
                risk_reward_ratio=2.0
            )

        return {
            "last_price": current_price,
            "ema_9": ema_9[-1],
            "ema_21": ema_21[-1],
            "rsi_14": rsi_14[-1],
            "vwap": vwap,
            "volume_analysis": volume_analysis,
            "support_resistance": support_resistance,
            "breakout_analysis": breakout_analysis,
            "trade_setup": trade_setup
        }

    @staticmethod
    def interpret_analysis(analysis: dict) -> dict:

        last_price = analysis["last_price"]
        ema_9 = analysis["ema_9"]
        ema_21 = analysis["ema_21"]
        rsi = analysis["rsi_14"]
        vwap = analysis["vwap"]

        # 1. Trend interpretation
        if ema_9 > ema_21:
            trend = "BULLISH"

        elif ema_9 < ema_21:
            trend = "BEARISH"

        else:
            trend = "SIDEWAYS"

        # 2. Momentum interpretation
        if rsi > 50:
            momentum = "POSITIVE"

        elif rsi < 50:
            momentum = "NEGATIVE"

        else:
            momentum = "NEUTRAL"

        # 3. RSI condition
        if rsi >= 70:
            rsi_condition = "OVERBOUGHT"

        elif rsi <= 30:
            rsi_condition = "OVERSOLD"

        else:
            rsi_condition = "NORMAL"

        # 4. VWAP interpretation
        if vwap is None or last_price is None:
            price_position = "UNAVAILABLE"

        elif last_price > vwap:
            price_position = "ABOVE_VWAP"

        elif last_price < vwap:
            price_position = "BELOW_VWAP"

        else:
            price_position = "AT_VWAP"

        return {
            "trend": trend,
            "momentum": momentum,
            "rsi_condition": rsi_condition,
            "price_position": price_position
        }
