import json
import random
from datetime import datetime, timezone
from typing import Any

from backend.tools.base import BaseTool


class MarketDataServer(BaseTool):
    name = "MarketDataServer"
    description = "Real-time and historical market data for equities, ETFs, indices, forex, and crypto"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get_quote", "get_market_overview", "get_historical", "get_options_chain"],
            },
            "symbol": {"type": "string", "description": "Ticker symbol"},
            "start_date": {"type": "string", "description": "Start date YYYY-MM-DD"},
            "end_date": {"type": "string", "description": "End date YYYY-MM-DD"},
        },
    }

    async def validate(self, **kwargs) -> bool:
        action = kwargs.get("action")
        return action in ("get_quote", "get_market_overview", "get_historical", "get_options_chain")

    async def execute(self, **kwargs) -> dict[str, Any]:
        action = kwargs.get("action", "get_market_overview")
        symbol = kwargs.get("symbol", "SPY")

        if action == "get_quote":
            return {
                "symbol": symbol,
                "price": round(random.uniform(100, 600), 2),
                "change": round(random.uniform(-5, 5), 2),
                "change_pct": round(random.uniform(-2, 2), 2),
                "volume": random.randint(1000000, 50000000),
                "bid": round(random.uniform(100, 600), 2),
                "ask": round(random.uniform(100, 600), 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        elif action == "get_market_overview":
            indices = ["SPY", "QQQ", "DIA", "IWM"]
            return {
                "indices": [
                    {"symbol": idx, "price": round(random.uniform(200, 500), 2),
                     "change_pct": round(random.uniform(-1.5, 1.5), 2)}
                    for idx in indices
                ],
                "advancers": random.randint(800, 2000),
                "decliners": random.randint(500, 1500),
                "unchanged": random.randint(100, 400),
                "market_status": "open",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        elif action == "get_historical":
            days = 30
            return {
                "symbol": symbol,
                "interval": "1d",
                "data": [
                    {
                        "date": f"2024-{(i % 12)+1:02d}-{(i % 28)+1:02d}",
                        "open": round(random.uniform(100, 600), 2),
                        "high": round(random.uniform(100, 600), 2),
                        "low": round(random.uniform(100, 600), 2),
                        "close": round(random.uniform(100, 600), 2),
                        "volume": random.randint(1000000, 50000000),
                    }
                    for i in range(days)
                ],
            }
        elif action == "get_options_chain":
            return {
                "symbol": symbol,
                "expirations": ["2024-12-20", "2025-01-17", "2025-03-21"],
                "calls": [
                    {"strike": 180, "bid": 5.20, "ask": 5.30, "volume": 15000, "oi": 45000},
                    {"strike": 185, "bid": 3.10, "ask": 3.20, "volume": 22000, "oi": 62000},
                ],
                "puts": [
                    {"strike": 180, "bid": 4.80, "ask": 4.90, "volume": 18000, "oi": 38000},
                    {"strike": 185, "bid": 6.50, "ask": 6.60, "volume": 12000, "oi": 29000},
                ],
            }
        return {"error": f"Unknown action: {action}"}


class PortfolioServer(BaseTool):
    name = "PortfolioServer"
    description = "Portfolio management, rebalancing, tax-loss harvesting, and performance analytics"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get_portfolio", "get_performance", "rebalance", "tax_loss_harvest"],
            },
            "portfolio_id": {"type": "string"},
        },
    }

    async def validate(self, **kwargs) -> bool:
        return kwargs.get("action") in ("get_portfolio", "get_performance", "rebalance", "tax_loss_harvest")

    async def execute(self, **kwargs) -> dict[str, Any]:
        action = kwargs.get("action", "get_portfolio")
        portfolio_id = kwargs.get("portfolio_id", "PF-001")

        if action == "get_portfolio":
            return {
                "portfolio_id": portfolio_id,
                "total_value": round(random.uniform(100000, 5000000), 2),
                "cash": round(random.uniform(5000, 500000), 2),
                "holdings": [
                    {"symbol": "AAPL", "shares": 500, "avg_cost": 150.00, "current_price": 178.50, "value": 89250},
                    {"symbol": "MSFT", "shares": 200, "avg_cost": 330.00, "current_price": 378.90, "value": 75780},
                    {"symbol": "GOOGL", "shares": 150, "avg_cost": 130.00, "current_price": 142.50, "value": 21375},
                    {"symbol": "SPY", "shares": 300, "avg_cost": 450.00, "current_price": 478.20, "value": 143460},
                ],
                "allocation": {"equities": 0.65, "bonds": 0.20, "cash": 0.10, "alternatives": 0.05},
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
        elif action == "get_performance":
            return {
                "portfolio_id": portfolio_id,
                "ytd_return": round(random.uniform(-10, 25), 2),
                "one_year_return": round(random.uniform(-5, 30), 2),
                "three_year_return": round(random.uniform(5, 60), 2),
                "since_inception": round(random.uniform(10, 100), 2),
                "sharpe_ratio": round(random.uniform(0.5, 2.5), 2),
                "volatility": round(random.uniform(8, 25), 2),
                "max_drawdown": round(random.uniform(-5, -35), 2),
                "alpha": round(random.uniform(-2, 5), 2),
                "beta": round(random.uniform(0.5, 1.5), 2),
            }
        elif action == "rebalance":
            return {
                "portfolio_id": portfolio_id,
                "rebalancing_required": True,
                "trades": [
                    {"action": "sell", "symbol": "AAPL", "amount": 15000, "reason": "overweight"},
                    {"action": "buy", "symbol": "BND", "amount": 15000, "reason": "underweight bonds"},
                ],
                "estimated_cost": round(random.uniform(10, 100), 2),
                "tax_impact": round(random.uniform(-500, 500), 2),
            }
        elif action == "tax_loss_harvest":
            return {
                "portfolio_id": portfolio_id,
                "opportunities_found": random.randint(1, 5),
                "total_loss_captured": round(random.uniform(1000, 25000), 2),
                "tax_savings_estimate": round(random.uniform(200, 5000), 2),
                "suggested_trades": [
                    {
                        "sell": "VTI",
                        "buy": "VOO",
                        "loss": round(random.uniform(500, 5000), 2),
                        "wash_sale_risk": "low",
                    }
                ],
            }
        return {"error": f"Unknown action: {action}"}


class ResearchServer(BaseTool):
    name = "ResearchServer"
    description = "Equity research, analyst ratings, fundamental data, and earnings estimates"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get_research", "get_ratings", "get_fundamentals", "get_earnings"],
            },
            "symbol": {"type": "string"},
        },
    }

    async def validate(self, **kwargs) -> bool:
        return kwargs.get("action") in ("get_research", "get_ratings", "get_fundamentals", "get_earnings")

    async def execute(self, **kwargs) -> dict[str, Any]:
        action = kwargs.get("action", "get_research")
        symbol = kwargs.get("symbol", "AAPL")

        if action == "get_research":
            return {
                "symbol": symbol,
                "company_name": f"{symbol} Corp",
                "sector": "Technology",
                "industry": "Semiconductors" if symbol in ("NVDA", "AMD") else "Software",
                "summary": f"{symbol} shows strong fundamentals with growing revenue and expanding margins. "
                           f"Analysts are bullish on the upcoming product cycle.",
                "rating": random.choice(["Strong Buy", "Buy", "Hold", "Sell"]),
                "target_price": round(random.uniform(150, 300), 2),
                "current_price": round(random.uniform(100, 250), 2),
                "upside_pct": round(random.uniform(-5, 30), 2),
            }
        elif action == "get_ratings":
            return {
                "symbol": symbol,
                "total_analysts": random.randint(25, 55),
                "breakdown": {
                    "strong_buy": random.randint(5, 20),
                    "buy": random.randint(5, 20),
                    "hold": random.randint(2, 10),
                    "sell": random.randint(0, 5),
                    "strong_sell": random.randint(0, 3),
                },
                "consensus": random.choice(["Strong Buy", "Buy", "Hold"]),
                "avg_target": round(random.uniform(150, 300), 2),
                "high_target": round(random.uniform(200, 400), 2),
                "low_target": round(random.uniform(100, 180), 2),
            }
        elif action == "get_fundamentals":
            return {
                "symbol": symbol,
                "market_cap": round(random.uniform(10e9, 3e12), 2),
                "pe_ratio": round(random.uniform(10, 40), 2),
                "forward_pe": round(random.uniform(10, 35), 2),
                "eps": round(random.uniform(1, 15), 2),
                "dividend_yield": round(random.uniform(0, 3.5), 2),
                "revenue_growth": round(random.uniform(-5, 30), 2),
                "profit_margin": round(random.uniform(5, 35), 2),
                "debt_to_equity": round(random.uniform(0, 2), 2),
                "roe": round(random.uniform(10, 50), 2),
            }
        elif action == "get_earnings":
            return {
                "symbol": symbol,
                "fiscal_year": 2024,
                "quarterly": [
                    {"quarter": "Q1", "revenue": round(random.uniform(10e9, 100e9), 2), "eps": round(random.uniform(1, 5), 2), "beat_estimate": random.choice([True, False])},
                    {"quarter": "Q2", "revenue": round(random.uniform(10e9, 100e9), 2), "eps": round(random.uniform(1, 5), 2), "beat_estimate": random.choice([True, False])},
                ],
                "next_report_date": "2024-10-24",
                "estimate_revenue": round(random.uniform(10e9, 100e9), 2),
                "estimate_eps": round(random.uniform(1, 5), 2),
            }
        return {"error": f"Unknown action: {action}"}


class CRMServer(BaseTool):
    name = "CRMServer"
    description = "Client relationship management, profiles, preferences, and interaction history"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get_client", "get_interactions", "get_preferences", "update_client"],
            },
            "client_id": {"type": "string"},
        },
    }

    async def validate(self, **kwargs) -> bool:
        return kwargs.get("action") in ("get_client", "get_interactions", "get_preferences", "update_client")

    async def execute(self, **kwargs) -> dict[str, Any]:
        action = kwargs.get("action", "get_client")
        client_id = kwargs.get("client_id", "CLT-001")

        if action == "get_client":
            return {
                "client_id": client_id,
                "name": f"Client {client_id}",
                "tier": random.choice(["platinum", "gold", "silver", "bronze"]),
                "relationship_manager": "RM-001",
                "account_value": round(random.uniform(100000, 10000000), 2),
                "risk_tolerance": random.choice(["conservative", "moderate", "aggressive"]),
                "investment_goals": ["retirement", "wealth_preservation", "growth"],
                "kyc_status": "verified",
                "onboarding_date": "2023-06-15",
            }
        elif action == "get_interactions":
            return {
                "client_id": client_id,
                "total_interactions": random.randint(10, 200),
                "recent": [
                    {
                        "date": "2024-09-15",
                        "type": "call",
                        "summary": "Discussed portfolio rebalancing",
                        "duration_minutes": 25,
                    },
                    {
                        "date": "2024-09-10",
                        "type": "email",
                        "summary": "Sent quarterly performance report",
                    },
                    {
                        "date": "2024-09-01",
                        "type": "meeting",
                        "summary": "Annual review meeting",
                        "duration_minutes": 60,
                    },
                ],
            }
        elif action == "get_preferences":
            return {
                "client_id": client_id,
                "communication_channel": random.choice(["email", "phone", "portal"]),
                "reporting_frequency": random.choice(["monthly", "quarterly", "annually"]),
                "interest_areas": ["technology", "healthcare", "renewable_energy"],
                "esg_preference": random.choice([True, False]),
                "tax_optimization": True,
            }
        elif action == "update_client":
            return {
                "client_id": client_id,
                "updated": True,
                "fields_modified": kwargs.get("fields", []),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        return {"error": f"Unknown action: {action}"}
