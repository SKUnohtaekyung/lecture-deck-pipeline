// 색 토큰 — plans/세컨브레인-특강/디자인_v2_노션.md §2, §6-1 (옵시디언은 조정값: 2026-10-22 조정자 지시)
export type Theme = {
  paper: string;
  white: string;
  line: string;
  line2: string;
  ink: string;
  ink2: string;
  ink3: string;
  ink4: string;
  accent: string;
  accentPress: string;
  accentTint: string;
  onAccent: string;
  black: string;
  sh1: string;
  sh2: string;
};

export const LIGHT: Theme = {
  paper: '#f6f5f4',
  white: '#ffffff',
  line: '#e6e6e6',
  line2: '#ededec',
  ink: 'rgba(0,0,0,.95)',
  ink2: '#31302e',
  ink3: '#615d59',
  ink4: '#a39e98',
  accent: '#0075de',
  accentPress: '#005bab',
  accentTint: '#e7f1fb',
  onAccent: '#ffffff',
  black: '#0f0f0f',
  sh1: '0 0 .175px 1.041px rgba(0,0,0,.01),0 .8px 2.925px rgba(0,0,0,.02),0 2.025px 7.847px rgba(0,0,0,.027),0 4px 18px rgba(0,0,0,.04)',
  sh2: '0 4px 18px rgba(0,0,0,.04),0 12px 32px rgba(0,0,0,.05),0 23px 52px rgba(0,0,0,.05)',
};

// 옵시디언 공식 값: 배경 #1c1c1c · 패널 #212121 · 선 #333333 · 글자 #dadada · 강조 #8a5cf5
export const DARK: Theme = {
  paper: '#1c1c1c',
  white: '#212121',
  line: '#333333',
  line2: '#2b2b2b',
  ink: '#dadada',
  ink2: '#bababa',
  ink3: '#999999',
  ink4: '#666666',
  accent: '#8a5cf5',
  accentPress: '#a079ff',
  accentTint: 'rgba(138,92,245,.18)',
  onAccent: '#ffffff',
  black: '#0f0f0f',
  sh1: '0 4px 18px rgba(0,0,0,.35)',
  sh2: '0 12px 32px rgba(0,0,0,.45)',
};

export const OBS_LOGO = '#a079ff'; // 옵시디언 로고 보라
export const OBS_NODE = '#999999'; // 그래프 기본 점

// 노션 앱 태그 칩 (밝은 바탕 + 진한 글자)
export const TAG = {
  gray: {bg: '#e3e2e0', fg: '#32302c'},
  brown: {bg: '#eee0da', fg: '#442a1e'},
  orange: {bg: '#fadec9', fg: '#49290e'},
  yellow: {bg: '#fdecc8', fg: '#402c1b'},
  green: {bg: '#dbeddb', fg: '#1c3829'},
  blue: {bg: '#d3e5ef', fg: '#183347'},
  purple: {bg: '#e8deee', fg: '#412454'},
  pink: {bg: '#f5e0e9', fg: '#4c2337'},
  red: {bg: '#ffe2dd', fg: '#5d1715'},
} as const;
export type TagColor = keyof typeof TAG;

// 스티커 색(장식 전용 · 점 하나)
export const ST = {
  sky: '#62aef0',
  purple: '#d6b6f6',
  pink: '#ff64c8',
  orange: '#dd5b00',
  teal: '#2a9d99',
  green: '#1aae39',
  yellow: '#f5c033',
} as const;

// 형광펜 (스티커 노랑 55%)
export const MARKER = 'rgba(245,192,51,.55)';

export const FONT = '"Inter","Pretendard",-apple-system,system-ui,sans-serif';
export const SERIF = '"Noto Serif KR","Pretendard",serif';
export const EMOJI = '"Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji",sans-serif';

export const W = 1920;
export const H = 1080;
