# InvestSmart Frontend

투자 교육용 기술적 분석 도구입니다.

## 🚀 기능

- **주식 차트 분석**: 캔들스틱 차트와 기술적 지표 표시
- **신호 분석**: 다양한 매수/매도 신호 제공
- **FCV 지표**: 종합 저평가 지수 배경 표시
- **다양한 종목**: 주식, ETF, 채권, 환율 등 지원

## 📊 지원 종목

### 현재 데이터 제공
- 코스피 (KOSPI)
- 나스닥 (NASDAQ)
- TLT (미국 20년 국채)
- USD/KRW 환율

### 선택 가능한 종목 (50개)
주식, ETF, 채권, 환율 등 다양한 자산 클래스 지원

## ⚠️ 면책조항

본 서비스는 **투자 교육 및 정보 제공** 목적으로 제작되었습니다.
- 모든 투자에는 원금 손실 위험이 있습니다
- 제공되는 정보는 투자 권유가 아닙니다
- 투자 결정은 본인 책임입니다

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Charts**: Plotly
- **Data**: JSON (정적 데이터)

## 📁 프로젝트 구조

```
├── app.py                 # 메인 애플리케이션
├── components/            # UI 컴포넌트
│   ├── chart.py          # 차트 렌더링
│   ├── stock_selector.py # 종목 선택
│   └── signal_controls.py # 신호 컨트롤
├── utils/                # 유틸리티
│   └── json_client.py    # JSON 데이터 클라이언트
├── signals_data.json     # 신호 데이터
└── requirements.txt      # 의존성
```

## 🚀 배포

Railway 또는 Render에서 자동 배포됩니다.

## 📝 라이선스

교육 목적으로만 사용 가능합니다.
