"""
JSON 데이터 클라이언트
JSON 파일에서 직접 데이터를 읽어오는 간단한 클라이언트
"""
import json
import streamlit as st
from typing import Dict, List, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class InvestSmartJSONClient:
    """InvestSmart JSON 데이터 클라이언트"""
    
    def __init__(self, json_file_path: str = "signals_data.json"):
        self.json_file_path = json_file_path
        self.data = self._load_json_data()
    
    def _load_json_data(self) -> List[Dict]:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"JSON 파일 로드 실패: {e}")
            return []
    
    def get_signals_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """특정 종목의 신호 데이터 조회"""
        try:
            # 특정 종목 데이터 필터링
            symbol_data = [item for item in self.data if item.get('symbol') == symbol]
            
            if not symbol_data:
                return {
                    'symbol': symbol,
                    'dates': [],
                    'signals': {},
                    'indicators': {},
                    'error': '데이터를 찾을 수 없습니다'
                }
            
            # 데이터 구조화
            dates = [item['date'] for item in symbol_data]
            
            # 주가 데이터
            stock_data = {
                'open': [item.get('open', 0) for item in symbol_data],
                'high': [item.get('high', 0) for item in symbol_data],
                'low': [item.get('low', 0) for item in symbol_data],
                'close': [item.get('close', 0) for item in symbol_data],
                'volume': [item.get('volume', 0) for item in symbol_data]
            }
            
            # 신호 데이터
            signals_data = {
                'short_signal_v1': [item.get('short_signal_v1', 0) for item in symbol_data],
                'short_signal_v2': [item.get('short_signal_v2', 0) for item in symbol_data],
                'long_signal': [item.get('long_signal', 0) for item in symbol_data],
                'combined_signal_v1': [item.get('combined_signal_v1', 0) for item in symbol_data],
                'macd_signal': [item.get('macd_signal', 0) for item in symbol_data],
                'momentum_color_signal': [item.get('momentum_color_signal', 0) for item in symbol_data],
            }
            
            # 지표 데이터
            indicators_data = {
                'Final_Composite_Value': [item.get('fcv', 0) for item in symbol_data]
            }
            
            return {
                'symbol': symbol,
                'dates': dates,
                'data': stock_data,
                'signals': signals_data,
                'indicators': indicators_data,
                'trendlines': [],  # 추세선 데이터 (나중에 추가 예정)
                'last_updated': symbol_data[-1].get('last_updated', dates[-1]) if symbol_data else None
            }
            
        except Exception as e:
            logger.error(f"신호 데이터 조회 실패: {symbol}, {e}")
            return {
                'symbol': symbol,
                'dates': [],
                'signals': {},
                'indicators': {},
                'error': f'데이터 조회 실패: {e}'
            }
    
    def get_available_symbols(self) -> List[str]:
        """사용 가능한 종목 목록 조회"""
        try:
            symbols = list(set([item.get('symbol') for item in self.data if item.get('symbol')]))
            return sorted(symbols)
        except Exception as e:
            logger.error(f"종목 목록 조회 실패: {e}")
            return []
    
    def get_data_info(self) -> Dict[str, Any]:
        """데이터 정보 조회"""
        try:
            if not self.data:
                return {'total_records': 0, 'symbols': [], 'last_updated': None}
            
            symbols = list(set([item.get('symbol') for item in self.data if item.get('symbol')]))
            last_updated = max([item.get('last_updated', '') for item in self.data])
            
            return {
                'total_records': len(self.data),
                'symbols': sorted(symbols),
                'last_updated': last_updated
            }
        except Exception as e:
            logger.error(f"데이터 정보 조회 실패: {e}")
            return {'total_records': 0, 'symbols': [], 'last_updated': None}