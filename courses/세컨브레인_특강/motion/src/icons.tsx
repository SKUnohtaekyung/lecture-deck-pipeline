import React from 'react';
import {LIGHT as T} from './theme';

export type IconKind = 'chat' | 'blog' | 'memo' | 'photo' | 'search' | 'pagePlus' | 'pencil' | 'pin' | 'ticket';

/** 노션 무드의 단순한 선화 아이콘 — 검정 선 · 둥근 끝 · 스티커 색 점 하나 */
export const LineIcon: React.FC<{kind: IconKind; size?: number; dot?: string; stroke?: string}> = ({
  kind,
  size = 64,
  dot,
  stroke = '#0f0f0f',
}) => {
  const p = {fill: T.white, stroke, strokeWidth: 3.4, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  const q = {fill: 'none', stroke, strokeWidth: 3.4, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const};
  let body: React.ReactNode = null;
  switch (kind) {
    case 'chat':
      body = (
        <>
          <path {...p} d="M10 10h44a6 6 0 0 1 6 6v24a6 6 0 0 1-6 6H32L19 57V46h-9a6 6 0 0 1-6-6V16a6 6 0 0 1 6-6z" />
          <circle cx="20" cy="28" r="2.6" fill={stroke} />
          <circle cx="32" cy="28" r="2.6" fill={stroke} />
          <circle cx="44" cy="28" r="2.6" fill={stroke} />
        </>
      );
      break;
    case 'blog':
      body = (
        <>
          <rect {...p} x="5" y="9" width="54" height="46" rx="7" />
          <path {...q} d="M5 22h54M14 34h36M14 44h22" />
        </>
      );
      break;
    case 'memo':
      body = (
        <>
          <path {...p} d="M14 6h28l10 10v42H14z" />
          <path {...q} d="M42 6v10h10M22 30h22M22 39h22M22 48h13" />
        </>
      );
      break;
    case 'photo':
      body = (
        <>
          <rect {...p} x="5" y="10" width="54" height="44" rx="7" />
          <circle {...q} cx="20" cy="26" r="5.5" />
          <path {...q} d="M5 46l16-14 12 10 8-7 18 15" />
        </>
      );
      break;
    case 'search':
      body = (
        <>
          <circle {...p} cx="27" cy="27" r="17" />
          <path {...q} d="M40 40l17 17" />
        </>
      );
      break;
    case 'pagePlus':
      body = (
        <>
          <path {...p} d="M12 6h26l12 12v40H12z" />
          <path {...q} d="M38 6v12h12M31 32v18M22 41h18" />
        </>
      );
      break;
    case 'pencil':
      body = (
        <>
          <path {...p} d="M9 55l4-15L42 11l11 11-29 29z" />
          <path {...q} d="M36 17l11 11" />
        </>
      );
      break;
    case 'pin':
      body = (
        <>
          <path {...p} d="M32 59C20 44 14 36 14 26a18 18 0 0 1 36 0c0 10-6 18-18 33z" />
          <circle {...q} cx="32" cy="26" r="6" />
        </>
      );
      break;
    case 'ticket':
      body = (
        <>
          <path {...p} d="M6 18h52v8a6 6 0 0 0 0 12v8H6v-8a6 6 0 0 0 0-12z" />
          <path {...q} d="M40 18v28" strokeDasharray="1 7" />
        </>
      );
      break;
  }
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" style={{overflow: 'visible'}}>
      {body}
      {dot && <circle cx="54" cy="10" r="7" fill={dot} stroke={T.white} strokeWidth={2.5} />}
    </svg>
  );
};
