"""
Streamlit Chart Component - 원본 코드와 동일한 차트 구조
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from utils.json_client import InvestSmartJSONClient

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)  # 5분간 캐시
def get_cached_signals_data(symbol: str, period: str):
    """캐시된 신호 데이터 조회"""
    json_client = InvestSmartJSONClient()
    return json_client.get_signals_data(symbol, period)



def _get_dynamic_annotations(fcv_has_green: bool, fcv_has_red: bool) -> list:
    """FCV 배경 색칠에 따른 동적 설명 생성"""
    annotations = [
        dict(
            x=0.98,
            y=0.98,
            xref='paper',
            yref='paper',
            text="● 국소적 저점",
            showarrow=False,
            font=dict(size=10, color='darkgreen'),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='darkgreen',
            borderwidth=1
        )
    ]
    
    # FCV 배경 색칠 설명 추가
    if fcv_has_green:
        annotations.append(
            dict(
                x=0.98,
                y=0.92,
                xref='paper',
                yref='paper',
                text="🟩 적극매수",
                showarrow=False,
                font=dict(size=10, color='green'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='darkgreen',
                borderwidth=1
            )
        )
    
    if fcv_has_red:
        annotations.append(
            dict(
                x=0.98,
                y=0.86 if fcv_has_green else 0.92,
                xref='paper',
                yref='paper',
                text="🟥 적극매도",
                showarrow=False,
                font=dict(size=10, color='red'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='darkred',
                borderwidth=1
            )
        )
    
    return annotations


def render_stock_chart(
    symbol: str, 
    period: str = "1y",
    settings: Optional[Dict[str, Any]] = None
):
    """
    주식 차트 렌더링 - 캐시된 데이터 사용으로 최적화
    """
    try:
        # 캐시된 데이터 로딩 (JSON 파일에서 직접 읽기)
        with st.spinner(f"{symbol} 데이터를 불러오는 중... 📊 참고용 정보: 제공되는 시그널과 지표는 투자 교육 목적이며, 투자 권유가 아닙니다."):
            # 신호 데이터 조회 (JSON에서 직접 읽기)
            signals_data = get_cached_signals_data(symbol, period)
            
            # 데이터가 없는 경우 체크
            if signals_data.get('error') or not signals_data.get('dates'):
                st.warning(f"⚠️ {symbol} 종목은 아직 지원하지 않는 종목입니다.")
                st.info("현재 지원하는 종목: 코스피, 나스닥, TLT, USD/KRW 환율")
                return
        
        # 차트 생성 (시그널 체크박스 변경 시에는 데이터 재다운로드 없이 차트만 재생성)
        _create_candlestick_chart(
            signals_data, 
            settings
        )
        
    except Exception as e:
        logger.error(f"차트 렌더링 실패: {symbol}, {e}")
        st.error(f"차트를 불러올 수 없습니다: {e}")


def _create_candlestick_chart(
    signals_data: Dict[str, Any],
    settings: Optional[Dict[str, Any]]
):
    """캔들스틱 차트 생성 - 인덱스 오류 방지 및 전체화면 최적화"""
    try:
        # 데이터 추출
        dates = pd.to_datetime(signals_data["dates"])
        open_prices = signals_data["data"]["open"]
        high_prices = signals_data["data"]["high"]
        low_prices = signals_data["data"]["low"]
        close_prices = signals_data["data"]["close"]
        volume = signals_data["data"]["volume"]
        
        # 데이터 길이 검증 및 정렬 (인덱스 오류 방지)
        min_length = min(len(dates), len(open_prices), len(high_prices), len(low_prices), len(close_prices))
        if min_length == 0:
            st.error("데이터가 없습니다.")
            return
            
        # 모든 데이터를 동일한 길이로 맞춤
        dates = dates[:min_length]
        open_prices = open_prices[:min_length]
        high_prices = high_prices[:min_length]
        low_prices = low_prices[:min_length]
        close_prices = close_prices[:min_length]
        
        # 단일 차트 생성 (FCV 서브차트 제거)
        fig = go.Figure()
        
        # FCV 배경 표시 (0.5 이상, -0.5 이하 구간)
        if signals_data.get("indicators") and 'Final_Composite_Value' in signals_data["indicators"]:
            fcv_values = signals_data["indicators"]['Final_Composite_Value']
            
            # FCV 값에 따른 배경 색상 설정
            for i in range(min_length - 1):
                if i < len(fcv_values) - 1:
                    current_fcv = fcv_values[i]
                    next_fcv = fcv_values[i + 1]
                    
                    # 0.5 이상 구간 (초록 배경)
                    if current_fcv >= 0.5 or next_fcv >= 0.5:
                        fig.add_shape(
                            type="rect",
                            x0=dates[i], x1=dates[i + 1],
                            y0=min(low_prices), y1=max(high_prices),
                            fillcolor="rgba(0, 255, 0, 0.1)",
                            line=dict(width=0),
                            layer="below"
                        )
                    
                    # -0.5 이하 구간 (빨강 배경)
                    elif current_fcv <= -0.5 or next_fcv <= -0.5:
                        fig.add_shape(
                            type="rect",
                            x0=dates[i], x1=dates[i + 1],
                            y0=min(low_prices), y1=max(high_prices),
                            fillcolor="rgba(255, 0, 0, 0.1)",
                            line=dict(width=0),
                            layer="below"
                        )
        
        # 캔들스틱 차트 (메인 차트)
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=open_prices,
                high=high_prices,
                low=low_prices,
                close=close_prices,
                name="주가",
                increasing_line_color='red',
                decreasing_line_color='blue'
            )
        )
        
        # 추세선 추가 (JSON 데이터에서 읽어오기)
        if signals_data.get("trendlines"):
            trendlines = signals_data["trendlines"]
            for trendline in trendlines:
                points = trendline.get("points", [])
                if len(points) >= 2:
                    trendline_dates = [pd.to_datetime(p["date"]) for p in points]
                    trendline_prices = [p["price"] for p in points]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=trendline_dates,
                            y=trendline_prices,
                            name=trendline["name"],
                            line=dict(
                                color=trendline["color"],
                                width=2,
                                dash="dash"
                            ),
                            mode="lines"
                        )
                    )
        
        # 시그널 표시 (원본 코드와 정확히 동일 + 색깔 구분)
        if settings and settings.get('selected_signals') and signals_data.get("signals"):
            signals = signals_data["signals"]
            show_buy_signals = settings.get('show_buy_signals', True)
            show_sell_signals = settings.get('show_sell_signals', True)
            
            # 시그널별 색깔 및 스타일 정의 (매수 신호: 가로 삼각형, 반전 신호: 세로 삼각형)
            signal_styles = {
                'short_signal_v2': {
                    'buy': {'color': '#00FFFF', 'size': 8, 'opacity': 0.8, 'line_width': 2, 'label': 'SHORT', 'symbol': 'circle'},
                    'sell': {'color': '#FF4444', 'size': 12, 'opacity': 0.8, 'line_width': 2, 'label': 'SHORT', 'symbol': 'triangle-left'}
                },
                'macd_signal': {
                    'buy': {'color': '#FFD700', 'size': 16, 'opacity': 0.85, 'line_width': 2, 'label': 'SHORT', 'symbol': 'triangle-up'},
                    'sell': {'color': '#FF6666', 'size': 16, 'opacity': 0.85, 'line_width': 2, 'label': 'SHORT', 'symbol': 'triangle-down'}
                },
                'short_signal_v1': {
                    'buy': {'color': '#32CD32', 'size': 9, 'opacity': 0.8, 'line_width': 2, 'label': 'MID', 'symbol': 'circle'},
                    'sell': {'color': '#FF7777', 'size': 13, 'opacity': 0.8, 'line_width': 2, 'label': 'MID', 'symbol': 'triangle-left'}
                },
                'momentum_color_signal': {
                    'buy': {'color': '#FF69B4', 'size': 17, 'opacity': 0.85, 'line_width': 2, 'label': 'MID', 'symbol': 'triangle-up'},
                    'sell': {'color': '#FF8888', 'size': 17, 'opacity': 0.85, 'line_width': 2, 'label': 'MID', 'symbol': 'triangle-down'}
                },
                'long_signal': {
                    'buy': {'color': '#4169E1', 'size': 10, 'opacity': 0.8, 'line_width': 2, 'label': 'LONG', 'symbol': 'circle'},
                    'sell': {'color': '#FF9999', 'size': 14, 'opacity': 0.8, 'line_width': 2, 'label': 'LONG', 'symbol': 'triangle-left'}
                },
                'combined_signal_v1': {
                    'buy': {'color': '#FF8C00', 'size': 15, 'opacity': 0.85, 'line_width': 2, 'label': 'LONG', 'symbol': 'triangle-up'},
                    'sell': {'color': '#FFAAAA', 'size': 15, 'opacity': 0.85, 'line_width': 2, 'label': 'LONG', 'symbol': 'triangle-down'}
                }
            }
            
            for signal_name in settings['selected_signals']:
                if signal_name in signals:
                    signal_values = signals[signal_name]
                    signal_style = signal_styles.get(signal_name, {'buy': {'color': '#00FF00', 'size': 14, 'opacity': 0.8, 'line_width': 2, 'label': 'SIGNAL', 'symbol': 'triangle-up'}, 'sell': {'color': '#FF0000', 'size': 14, 'opacity': 0.8, 'line_width': 2, 'label': 'SIGNAL', 'symbol': 'triangle-down'}})
                    
                    # 매수 신호 표시 (인덱스 오류 방지) - FCV 제외
                    if show_buy_signals and signal_name != 'fcv_signal':
                        buy_signals = []
                        
                        # 주봉 기준 신호는 해당 주의 첫 번째 신호만 표시
                        if signal_name in ['momentum_color_signal']:
                            # 주별로 그룹화하여 각 주의 첫 번째 신호만 표시
                            weekly_signals = {}
                            for i, signal in enumerate(signal_values):
                                if i < min_length and signal == 1:  # 인덱스 범위 체크
                                    # 해당 날짜의 주 시작일(월요일) 계산
                                    week_start = dates[i] - pd.Timedelta(days=dates[i].weekday())
                                    week_key = week_start.strftime('%Y-%W')
                                    
                                    # 해당 주에 아직 신호가 없으면 추가
                                    if week_key not in weekly_signals:
                                        weekly_signals[week_key] = (dates[i], low_prices[i] * 0.99)
                            
                            # 각 주의 첫 번째 신호만 추가
                            buy_signals = list(weekly_signals.values())
                        else:
                            # 일반 신호는 모든 날짜에 표시
                            for i, signal in enumerate(signal_values):
                                if i < min_length and signal == 1:  # 인덱스 범위 체크
                                    buy_signals.append((dates[i], low_prices[i] * 0.97))
                        
                        # 반전 시그널에 대한 BUY! 텍스트 표시
                        reversal_signals = ['macd_signal', 'momentum_color_signal', 'combined_signal_v1']
                        if signal_name in reversal_signals:
                            # 해당 그룹의 매수 시그널 찾기
                            group_buy_signals = []
                            if signal_name == 'macd_signal':
                                group_buy_signals = ['short_signal_v2']  # 단기 그룹
                            elif signal_name == 'momentum_color_signal':
                                group_buy_signals = ['short_signal_v1']  # 중기 그룹
                            elif signal_name == 'combined_signal_v1':
                                group_buy_signals = ['long_signal']  # 장기 그룹
                            
                            buy_text_signals = []
                            if signal_name == 'momentum_color_signal':
                                # 중기 추세전환은 주별로 첫 번째 BUY!만 표시
                                weekly_buy_texts = {}
                                for i, signal in enumerate(signal_values):
                                    if i < min_length and signal == 1:  # 반전 시그널이 있는 경우
                                        # 최근 50개 데이터에서 해당 그룹의 매수 시그널 확인 (중기)
                                        start_idx = max(0, i - 50)
                                        
                                        # 해당 그룹의 매수 시그널이 있는지 확인
                                        has_buy_signal = False
                                        for group_signal in group_buy_signals:
                                            if group_signal in signals:
                                                group_values = signals[group_signal]
                                                if len(group_values) > i:
                                                    recent_group_signals = group_values[start_idx:i]
                                                    if 1 in recent_group_signals:
                                                        has_buy_signal = True
                                                        break
                                        
                                        # 매수 시그널이 있었으면 해당 주의 첫 번째 BUY!만 추가
                                        if has_buy_signal:
                                            week_start = dates[i] - pd.Timedelta(days=dates[i].weekday())
                                            week_key = week_start.strftime('%Y-%W')
                                            if week_key not in weekly_buy_texts:
                                                weekly_buy_texts[week_key] = (dates[i], low_prices[i] * 0.95)  # 위치 올림
                                
                                buy_text_signals = list(weekly_buy_texts.values())
                            else:
                                # 단기/장기는 모든 BUY! 표시
                                for i, signal in enumerate(signal_values):
                                    if i < min_length and signal == 1:  # 반전 시그널이 있는 경우
                                        # 최근 20개 데이터에서 해당 그룹의 매수 시그널 확인
                                        start_idx = max(0, i - 20)
                                        
                                        # 해당 그룹의 매수 시그널이 있는지 확인
                                        has_buy_signal = False
                                        for group_signal in group_buy_signals:
                                            if group_signal in signals:
                                                group_values = signals[group_signal]
                                                if len(group_values) > i:
                                                    recent_group_signals = group_values[start_idx:i]
                                                    if 1 in recent_group_signals:
                                                        has_buy_signal = True
                                                        break
                                        
                                        # 매수 시그널이 있었으면 BUY! 텍스트 추가
                                        if has_buy_signal:
                                            buy_text_signals.append((dates[i], low_prices[i] * 0.95))  # 위치 올림
                            
                            # BUY! 텍스트 표시
                            if buy_text_signals:
                                text_dates, text_prices = zip(*buy_text_signals)
                                fig.add_trace(
                                    go.Scatter(
                                        x=text_dates,
                                        y=text_prices,
                                        mode='text',
                                        text=['BUY!!'] * len(text_dates),
                                        textposition='middle center',
                                        textfont=dict(
                                            color='red',
                                            size=14,
                                            family='Arial Black'
                                        ),
                                        name=f'{signal_style["buy"]["label"]} BUY!!',
                                        showlegend=False
                                    )
                                )
                        
                        if buy_signals:
                            buy_dates, buy_prices = zip(*buy_signals)
                            
                            # 매수 신호 표시 (가로 삼각형)
                            fig.add_trace(
                                go.Scatter(
                                    x=buy_dates,
                                    y=buy_prices,
                                    mode='markers',
                                    marker=dict(
                                        symbol=signal_style['buy']['symbol'],
                                        size=signal_style['buy']['size'],
                                        color=signal_style['buy']['color'],
                                        opacity=signal_style['buy']['opacity'],
                                        line=dict(width=signal_style['buy']['line_width'], color='darkgreen')
                                    ),
                                    name=f'{signal_style["buy"]["label"]} BUY'
                                )
                            )
                            
                            # low point 텍스트는 제거 (우측 상단에 설명으로 대체)
                    
                    
                    # 매도 신호 표시 (인덱스 오류 방지) - 일시적으로 비활성화
                    # if show_sell_signals:
                    #     sell_signals = []
                    #     for i, signal in enumerate(signal_values):
                    #         if i < min_length and signal == -1:  # 인덱스 범위 체크
                    #             sell_signals.append((dates[i], high_prices[i] * 1.02))
                    #     
                    #     if sell_signals:
                    #         sell_dates, sell_prices = zip(*sell_signals)
                    #         fig.add_trace(
                    #             go.Scatter(
                    #                 x=sell_dates,
                    #                 y=sell_prices,
                    #                 mode='markers',
                    #                 marker=dict(
                    #                     symbol=signal_style['sell']['symbol'],
                    #                     size=signal_style['sell']['size'],
                    #                     color=signal_style['sell']['color'],
                    #                     opacity=signal_style['sell']['opacity'],
                    #                     line=dict(width=signal_style['sell']['line_width'], color='darkred')
                    #                 ),
                    #                 name=f'{signal_style["sell"]["label"]} SELL'
                    #             )
                    #         )
        
        
        # FCV 배경 색칠 (단기중기장기 무관하게 배경에 색칠)
        fcv_has_green = False
        fcv_has_red = False
        
        if signals_data.get("indicators") and "Final_Composite_Value" in signals_data["indicators"]:
            fcv_values = signals_data["indicators"]["Final_Composite_Value"]
            if len(fcv_values) > 0:
                # FCV >= 0.5: 녹색 배경, FCV <= -0.5: 빨간색 배경
                for i in range(min(len(fcv_values), min_length)):
                    fcv_val = fcv_values[i]
                    if fcv_val >= 0.5:
                        fcv_has_green = True
                        # 녹색 배경
                        fig.add_shape(
                            type="rect",
                            x0=dates[i], x1=dates[i+1] if i+1 < len(dates) else dates[i],
                            y0=0, y1=1,
                            yref="paper",
                            fillcolor="rgba(0, 255, 0, 0.1)",
                            line=dict(width=0)
                        )
                    elif fcv_val <= -0.5:
                        fcv_has_red = True
                        # 빨간색 배경
                        fig.add_shape(
                            type="rect",
                            x0=dates[i], x1=dates[i+1] if i+1 < len(dates) else dates[i],
                            y0=0, y1=1,
                            yref="paper",
                            fillcolor="rgba(255, 0, 0, 0.1)",
                            line=dict(width=0)
                        )
        
        # 차트 레이아웃 설정 (전체화면 최적화 + 인터랙티브 제한)
        fig.update_layout(
            title="",  # 제목 제거
            xaxis_rangeslider_visible=False,
            height=500,  # 전체화면에 맞는 높이 (FCV 서브차트 제거로 더 크게)
            showlegend=False,  # 범례 제거로 공간 확보
            template="plotly_white",
            margin=dict(l=2, r=2, t=15, b=2),  # 여백 극소화
            font=dict(size=9),  # 폰트 크기 더 축소
            plot_bgcolor='white',
            paper_bgcolor='white',
            # 인터랙티브 기능 제한
            dragmode=False,  # 드래그 비활성화
            hovermode=False,  # 호버 툴팁 완전 비활성화
            # 우측 상단에 시그널 설명 추가 (동적)
            annotations=_get_dynamic_annotations(fcv_has_green, fcv_has_red),
            # 줌/팬 비활성화
            xaxis=dict(
                fixedrange=True,  # X축 고정
                showspikes=False,  # 스파이크 제거
                spikemode='across',
                spikecolor='grey',
                spikesnap='cursor',
                spikethickness=1
            ),
            yaxis=dict(
                fixedrange=True,  # Y축 고정
                showspikes=False,  # 스파이크 제거
                spikemode='across',
                spikecolor='grey',
                spikesnap='cursor',
                spikethickness=1
            )
        )
        
        # Y축 설정 (제목 제거로 공간 확보 + 인터랙티브 제한)
        fig.update_yaxes(
            title_text="", 
            fixedrange=True,  # 주가 축 고정
            showspikes=False
        )
        
        # 차트 표시
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"캔들스틱 차트 생성 실패: {e}")
        st.error(f"차트 생성 중 오류가 발생했습니다: {e}")