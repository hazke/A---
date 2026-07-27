"""Collect live market perception data via akshare."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Tuple

from core.perception.schemas import (
    CapitalFlowBucket,
    CapitalFlowData,
    FieldStatus,
    GlobalContextData,
    GlobalTicker,
    LivePerception,
    MarketData,
    QualityFlag,
    SectorItem,
    SectorThemeData,
)
from core.config_manager import ConfigManager
from core.perception.helpers import (
    flag,
    missing_metric,
    ok_metric,
    pick_row,
    safe_float,
    summarize_quality,
    utc_now,
)


DEFAULT_SECTORS = [
    {"code": "BK0447", "name": "通信设备"},
    {"code": "BK0448", "name": "计算机设备"},
    {"code": "BK1036", "name": "半导体"},
    {"code": "BK0800", "name": "人工智能"},
]

DEFAULT_ETFS = [
    {"code": "588000", "name": "科创50ETF"},
    {"code": "515050", "name": "5G通信ETF"},
    {"code": "512760", "name": "芯片ETF"},
]

DEFAULT_GLOBAL_TICKERS = [
    {"symbol": "NVDA", "name": "英伟达"},
    {"symbol": "SOXX", "name": "半导体ETF"},
    {"symbol": "QQQ", "name": "纳指100ETF"},
]


class PerceptionIngestor:
    """Fetch and normalize Stage-01 perception fields."""

    def __init__(self):
        config = ConfigManager()
        self.default_symbol = config.get("agenticq.default_symbol", "601138")
        self.freshness_sla_seconds = int(
            config.get("agenticq.perception.freshness_sla_seconds", 120)
        )
        self.sector_watchlist = config.get(
            "agenticq.perception.sectors", DEFAULT_SECTORS
        )
        self.etf_watchlist = config.get("agenticq.perception.etfs", DEFAULT_ETFS)
        self.global_watchlist = config.get(
            "agenticq.perception.global_tickers", DEFAULT_GLOBAL_TICKERS
        )

    def collect(self, symbol: Optional[str] = None) -> LivePerception:
        symbol = (symbol or self.default_symbol).replace(".SH", "").replace(".SZ", "")
        collected_at = utc_now()
        flags: List[QualityFlag] = []

        market, market_flags = self._collect_market(symbol, collected_at)
        flags.extend(market_flags)

        capital_flow, flow_flags = self._collect_capital_flow(symbol, collected_at)
        flags.extend(flow_flags)

        sector_theme, sector_flags = self._collect_sector_theme(collected_at)
        flags.extend(sector_flags)

        global_context, global_flags = self._collect_global_context(collected_at)
        flags.extend(global_flags)

        quality = summarize_quality(flags, freshness_sla_seconds=self.freshness_sla_seconds)

        return LivePerception(
            symbol=symbol,
            collected_at=collected_at,
            market=market,
            capital_flow=capital_flow,
            sector_theme=sector_theme,
            global_context=global_context,
            quality=quality,
        )

    def _collect_market(
        self, symbol: str, collected_at: datetime
    ) -> Tuple[MarketData, List[QualityFlag]]:
        flags: List[QualityFlag] = []
        market = MarketData(symbol=symbol, as_of=collected_at)

        try:
            import akshare as ak
        except ImportError:
            flags.append(
                flag(
                    "market",
                    FieldStatus.MISSING,
                    message="akshare is not installed",
                    source="akshare",
                )
            )
            return market, flags

        try:
            spot_df = ak.stock_zh_a_spot_em()
            row = pick_row(spot_df, "代码", symbol)
            if row is None:
                flags.append(
                    flag(
                        "market.last_price",
                        FieldStatus.MISSING,
                        message=f"symbol {symbol} not found in spot feed",
                        source="akshare.stock_zh_a_spot_em",
                    )
                )
                return market, flags

            market.name = str(row.get("名称", "")) or None
            as_of = collected_at

            def metric_from_row(field_path: str, column: str, unit: Optional[str] = None):
                value = safe_float(row.get(column))
                if value is None:
                    flags.append(
                        flag(
                            field_path,
                            FieldStatus.MISSING,
                            message=f"{column} unavailable",
                            source="akshare.stock_zh_a_spot_em",
                            observed_at=as_of,
                        )
                    )
                    return missing_metric()
                return ok_metric(value, unit=unit, as_of=as_of)

            market.last_price = metric_from_row("market.last_price", "最新价", "CNY")
            market.open = metric_from_row("market.open", "今开", "CNY")
            market.high = metric_from_row("market.high", "最高", "CNY")
            market.low = metric_from_row("market.low", "最低", "CNY")
            market.prev_close = metric_from_row("market.prev_close", "昨收", "CNY")
            market.change_pct = metric_from_row("market.change_pct", "涨跌幅", "%")
            market.volume = metric_from_row("market.volume", "成交量", "shares")
            market.amount = metric_from_row("market.amount", "成交额", "CNY")
            market.turnover_rate = metric_from_row("market.turnover_rate", "换手率", "%")

            # VWAP and L2 are not in the free spot feed — mark explicitly.
            flags.append(
                flag(
                    "market.vwap",
                    FieldStatus.MISSING,
                    message="VWAP requires intraday/L2 feed (not in spot API)",
                    source="akshare.stock_zh_a_spot_em",
                    observed_at=as_of,
                )
            )
            market.vwap = missing_metric()

            flags.append(
                flag(
                    "market.bid_ask_spread",
                    FieldStatus.MISSING,
                    message="Bid-ask spread requires Level-2 feed",
                    source="perception",
                    observed_at=as_of,
                )
            )
            market.bid_ask_spread = missing_metric()

        except Exception as exc:
            flags.append(
                flag(
                    "market",
                    FieldStatus.MISSING,
                    message=str(exc),
                    source="akshare.stock_zh_a_spot_em",
                    observed_at=collected_at,
                )
            )

        return market, flags

    def _collect_capital_flow(
        self, symbol: str, collected_at: datetime
    ) -> Tuple[CapitalFlowData, List[QualityFlag]]:
        flags: List[QualityFlag] = []
        flow = CapitalFlowData(as_of=collected_at)

        try:
            import akshare as ak
        except ImportError:
            flags.append(
                flag(
                    "capital_flow",
                    FieldStatus.MISSING,
                    message="akshare is not installed",
                    source="akshare",
                )
            )
            return flow, flags

        market_prefix = "sh" if symbol.startswith("6") else "sz"
        try:
            flow_df = ak.stock_individual_fund_flow(stock=symbol, market=market_prefix)
            if flow_df is None or flow_df.empty:
                flags.append(
                    flag(
                        "capital_flow",
                        FieldStatus.MISSING,
                        message="fund flow feed returned empty",
                        source="akshare.stock_individual_fund_flow",
                        observed_at=collected_at,
                    )
                )
                return flow, flags

            latest = flow_df.iloc[-1]
            as_of = collected_at

            mapping = {
                "main": "主力净流入-净额",
                "super_large": "超大单净流入-净额",
                "large": "大单净流入-净额",
                "medium": "中单净流入-净额",
                "small": "小单净流入-净额",
            }

            for bucket_name, column in mapping.items():
                value = safe_float(latest.get(column))
                bucket = CapitalFlowBucket()
                field_path = f"capital_flow.{bucket_name}.net_inflow"
                if value is None:
                    flags.append(
                        flag(
                            field_path,
                            FieldStatus.MISSING,
                            message=f"{column} unavailable",
                            source="akshare.stock_individual_fund_flow",
                            observed_at=as_of,
                        )
                    )
                    bucket.net_inflow = missing_metric()
                else:
                    bucket.net_inflow = ok_metric(value, unit="CNY", as_of=as_of)
                setattr(flow, bucket_name, bucket)

        except Exception as exc:
            flags.append(
                flag(
                    "capital_flow",
                    FieldStatus.MISSING,
                    message=str(exc),
                    source="akshare.stock_individual_fund_flow",
                    observed_at=collected_at,
                )
            )

        return flow, flags

    def _collect_sector_theme(
        self, collected_at: datetime
    ) -> Tuple[SectorThemeData, List[QualityFlag]]:
        flags: List[QualityFlag] = []
        sector_theme = SectorThemeData(as_of=collected_at)

        try:
            import akshare as ak
        except ImportError:
            flags.append(
                flag(
                    "sector_theme",
                    FieldStatus.MISSING,
                    message="akshare is not installed",
                    source="akshare",
                )
            )
            return sector_theme, flags

        try:
            board_df = ak.stock_board_industry_name_em()
            for item in self.sector_watchlist:
                row = pick_row(board_df, "板块名称", item["name"])
                if row is None:
                    row = pick_row(board_df, "板块代码", item["code"])
                change_pct = missing_metric()
                if row is not None:
                    value = safe_float(row.get("涨跌幅"))
                    if value is not None:
                        change_pct = ok_metric(value, unit="%", as_of=collected_at)
                    else:
                        flags.append(
                            flag(
                                f"sector_theme.sectors.{item['code']}.change_pct",
                                FieldStatus.MISSING,
                                message="sector change_pct unavailable",
                                source="akshare.stock_board_industry_name_em",
                                observed_at=collected_at,
                            )
                        )
                else:
                    flags.append(
                        flag(
                            f"sector_theme.sectors.{item['code']}",
                            FieldStatus.MISSING,
                            message=f"sector {item['name']} not found",
                            source="akshare.stock_board_industry_name_em",
                            observed_at=collected_at,
                        )
                    )
                sector_theme.sectors.append(
                    SectorItem(code=item["code"], name=item["name"], change_pct=change_pct)
                )
        except Exception as exc:
            flags.append(
                flag(
                    "sector_theme.sectors",
                    FieldStatus.MISSING,
                    message=str(exc),
                    source="akshare.stock_board_industry_name_em",
                    observed_at=collected_at,
                )
            )

        try:
            import akshare as ak

            etf_df = ak.fund_etf_spot_em()
            for item in self.etf_watchlist:
                row = pick_row(etf_df, "代码", item["code"])
                change_pct = missing_metric()
                if row is not None:
                    value = safe_float(row.get("涨跌幅"))
                    if value is not None:
                        change_pct = ok_metric(value, unit="%", as_of=collected_at)
                    else:
                        flags.append(
                            flag(
                                f"sector_theme.etfs.{item['code']}.change_pct",
                                FieldStatus.MISSING,
                                message="ETF change_pct unavailable",
                                source="akshare.fund_etf_spot_em",
                                observed_at=collected_at,
                            )
                        )
                else:
                    flags.append(
                        flag(
                            f"sector_theme.etfs.{item['code']}",
                            FieldStatus.MISSING,
                            message=f"ETF {item['name']} not found",
                            source="akshare.fund_etf_spot_em",
                            observed_at=collected_at,
                        )
                    )
                sector_theme.etfs.append(
                    SectorItem(code=item["code"], name=item["name"], change_pct=change_pct)
                )
        except Exception as exc:
            flags.append(
                flag(
                    "sector_theme.etfs",
                    FieldStatus.MISSING,
                    message=str(exc),
                    source="akshare.fund_etf_spot_em",
                    observed_at=collected_at,
                )
            )

        return sector_theme, flags

    def _collect_global_context(
        self, collected_at: datetime
    ) -> Tuple[GlobalContextData, List[QualityFlag]]:
        flags: List[QualityFlag] = []
        global_context = GlobalContextData(as_of=collected_at)

        try:
            import akshare as ak
        except ImportError:
            flags.append(
                flag(
                    "global_context",
                    FieldStatus.MISSING,
                    message="akshare is not installed",
                    source="akshare",
                )
            )
            return global_context, flags

        try:
            us_df = ak.stock_us_spot_em()
            for item in self.global_watchlist:
                row = None
                if us_df is not None and not us_df.empty:
                    if "代码" in us_df.columns:
                        row = pick_row(us_df, "代码", item["symbol"])
                    if row is None and "名称" in us_df.columns:
                        row = pick_row(us_df, "名称", item["name"])

                last_price = missing_metric()
                change_pct = missing_metric()
                if row is not None:
                    price_val = safe_float(row.get("最新价"))
                    change_val = safe_float(row.get("涨跌幅"))
                    if price_val is not None:
                        last_price = ok_metric(price_val, unit="USD", as_of=collected_at)
                    else:
                        flags.append(
                            flag(
                                f"global_context.{item['symbol']}.last_price",
                                FieldStatus.MISSING,
                                message="global last_price unavailable",
                                source="akshare.stock_us_spot_em",
                                observed_at=collected_at,
                            )
                        )
                    if change_val is not None:
                        change_pct = ok_metric(change_val, unit="%", as_of=collected_at)
                    else:
                        flags.append(
                            flag(
                                f"global_context.{item['symbol']}.change_pct",
                                FieldStatus.MISSING,
                                message="global change_pct unavailable",
                                source="akshare.stock_us_spot_em",
                                observed_at=collected_at,
                            )
                        )
                else:
                    flags.append(
                        flag(
                            f"global_context.{item['symbol']}",
                            FieldStatus.MISSING,
                            message=f"ticker {item['symbol']} not found",
                            source="akshare.stock_us_spot_em",
                            observed_at=collected_at,
                        )
                    )

                global_context.tickers.append(
                    GlobalTicker(
                        symbol=item["symbol"],
                        name=item["name"],
                        last_price=last_price,
                        change_pct=change_pct,
                    )
                )
        except Exception as exc:
            flags.append(
                flag(
                    "global_context",
                    FieldStatus.MISSING,
                    message=str(exc),
                    source="akshare.stock_us_spot_em",
                    observed_at=collected_at,
                )
            )
            for item in self.global_watchlist:
                global_context.tickers.append(
                    GlobalTicker(
                        symbol=item["symbol"],
                        name=item["name"],
                        last_price=missing_metric(),
                        change_pct=missing_metric(),
                    )
                )

        return global_context, flags
