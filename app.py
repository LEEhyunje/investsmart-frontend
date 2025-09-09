"""
Streamlit Main App - 원본 코드와 동일한 단순한 차트 화면 (탭 없음)
"""
import streamlit as st
import sys
import os
import logging
from typing import Dict, Any, Optional

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 페이지 설정 (모바일 최적화)
st.set_page_config(
    page_title="InvestSmart",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"  # 모바일에서 사이드바 기본 접힘
)

# 컴포넌트 import
from components.stock_selector import render_simple_stock_selector
from utils.json_client import InvestSmartJSONClient
from components.chart import render_stock_chart

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def render_disclaimer():
    """면책조항 표시 - 처음 체크하면 아예 없어짐"""
    if 'disclaimer_agreed' not in st.session_state:
        st.session_state.disclaimer_agreed = False
    
    if not st.session_state.disclaimer_agreed:
        with st.expander("⚠️ 투자 주의사항", expanded=True):
            st.markdown("""
            **📋 서비스 성격**
            - 본 서비스는 **투자 교육 및 정보 제공** 목적으로 제작되었습니다
            - 기술적 분석 도구와 시장 정보를 제공하는 **학습 플랫폼**입니다
            
            **⚠️ 투자 위험 고지**
            - **모든 투자에는 원금 손실 위험이 있습니다**
            - 과거 성과가 미래 수익을 보장하지 않습니다
            - 제공되는 정보는 투자 권유가 아닙니다
            
            **📊 제공 정보의 한계**
            - 기술적 지표와 시그널은 참고용 정보입니다
            - 시장 상황에 따라 정확도가 달라질 수 있습니다
            - 모든 투자 결정은 **본인의 판단과 책임**입니다
            
            **🔒 면책사항**
            - 본 서비스 이용으로 인한 투자 손실에 대해 책임지지 않습니다
            - 제공되는 정보의 정확성을 보장하지 않습니다
            - 투자 전 충분한 검토와 전문가 상담을 권장합니다
            """)
            
            agreed = st.checkbox(
                "위 내용을 충분히 이해했으며, 투자 위험을 인지합니다", 
                key="disclaimer_checkbox"
            )
            
            if agreed:
                st.session_state.disclaimer_agreed = True
                st.rerun()
            else:
                st.warning("⚠️ 위험 고지사항에 동의해야 서비스를 이용할 수 있습니다.")
                st.stop()

def get_json_client() -> InvestSmartJSONClient:
    """JSON 클라이언트 인스턴스 반환"""
    if 'json_client' not in st.session_state:
        st.session_state.json_client = InvestSmartJSONClient()
    return st.session_state.json_client


def test_json_connection() -> bool:
    """JSON 파일 연결 테스트"""
    try:
        client = get_json_client()
        # 간단한 데이터 확인
        info = client.get_data_info()
        return info['total_records'] > 0
    except Exception as e:
        logger.error(f"JSON 파일 연결 실패: {e}")
        return False

def main():
    """주식 분석 메인 페이지 - 단계별 사용자 인터페이스"""
    # JSON 파일 연결 테스트
    if not test_json_connection():
        st.error("🚨 신호 데이터 파일을 찾을 수 없습니다. signals_data.json 파일이 있는지 확인해주세요.")
        st.stop()
    
    # 면책조항 표시 (메인 페이지 상단)
    render_disclaimer()
    
    # 세션 상태 초기화
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'selected_symbol' not in st.session_state:
        st.session_state.selected_symbol = None
    if 'selected_indicator_group' not in st.session_state:
        st.session_state.selected_indicator_group = None
    
    # 단계별 인터페이스
    if st.session_state.step == 1:
        render_step1_symbol_selection()
    elif st.session_state.step == 2:
        render_step2_indicator_selection()
    elif st.session_state.step == 3:
        render_step3_chart_display()


def render_step1_symbol_selection():
    """1단계: 종목 선택"""
    st.title("📈 InvestSmart - 종목 분석")
    st.markdown("### 1단계: 궁금한 종목(혹은 지수)는?")
    
    # 종목 선택
    symbol = render_simple_stock_selector()
    
    if symbol:
        st.session_state.selected_symbol = symbol
        st.success(f"✅ 선택된 종목: **{symbol}**")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("다음 단계", type="primary", use_container_width=True):
                st.session_state.step = 2
                st.rerun()


def render_step2_indicator_selection():
    """2단계: 지표 그룹 선택"""
    st.title("📈 InvestSmart - 지표 분석")
    st.markdown("### 2단계: 궁금한 지표는?")
    
    # 이전 단계로 돌아가기
    if st.button("← 이전 단계"):
        st.session_state.step = 1
        st.rerun()
    
    st.info(f"선택된 종목: **{st.session_state.selected_symbol}**")
    
    # 지표 그룹 선택
    indicator_groups = {
        "단기": {
            "description": "단기 트레이딩용 지표",
            "signals": ["short_signal_v2", "macd_signal"],
            "color": "#00FFFF"
        },
        "중기": {
            "description": "중기 투자용 지표", 
            "signals": ["short_signal_v1", "momentum_color_signal"],
            "color": "#32CD32"
        },
        "장기": {
            "description": "장기 투자용 지표",
            "signals": ["long_signal", "combined_signal_v1"],
            "color": "#4169E1"
        }
    }
    
    # 지표 그룹 선택 버튼들
    cols = st.columns(3)
    for i, (group_name, group_info) in enumerate(indicator_groups.items()):
        with cols[i]:
            st.markdown(f"### {group_name}")
            st.markdown(f"*{group_info['description']}*")
            
            if st.button(
                f"{group_name} 선택", 
                key=f"group_{group_name}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.selected_indicator_group = group_name
                st.session_state.selected_signals = group_info['signals']
                st.session_state.step = 3
                st.rerun()


def render_step3_chart_display():
    """3단계: 차트만 표시"""
    # 이전 단계로 돌아가기 버튼만 표시
    if st.button("← 이전 단계"):
        st.session_state.step = 2
        st.rerun()
    
    # 차트 표시 설정
    settings = {
        'selected_signals': st.session_state.selected_signals,
        'show_buy_signals': True,
        'show_sell_signals': True,
        'show_trendlines': True,
        'selected_indicators': []
    }
    
    # 차트 렌더링 (3년 기본 기간) - 차트만 표시
    render_stock_chart(st.session_state.selected_symbol, "3y", settings)

if __name__ == "__main__":
    main()