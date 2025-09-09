"""
Stock Selector Component - 간단한 종목 선택
"""
import streamlit as st
from typing import Optional
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.json_client import InvestSmartJSONClient


def render_stock_selector() -> Optional[str]:
    """
    종목 선택 컴포넌트 렌더링
    
    Returns:
        선택된 종목 심볼 또는 None
    """
    try:
        json_client = InvestSmartJSONClient()
        available_symbols = json_client.get_available_symbols()
        
        if not available_symbols:
            st.error("종목 목록을 불러올 수 없습니다.")
            return None
        
        # 종목 선택
        selected_symbol = None
        
        # 원래 종목 목록 복원 (백엔드에서 제공하던 종목들)
        symbol_display_names = {
            "^KS11": "코스피 (KOSPI)",
            "^IXIC": "나스닥 (NASDAQ)",
            "^GSPC": "S&P 500",
            "^DJI": "다우존스",
            "^VIX": "VIX (변동성 지수)",
            "AAPL": "애플 (Apple)",
            "MSFT": "마이크로소프트 (Microsoft)",
            "GOOGL": "구글 (Google)",
            "AMZN": "아마존 (Amazon)",
            "TSLA": "테슬라 (Tesla)",
            "NVDA": "엔비디아 (NVIDIA)",
            "META": "메타 (Meta)",
            "NFLX": "넷플릭스 (Netflix)",
            "AMD": "AMD",
            "INTC": "인텔 (Intel)",
            "CRM": "세일즈포스 (Salesforce)",
            "ADBE": "어도비 (Adobe)",
            "PYPL": "페이팔 (PayPal)",
            "UBER": "우버 (Uber)",
            "SPOT": "스포티파이 (Spotify)",
            "TLT": "TLT (미국 20년 국채)",
            "IEF": "IEF (미국 7-10년 국채)",
            "GLD": "GLD (금 ETF)",
            "SLV": "SLV (은 ETF)",
            "VTI": "VTI (미국 전체 주식 시장)",
            "QQQ": "QQQ (나스닥 100)",
            "SPY": "SPY (S&P 500)",
            "DIA": "DIA (다우존스)",
            "IWM": "IWM (러셀 2000)",
            "EFA": "EFA (선진국 주식)",
            "EEM": "EEM (신흥국 주식)",
            "VEA": "VEA (선진국 주식)",
            "VWO": "VWO (신흥국 주식)",
            "BND": "BND (미국 채권)",
            "AGG": "AGG (미국 채권)",
            "LQD": "LQD (회사채)",
            "HYG": "HYG (고수익 채권)",
            "EMB": "EMB (신흥국 채권)",
            "TIP": "TIP (인플레이션 보호 채권)",
            "SHY": "SHY (단기 채권)",
            "IEF": "IEF (중기 채권)",
            "TLT": "TLT (장기 채권)",
            "USDKRW=X": "USD/KRW 환율",
            "EURUSD=X": "EUR/USD 환율",
            "GBPUSD=X": "GBP/USD 환율",
            "USDJPY=X": "USD/JPY 환율",
            "AUDUSD=X": "AUD/USD 환율",
            "USDCAD=X": "USD/CAD 환율",
            "USDCHF=X": "USD/CHF 환율",
            "NZDUSD=X": "NZD/USD 환율"
        }
        
        # 모든 종목을 선택 가능하게 표시 (데이터 없는 종목은 나중에 경고)
        all_options = []
        all_symbols = []
        
        for symbol, display_name in symbol_display_names.items():
            all_options.append(display_name)
            all_symbols.append(symbol)
        
        if all_options:
            selected_index = st.selectbox(
                "종목을 선택하세요:",
                range(len(all_options)),
                format_func=lambda x: all_options[x],
                key="stock_selector"
            )
            
            if selected_index is not None:
                selected_symbol = all_symbols[selected_index]
        
        return selected_symbol
        
    except Exception as e:
        st.error(f"종목 선택 중 오류가 발생했습니다: {e}")
        return None


def render_simple_stock_selector() -> Optional[str]:
    """
    간단한 종목 선택 (드롭다운)
    """
    try:
        json_client = InvestSmartJSONClient()
        available_symbols = json_client.get_available_symbols()
        
        if not available_symbols:
            st.error("종목 목록을 불러올 수 없습니다.")
            return None
        
        # 원래 종목 목록 복원 (백엔드에서 제공하던 종목들)
        symbol_display_names = {
            "^KS11": "코스피 (KOSPI)",
            "^IXIC": "나스닥 (NASDAQ)",
            "^GSPC": "S&P 500",
            "^DJI": "다우존스",
            "^VIX": "VIX (변동성 지수)",
            "AAPL": "애플 (Apple)",
            "MSFT": "마이크로소프트 (Microsoft)",
            "GOOGL": "구글 (Google)",
            "AMZN": "아마존 (Amazon)",
            "TSLA": "테슬라 (Tesla)",
            "NVDA": "엔비디아 (NVIDIA)",
            "META": "메타 (Meta)",
            "NFLX": "넷플릭스 (Netflix)",
            "AMD": "AMD",
            "INTC": "인텔 (Intel)",
            "CRM": "세일즈포스 (Salesforce)",
            "ADBE": "어도비 (Adobe)",
            "PYPL": "페이팔 (PayPal)",
            "UBER": "우버 (Uber)",
            "SPOT": "스포티파이 (Spotify)",
            "TLT": "TLT (미국 20년 국채)",
            "IEF": "IEF (미국 7-10년 국채)",
            "GLD": "GLD (금 ETF)",
            "SLV": "SLV (은 ETF)",
            "VTI": "VTI (미국 전체 주식 시장)",
            "QQQ": "QQQ (나스닥 100)",
            "SPY": "SPY (S&P 500)",
            "DIA": "DIA (다우존스)",
            "IWM": "러셀 2000",
            "EFA": "EFA (선진국 주식)",
            "EEM": "EEM (신흥국 주식)",
            "VEA": "VEA (선진국 주식)",
            "VWO": "VWO (신흥국 주식)",
            "BND": "BND (미국 채권)",
            "AGG": "AGG (미국 채권)",
            "LQD": "LQD (회사채)",
            "HYG": "HYG (고수익 채권)",
            "EMB": "EMB (신흥국 채권)",
            "TIP": "TIP (인플레이션 보호 채권)",
            "SHY": "SHY (단기 채권)",
            "USDKRW=X": "USD/KRW 환율",
            "EURUSD=X": "EUR/USD 환율",
            "GBPUSD=X": "GBP/USD 환율",
            "USDJPY=X": "USD/JPY 환율",
            "AUDUSD=X": "AUD/USD 환율",
            "USDCAD=X": "USD/CAD 환율",
            "USDCHF=X": "USD/CHF 환율",
            "NZDUSD=X": "NZD/USD 환율"
        }
        
        # 모든 종목을 선택 가능하게 표시 (데이터 없는 종목은 나중에 경고)
        all_options = []
        all_symbols = []
        
        for symbol, display_name in symbol_display_names.items():
            all_options.append(display_name)
            all_symbols.append(symbol)
        
        if not all_options:
            st.error("종목 목록을 불러올 수 없습니다.")
            return None
        
        # 드롭다운으로 선택
        selected_display = st.selectbox(
            "종목 선택",
            all_options,
            help="분석할 종목을 선택하세요."
        )
        
        # 선택된 종목의 심볼 찾기
        for i, display_name in enumerate(all_options):
            if display_name == selected_display:
                return all_symbols[i]
        
        return None
        
    except Exception as e:
        st.error(f"종목 선택 중 오류가 발생했습니다: {e}")
        return None