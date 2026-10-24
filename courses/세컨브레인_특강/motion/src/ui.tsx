import React from 'react';
import {interpolateColors} from 'remotion';
import {eIn, eOut, lerp, pg} from './anim';
import {EMOJI, FONT, SERIF, TAG, Theme, TagColor} from './theme';

/** 이모지 — 글자 크기와 별개로 아이콘으로만 쓴다(64px 안팎) */
export const Emoji: React.FC<{size?: number; children: React.ReactNode}> = ({size = 64, children}) => (
  <span style={{fontFamily: EMOJI, fontSize: size, lineHeight: 1, display: 'inline-block'}}>{children}</span>
);

/** 노션 select 태그 칩 */
export const Tag: React.FC<{c: TagColor; children: React.ReactNode; size?: number}> = ({c, children, size = 48}) => (
  <span
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      height: size + 20,
      padding: '0 22px',
      borderRadius: 8,
      background: TAG[c].bg,
      color: TAG[c].fg,
      fontSize: size,
      fontWeight: 500,
      whiteSpace: 'nowrap',
      letterSpacing: '-0.01em',
    }}
  >
    {children}
  </span>
);

export type Step = {num?: number; word: string; sub?: string; sub2?: {text: string; from: number}; from: number; to?: number};

/** 왼쪽 위 단계 낱말 — 장면마다 하나씩 크게 */
export const StageHeader: React.FC<{f: number; steps: Step[]; t: Theme; top?: number; wordSize?: number; subSize?: number}> = ({
  f,
  steps,
  t,
  top = 56,
  wordSize = 128,
  subSize = 56,
}) => (
  <>
    {steps.map((s, i) => {
      const inP = pg(f, s.from, 16, eOut);
      const outP = s.to !== undefined ? pg(f, s.to - 9, 9, eIn) : 0;
      const op = inP * (1 - outP);
      if (op <= 0.001) return null;
      return (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: 96,
            top,
            height: wordSize,
            display: 'flex',
            alignItems: 'center',
            gap: 32,
            opacity: op,
            transform: `translateY(${(1 - inP) * 34 - outP * 12}px)`,
          }}
        >
          {s.num !== undefined && (
            <div
              style={{
                width: 112,
                height: 112,
                borderRadius: 26,
                background: t.accent,
                color: t.onAccent,
                fontFamily: SERIF,
                fontWeight: 900,
                fontSize: 76,
                lineHeight: '112px',
                textAlign: 'center',
              }}
            >
              {s.num}
            </div>
          )}
          <span style={{fontSize: wordSize, fontWeight: 800, letterSpacing: '-0.03em', color: t.ink, lineHeight: 1, whiteSpace: 'nowrap'}}>
            {s.word}
          </span>
          {s.sub && (
            <span style={{position: 'relative', marginTop: wordSize * 0.22, lineHeight: 1}}>
              <span
                style={{
                  fontSize: subSize,
                  fontWeight: 500,
                  color: t.ink3,
                  whiteSpace: 'nowrap',
                  opacity: s.sub2 ? 1 - pg(f, s.sub2.from, 10) : 1,
                }}
              >
                {s.sub}
              </span>
              {s.sub2 && (
                <span
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    fontSize: subSize,
                    fontWeight: 500,
                    color: t.ink3,
                    whiteSpace: 'nowrap',
                    opacity: pg(f, s.sub2.from + 6, 12),
                  }}
                >
                  {s.sub2.text}
                </span>
              )}
            </span>
          )}
        </div>
      );
    })}
  </>
);

/** 오른쪽 위 약어 글자 (C O D E / R A G) — 지금 단계의 글자만 강조색 */
export const Letters: React.FC<{f: number; letters: string[]; starts: number[]; t: Theme; showAt: number}> = ({
  f,
  letters,
  starts,
  t,
  showAt,
}) => {
  const vis = pg(f, showAt, 16);
  return (
    <div
      style={{
        position: 'absolute',
        right: 96,
        top: 70,
        display: 'flex',
        gap: 26,
        opacity: vis,
        fontFamily: FONT,
        fontSize: 104,
        fontWeight: 800,
        lineHeight: 1,
        letterSpacing: '0.02em',
      }}
    >
      {letters.map((l, i) => {
        const a = pg(f, starts[i], 14);
        const d = starts[i + 1] !== undefined ? pg(f, starts[i + 1], 14) : 0;
        const col = d > 0 ? interpolateColors(d, [0, 1], [t.accent, t.ink2]) : interpolateColors(a, [0, 1], [t.ink4, t.accent]);
        return (
          <span key={i} style={{color: col}}>
            {l}
          </span>
        );
      })}
    </div>
  );
};

const CheckGlyph: React.FC<{size: number; color: string; p?: number}> = ({size, color, p = 1}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path
      d="M5 12.5l4.5 4.5L19 7"
      stroke={color}
      strokeWidth={3.2}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray={24}
      strokeDashoffset={24 * (1 - p)}
    />
  </svg>
);
export {CheckGlyph};

/** 아래 단계 막대 — 끝난 단계는 ✓, 지금 단계는 강조색 */
export const Rail: React.FC<{
  f: number;
  labels: string[];
  starts: number[];
  t: Theme;
  showAt: number;
  place?: 'bottom' | 'top-left';
  endAt?: number;
}> = ({f, labels, starts, t, showAt, place = 'bottom', endAt}) => {
  const top = place === 'top-left';
  const chipH = top ? 76 : 84;
  const vis = pg(f, showAt, 18, eOut);
  return (
    <div
      style={{
        position: 'absolute',
        left: top ? 96 : 0,
        right: top ? undefined : 0,
        bottom: top ? undefined : 46,
        top: top ? 40 : undefined,
        display: 'flex',
        justifyContent: top ? 'flex-start' : 'center',
        alignItems: 'center',
        opacity: vis,
        transform: `translateY(${(top ? -1 : 1) * (1 - vis) * 24}px)`,
      }}
    >
      {labels.map((lb, i) => {
        const act = pg(f, starts[i], 14);
        const done = starts[i + 1] !== undefined ? pg(f, starts[i + 1], 14) : endAt !== undefined ? pg(f, endAt, 14) : 0;
        // 대기(0) → 진행(1) → 완료(2)
        const st = act + done;
        const bg = st <= 1 ? interpolateColors(st, [0, 1], [t.paper, t.accent]) : interpolateColors(st - 1, [0, 1], [t.accent, t.white]);
        const fg = st <= 1 ? interpolateColors(st, [0, 1], [t.ink3, t.onAccent]) : interpolateColors(st - 1, [0, 1], [t.onAccent, t.ink2]);
        const bd = st <= 1 ? interpolateColors(st, [0, 1], [t.line, t.accent]) : interpolateColors(st - 1, [0, 1], [t.accent, t.line]);
        return (
          <React.Fragment key={i}>
            {i > 0 && (
              <div
                style={{
                  width: 40,
                  height: 3,
                  margin: '0 14px',
                  background: f >= starts[i] ? t.ink3 : t.line,
                  borderRadius: 2,
                }}
              />
            )}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                height: chipH,
                padding: top ? '0 26px' : '0 32px',
                borderRadius: 42,
                background: bg,
                color: fg,
                border: `2px solid ${bd}`,
                fontSize: 48,
                fontWeight: 700,
                letterSpacing: '-0.02em',
                whiteSpace: 'nowrap',
                transform: `scale(${1 + 0.04 * Math.max(0, Math.min(1, act - done))})`,
              }}
            >
              <span style={{width: 40, display: 'inline-flex', justifyContent: 'center', alignItems: 'center', fontFamily: FONT}}>
                {done > 0.5 ? <CheckGlyph size={40} color={t.ink2} p={Math.min(1, (done - 0.5) * 2)} /> : i + 1}
              </span>
              {lb}
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

/** 마우스 커서 — (x,y)가 화살촉 끝 */
export const Cursor: React.FC<{x: number; y: number; press: number; opacity: number}> = ({x, y, press, opacity}) => {
  const s = 3.0;
  return (
    <svg
      width={24 * s}
      height={24 * s}
      viewBox="0 0 24 24"
      style={{
        position: 'absolute',
        left: x - 3 * s,
        top: y - 2 * s,
        opacity,
        transformOrigin: `${3 * s}px ${2 * s}px`,
        transform: `scale(${1 - 0.14 * press})`,
        filter: 'drop-shadow(0 3px 5px rgba(0,0,0,.25))',
      }}
    >
      <path
        d="M3 2 L3 19 L7.6 14.6 L10.8 21.6 L14 20.2 L10.8 13.4 L17.4 13.2 Z"
        fill="#0f0f0f"
        stroke="#ffffff"
        strokeWidth={1.5}
        strokeLinejoin="round"
      />
    </svg>
  );
};

/** 클릭 파문 */
export const Ripple: React.FC<{x: number; y: number; p: number; color: string}> = ({x, y, p, color}) => {
  if (p <= 0 || p >= 1) return null;
  const r = lerp(20, 110, p);
  return (
    <div
      style={{
        position: 'absolute',
        left: x - r,
        top: y - r,
        width: r * 2,
        height: r * 2,
        borderRadius: '50%',
        border: `5px solid ${color}`,
        opacity: (1 - p) * 0.7,
      }}
    />
  );
};
