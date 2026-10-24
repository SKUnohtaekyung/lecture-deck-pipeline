import React from 'react';
import {AbsoluteFill, interpolateColors, useCurrentFrame} from 'remotion';
import {eIO, eOut, eSoft, lerp, path, pg, sp, typed} from './anim';
import {Fonts} from './fonts';
import {FONT, LIGHT as T, SERIF} from './theme';
import {Emoji, Rail, StageHeader, Step} from './ui';

// V3 rag — 질문 → 나누기 → 찾기 → 붙이기 → 만들기 (18초)
export const RAG_DURATION = 540;
const S = {s1: 0, s2: 60, s3: 150, s4: 260, s5: 350};

const WY = 230; // 두 창 위쪽
const WH = 670;
const BAR = 76;
const CHAT = {x: 96, w: 820};
const NOTE = {x: 980, w: 844};

const QUESTION = '경주 1박 2일 일정표를 써 주세요';
const PLACES = ['불국사', '석굴암', '대릉원', '첨성대', '황리단길', '국립경주박물관'];
const LIT = [0, 2, 4]; // 불국사 · 대릉원 · 황리단길
const LIT_PIECE = [1, 0, 2]; // 켜지는 조각 번호
const ROW_TOP = 410;
const ROW_H = 76;
const rowC = (i: number) => ROW_TOP + i * ROW_H + ROW_H / 2;
const ROW_X = NOTE.x + 20;
const ROW_W = NOTE.w - 40;
const PIECE_X = ROW_X + 430;
const PIECE_W = 108;
const PIECE_H = 44;
const GAP_MAX = 18;
const pieceX = (j: number, g: number) => PIECE_X + j * (PIECE_W + g);
const pieceY = (i: number) => ROW_TOP + i * ROW_H + (ROW_H - PIECE_H) / 2;

const ANSWER_HEAD = '1일차';
const ANSWERS = [
  {text: '오전 · 불국사', chip: '불국사', row: 0},
  {text: '오후 · 대릉원', chip: '대릉원', row: 2},
  {text: '저녁 · 황리단길', chip: '황리단길', row: 4},
];
const ANS_X = 132;
const CHIP_X = 520;
const ansY = (k: number) => 560 + k * 92; // 문장 줄
const BOX_CHIP_X = 148;
const boxChipY = (k: number) => 540 + k * 84;

const STEPS: Step[] = [
  {from: S.s1, to: S.s2, word: '질문'},
  {from: S.s2, to: S.s3, num: 1, word: '나누기'},
  {from: S.s3, to: S.s4, num: 2, word: '찾기'},
  {from: S.s4, to: S.s5, num: 3, word: '붙이기'},
  {from: S.s5, num: 4, word: '만들기'},
];

// 출처 칩 (노션 페이지 멘션)
const Chip: React.FC<{label: string; shadow?: number}> = ({label, shadow = 0}) => (
  <div
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 12,
      height: 72,
      padding: '0 22px 0 18px',
      borderRadius: 14,
      boxSizing: 'border-box',
      background: '#f1f1ef',
      border: `2px solid ${T.line}`,
      boxShadow: shadow > 0 ? `0 8px 24px rgba(0,0,0,${0.12 * shadow})` : 'none',
      fontSize: 48,
      fontWeight: 600,
      color: T.ink,
      letterSpacing: '-0.02em',
      whiteSpace: 'nowrap',
    }}
  >
    <Emoji size={48}>📄</Emoji>
    {label}
  </div>
);

const Magnifier: React.FC<{x: number; y: number; opacity: number}> = ({x, y, opacity}) => (
  <svg width={170} height={170} viewBox="0 0 170 170" style={{position: 'absolute', left: x - 56, top: y - 56, opacity, filter: 'drop-shadow(0 6px 10px rgba(0,0,0,.18))'}}>
    <line x1="98" y1="98" x2="152" y2="152" stroke="#0f0f0f" strokeWidth="18" strokeLinecap="round" />
    <circle cx="56" cy="56" r="46" fill="rgba(255,255,255,.55)" stroke="#0f0f0f" strokeWidth="12" />
  </svg>
);

/** 문단 조각(글줄 두 개가 든 작은 카드) */
const PieceBox: React.FC<{lit: number; radius: number}> = ({lit, radius}) => {
  const bg = interpolateColors(lit, [0, 1], ['#f1f1ef', T.accentTint]);
  const bd = interpolateColors(lit, [0, 1], [T.line, T.accent]);
  const bar = interpolateColors(lit, [0, 1], ['#d6d3ce', '#7ab4ee']);
  return (
    <div style={{width: PIECE_W, height: PIECE_H, boxSizing: 'border-box', borderRadius: radius, background: bg, border: `${lit > 0.5 ? 3 : 2}px solid ${bd}`, position: 'relative'}}>
      <div style={{position: 'absolute', left: 14, top: 11, width: 66, height: 6, borderRadius: 3, background: bar}} />
      <div style={{position: 'absolute', left: 14, top: 24, width: 44, height: 6, borderRadius: 3, background: bar}} />
    </div>
  );
};

export const RagScene: React.FC = () => {
  const f = useCurrentFrame();

  const winL = pg(f, 0, 24, eOut);
  const winR = pg(f, 10, 24, eOut);
  const qP = pg(f, 12, 22, eOut);

  // 나누기: 문서 막대가 세 조각으로 갈라진다
  const splitP = (i: number) => pg(f, S.s2 + 10 + i * 5, 26, eSoft);

  // 찾기: 돋보기가 행마다 잠깐 멈춤
  const arrive = PLACES.map((_, i) => S.s3 + 12 + i * 15);
  const frames: number[] = [S.s3 + 2];
  const ys: number[] = [370];
  arrive.forEach((t, i) => {
    frames.push(t, t + 8);
    ys.push(rowC(i), rowC(i));
  });
  const magY = path(f, frames, ys);
  const magOp = pg(f, S.s3 + 2, 10) * (1 - pg(f, S.s3 + 100, 8));
  const litAt = (idx: number) => pg(f, arrive[LIT[idx]] + 2, 12);
  const scan = (i: number) => (LIT.includes(i) ? 0 : pg(f, arrive[i], 8) * (1 - pg(f, arrive[i] + 8, 10)));

  // 붙이기: 상자 + 날아오는 조각
  const boxP = pg(f, S.s4, 16, eOut);
  const boxOut = pg(f, S.s5, 12);
  const bubbleY = 330 + 84 * boxP * (1 - boxOut);
  const flyStart = (k: number) => S.s4 + 12 + k * 10;
  const flyP = (k: number) => pg(f, flyStart(k), 30, eSoft);

  const rowEls = PLACES.map((label, i) => {
    const lit = LIT.includes(i);
    const idx = LIT.indexOf(i);
    const l = lit ? litAt(idx) : 0;
    const sc = scan(i);
    return (
      <div
        key={i}
        style={{
          position: 'absolute',
          left: ROW_X,
          top: ROW_TOP + i * ROW_H,
          width: ROW_W,
          height: ROW_H,
          boxSizing: 'border-box',
          borderRadius: 12,
          display: 'flex',
          alignItems: 'center',
          paddingLeft: 20,
          gap: 14,
          background: lit ? `rgba(231,241,251,${l * 0.8})` : `rgba(0,0,0,${0.045 * sc})`,
          fontSize: 48,
          fontWeight: 600,
          letterSpacing: '-0.02em',
          color: lit ? interpolateColors(l, [0, 1], [T.ink, T.accentPress]) : T.ink,
          whiteSpace: 'nowrap',
        }}
      >
        {lit && <div style={{position: 'absolute', left: 0, top: 14, bottom: 14, width: 8, borderRadius: 4, background: T.accent, opacity: l}} />}
        <Emoji size={48}>📄</Emoji>
        {label}
        {!lit && <div style={{position: 'absolute', left: 8, right: 8, bottom: 0, height: 1, background: T.line2}} />}
      </div>
    );
  });

  // 조각 (붙이기에서 날아가는 조각은 원래 자리에서 사라진다)
  const pieceEls = PLACES.flatMap((_, i) =>
    [0, 1, 2].map((j) => {
      const sp0 = splitP(i);
      const g = GAP_MAX * sp0;
      const idx = LIT.indexOf(i);
      const isLit = idx >= 0 && LIT_PIECE[idx] === j;
      const lit = isLit ? litAt(idx) : 0;
      const gone = isLit ? pg(f, flyStart(idx), 6) : 0;
      return (
        <div
          key={`${i}-${j}`}
          style={{
            position: 'absolute',
            left: pieceX(j, g),
            top: pieceY(i) - 5 * Math.sin(sp0 * Math.PI) * 0.0 - 3 * sp0,
            opacity: winR * (1 - gone),
          }}
        >
          <PieceBox lit={lit} radius={lerp(3, 10, sp0)} />
        </div>
      );
    }),
  );

  return (
    <AbsoluteFill style={{background: T.paper, fontFamily: FONT, color: T.ink, wordBreak: 'keep-all'}}>
      {/* ChatGPT 창 */}
      <div
        style={{
          position: 'absolute',
          left: CHAT.x,
          top: WY,
          width: CHAT.w,
          height: WH,
          opacity: winL,
          transform: `translateY(${(1 - winL) * 24}px)`,
          background: T.white,
          border: `1px solid ${T.line}`,
          borderRadius: 20,
          boxShadow: T.sh2,
        }}
      >
        <div style={{height: BAR, borderBottom: `1px solid ${T.line2}`, display: 'flex', alignItems: 'center', padding: '0 36px'}}>
          <span style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>ChatGPT</span>
        </div>
      </div>

      {/* 노션 창 */}
      <div
        style={{
          position: 'absolute',
          left: NOTE.x,
          top: WY,
          width: NOTE.w,
          height: WH,
          opacity: winR,
          transform: `translateY(${(1 - winR) * 24}px)`,
          background: T.white,
          border: `1px solid ${T.line}`,
          borderRadius: 20,
          boxShadow: T.sh2,
        }}
      >
        <div style={{height: BAR, borderBottom: `1px solid ${T.line2}`, display: 'flex', alignItems: 'center', padding: '0 28px', gap: 16}}>
          <div style={{width: 56, height: 56, borderRadius: 12, background: T.black, color: '#fff', fontFamily: SERIF, fontWeight: 900, fontSize: 48, lineHeight: '56px', textAlign: 'center'}}>N</div>
          <span style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>Notion</span>
        </div>
        <div style={{position: 'absolute', left: 28, top: BAR + 14, display: 'flex', alignItems: 'center', gap: 16}}>
          <Emoji size={52}>🗂️</Emoji>
          <span style={{fontSize: 52, fontWeight: 800, letterSpacing: '-0.03em'}}>경주 자료함</span>
        </div>
      </div>
      <div style={{opacity: winR}}>{rowEls}</div>
      {pieceEls}

      {/* 질문 + 찾은 글 상자 */}
      {boxP * (1 - boxOut) > 0.001 && (
        <div
          style={{
            position: 'absolute',
            left: 120,
            top: 318,
            width: 772,
            height: 478,
            boxSizing: 'border-box',
            border: `3px solid ${T.accent}`,
            borderRadius: 26,
            background: 'rgba(231,241,251,.45)',
            opacity: boxP * (1 - boxOut),
            transform: `scale(${lerp(0.97, 1, boxP)})`,
          }}
        >
          <div
            style={{
              position: 'absolute',
              left: 24,
              top: 16,
              display: 'inline-flex',
              alignItems: 'center',
              height: 68,
              padding: '0 24px',
              borderRadius: 12,
              background: T.accent,
              color: T.onAccent,
              fontSize: 48,
              fontWeight: 700,
              whiteSpace: 'nowrap',
            }}
          >
            질문 + 찾은 글
          </div>
        </div>
      )}

      {/* 질문 말풍선 */}
      <div
        style={{
          position: 'absolute',
          right: 1920 - (CHAT.x + CHAT.w - 36),
          top: bubbleY,
          padding: '20px 28px',
          background: '#f4f4f4',
          borderRadius: 28,
          fontSize: 48,
          lineHeight: 1.4,
          fontWeight: 500,
          opacity: qP,
          transform: `translateY(${(1 - qP) * 28}px) scale(${lerp(0.96, 1, qP)})`,
          whiteSpace: 'nowrap',
        }}
      >
        {QUESTION}
      </div>

      {/* 날아오는 조각 → 칩 */}
      {LIT.map((row, k) => {
        const p = flyP(k);
        const op = pg(f, flyStart(k), 4) * (1 - pg(f, S.s5, 12));
        if (op <= 0.001) return null;
        const sx = pieceX(LIT_PIECE[k], GAP_MAX);
        const sy = pieceY(row);
        const chipP = pg(f, flyStart(k) + 14, 14);
        const x = lerp(sx, BOX_CHIP_X, p);
        const y = lerp(sy - 14, boxChipY(k), p);
        return (
          <div key={k} style={{position: 'absolute', left: x, top: y, opacity: op}}>
            <div style={{position: 'absolute', left: 0, top: 14, opacity: 1 - chipP}}>
              <PieceBox lit={1} radius={10} />
            </div>
            <div style={{opacity: chipP}}>
              <Chip label={PLACES[row]} shadow={Math.sin(p * Math.PI)} />
            </div>
          </div>
        );
      })}

      {/* 만들기: 일정표 문장 + 출처 칩 */}
      {(() => {
        const headStart = S.s5 + 14;
        const head = typed(ANSWER_HEAD, f, headStart, 0.5);
        return (
          <div style={{position: 'absolute', left: ANS_X, top: 478, fontSize: 52, fontWeight: 800, letterSpacing: '-0.02em', whiteSpace: 'nowrap'}}>{head}</div>
        );
      })()}
      {ANSWERS.map((a, k) => {
        const start = S.s5 + 30 + k * 40;
        const t = typed(a.text, f, start, 0.55);
        const chipP = sp(f, start + Math.ceil(a.text.length / 0.55), {damping: 18, stiffness: 150});
        return (
          <React.Fragment key={k}>
            <div style={{position: 'absolute', left: ANS_X, top: ansY(k), fontSize: 48, fontWeight: 500, lineHeight: 1.4, whiteSpace: 'nowrap'}}>{t}</div>
            <div
              style={{
                position: 'absolute',
                left: CHIP_X,
                top: ansY(k) - 3,
                opacity: chipP,
                transform: `scale(${lerp(0.8, 1, chipP)})`,
                transformOrigin: 'left center',
              }}
            >
              <Chip label={a.chip} />
            </div>
          </React.Fragment>
        );
      })}

      <Magnifier x={1480} y={magY} opacity={magOp} />

      <StageHeader f={f} steps={STEPS} t={T} />
      <Rail f={f} labels={['나누기', '찾기', '붙이기', '만들기']} starts={[S.s2, S.s3, S.s4, S.s5]} t={T} showAt={S.s2 + 6} />
    </AbsoluteFill>
  );
};

export const RagVideo: React.FC = () => (
  <Fonts>
    <RagScene />
  </Fonts>
);

void eIO;
