import React from 'react';
import {AbsoluteFill, Easing, useCurrentFrame} from 'remotion';
import {eIO, eIn, eOut, lerp, pg, sp, typed} from './anim';
import {Fonts} from './fonts';
import {IconKind, LineIcon} from './icons';
import {FONT, LIGHT as T, MARKER, ST, TagColor} from './theme';
import {Emoji, Rail, StageHeader, Step, Tag} from './ui';

// V1 code — 세컨드 브레인 설명 영상 (42초)
// ① 흩어진 경주 여행 정보 → ② 정의 → ③ 모으기 → ④ 정리하기 → ⑤ 추리기 → ⑥ 꺼내 쓰기 → ⑦ AI가 꺼내 쓴다
export const CODE_DURATION = 1260;
const S = {s1: 0, s2: 135, s3: 270, s4: 420, s5: 600, s6: 795, s7: 990};

// 노션 페이지 카드(③~⑥)
const CARD = {x: 320, y: 284, w: 1280, h: 730};
const PAD = 48;
const ROW_X = CARD.x + PAD; // 368
const ROW_W = CARD.w - 2 * PAD; // 1184
const CONTENT_Y = CARD.y + 112; // 396 · 제목 줄 아래
const INBOX_H = 88;
const INBOX_Y = CONTENT_Y + 6;
const HEAD_H = 68;
const TROW_H = 74;
const TROW_Y = CONTENT_Y + HEAD_H; // 464
const TAG_X = ROW_X + 700;

type Item = {kind: IconKind; dot: string; label: string; w: number; fx: number; fy: number; rot: number};
const ITEMS: Item[] = [
  {kind: 'chat', dot: ST.sky, label: '카톡 링크', w: 390, fx: 120, fy: 130, rot: -3},
  {kind: 'blog', dot: ST.orange, label: '블로그 캡처', w: 450, fx: 1350, fy: 110, rot: 3},
  {kind: 'memo', dot: ST.yellow, label: '메모', w: 290, fx: 160, fy: 830, rot: 2},
  {kind: 'photo', dot: ST.pink, label: '사진', w: 290, fx: 1450, fy: 840, rot: -2},
];
const SCRAPS: {kind: IconKind; x: number; y: number}[] = [
  {kind: 'pin', x: 60, y: 470},
  {kind: 'ticket', x: 1730, y: 450},
  {kind: 'photo', x: 760, y: 900},
  {kind: 'chat', x: 1100, y: 56},
  {kind: 'blog', x: 520, y: 100},
];

const PLACES: {n: string; t: string; c: TagColor}[] = [
  {n: '불국사', t: '사찰', c: 'orange'},
  {n: '석굴암', t: '사찰', c: 'orange'},
  {n: '대릉원', t: '고분', c: 'brown'},
  {n: '첨성대', t: '유적', c: 'green'},
  {n: '동궁과 월지', t: '야경', c: 'purple'},
  {n: '황리단길', t: '거리', c: 'pink'},
  {n: '국립경주박물관', t: '박물관', c: 'blue'},
];

const STEPS: Step[] = [
  {from: S.s3, to: S.s4, word: '모으기', sub: 'Capture'},
  {from: S.s4, to: S.s5, word: '정리하기', sub: 'Organize'},
  {from: S.s5, to: S.s6, word: '추리기', sub: 'Distill'},
  {from: S.s6, to: S.s7, word: '꺼내 쓰기', sub: 'Express'},
];

// ---------- 떠다니는 정보 카드 → 받은함 행 ----------
const ItemView: React.FC<{i: number; f: number}> = ({i, f}) => {
  const it = ITEMS[i];
  const appear = pg(f, 4 + i * 5, 22, eOut);
  const m = pg(f, S.s3 + 10 + i * 8, 36, Easing.bezier(0.5, 0, 0.15, 1));
  const bobX = Math.cos((f / 30) * 0.9 + i * 1.7) * 14 * (1 - m);
  const bobY = Math.sin((f / 30) * 1.1 + i * 2.3) * 16 * (1 - m);
  const x = lerp(it.fx + bobX, ROW_X, m);
  const y = lerp(it.fy + bobY, INBOX_Y + i * INBOX_H, m);
  const w = lerp(it.w, ROW_W, m);
  const h = lerp(112, INBOX_H, m);
  const gone = pg(f, S.s4, 16); // 정리하기가 시작되면 받은함 행은 물러난다
  const opacity = appear * (1 - gone);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        opacity,
        transform: `rotate(${it.rot * (1 - m)}deg) scale(${lerp(0.92, 1, appear)}) translateX(${-gone * 60}px)`,
        background: T.white,
        borderRadius: lerp(20, 0, m),
        border: `1px solid rgba(230,230,230,${1 - m})`,
        boxShadow: `0 4px 18px rgba(0,0,0,${0.06 * (1 - m)}), 0 12px 32px rgba(0,0,0,${0.06 * (1 - m)})`,
        display: 'flex',
        alignItems: 'center',
        paddingLeft: lerp(26, 8, m),
        gap: 20,
        boxSizing: 'border-box',
      }}
    >
      <LineIcon kind={it.kind} size={60} dot={it.dot} />
      <span style={{fontSize: 48, fontWeight: 600, color: T.ink, letterSpacing: '-0.02em', whiteSpace: 'nowrap'}}>{it.label}</span>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 1, background: T.line2, opacity: m}} />
    </div>
  );
};

const Scrap: React.FC<{k: number; f: number}> = ({k, f}) => {
  const s = SCRAPS[k];
  const appear = pg(f, 8 + k * 5, 20, eOut);
  const m = pg(f, S.s3 + 6 + k * 6, 34, Easing.bezier(0.5, 0, 0.15, 1));
  const bobX = Math.cos((f / 30) * 0.8 + k * 2.1) * 12 * (1 - m);
  const bobY = Math.sin((f / 30) * 1.0 + k * 1.3) * 14 * (1 - m);
  return (
    <div
      style={{
        position: 'absolute',
        left: lerp(s.x + bobX, 940, m),
        top: lerp(s.y + bobY, 560, m),
        width: 120,
        height: 120,
        borderRadius: 60,
        background: T.white,
        border: `1px solid ${T.line}`,
        boxShadow: T.sh1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        opacity: appear * (1 - pg(f, S.s3 + 26 + k * 6, 14)),
        transform: `scale(${lerp(1, 0.3, m)})`,
      }}
    >
      <LineIcon kind={s.kind} size={64} />
    </div>
  );
};

// ---------- ② 머리 밖에 두는 기록 창고 ----------
const HeadAndBox: React.FC<{f: number}> = ({f}) => {
  const a = pg(f, S.s2 + 8, 18, eOut);
  const b = pg(f, S.s2 + 40, 20, eOut);
  const c = pg(f, S.s2 + 26, 28, eIO);
  const op = 1 - pg(f, S.s3 - 4, 14);
  return (
    <svg width={760} height={270} viewBox="0 0 760 270" style={{position: 'absolute', left: 580, top: 270, opacity: op}} fill="none">
      <g opacity={a} transform={`translate(0 ${(1 - a) * 16})`}>
        <circle cx="120" cy="96" r="62" fill="#fff" stroke="#0f0f0f" strokeWidth="4.5" />
        <path d="M30 262C30 190 70 160 120 160C170 160 210 190 210 262" fill="#fff" stroke="#0f0f0f" strokeWidth="4.5" strokeLinecap="round" />
        <circle cx="170" cy="52" r="9" fill={ST.sky} />
      </g>
      <path
        d="M222 100C310 20 410 20 490 100"
        stroke="#0f0f0f"
        strokeWidth="4.5"
        strokeLinecap="round"
        strokeDasharray="2 16"
        pathLength={1}
        style={{strokeDasharray: '0.012 0.04', strokeDashoffset: 1 - c}}
        opacity={c > 0 ? 1 : 0}
      />
      <path d="M478 72L492 102L462 100" stroke="#0f0f0f" strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" opacity={pg(f, S.s2 + 50, 8)} />
      <g opacity={b} transform={`translate(${(1 - b) * 24} 0)`}>
        <rect x="520" y="110" width="220" height="150" rx="18" fill="#fff" stroke="#0f0f0f" strokeWidth="4.5" />
        <path d="M520 156H740" stroke="#0f0f0f" strokeWidth="4.5" />
        <rect x="598" y="128" width="64" height="12" rx="6" fill="#0f0f0f" />
        <path d="M556 196H704M556 226H664" stroke="#0f0f0f" strokeWidth="4.5" strokeLinecap="round" />
        <circle cx="722" cy="118" r="11" fill={ST.orange} stroke="#fff" strokeWidth="3" />
      </g>
    </svg>
  );
};

// ---------- 문장(추리기 · 꺼내 쓰기) ----------
const SENT_X = ROW_X;
const LINE_STYLE: React.CSSProperties = {fontWeight: 500, letterSpacing: '-0.02em', lineHeight: 1.3, whiteSpace: 'nowrap'};

export const CodeScene: React.FC = () => {
  const f = useCurrentFrame();

  // ① ② 자막
  const cap1 = pg(f, 12, 22, eOut) * (1 - pg(f, S.s2 - 4, 14));
  const cap2 = pg(f, S.s2 + 6, 22, eOut) * (1 - pg(f, S.s3 - 4, 14));

  // 카드
  const cardP = pg(f, S.s3, 20, eOut) * (1 - pg(f, S.s7, 14));
  const tIn = pg(f, S.s3 + 14, 12); // 받은함 제목
  const tTable = pg(f, S.s4 + 8, 12); // 경주 자료함
  const tOpen = pg(f, S.s5 + 14, 12); // 불국사
  const tPlan = pg(f, S.s6 + 8, 14); // 1박 2일 일정표
  const titleA = tIn * (1 - pg(f, S.s4 + 2, 8));
  const titleB = tTable * (1 - pg(f, S.s5 + 8, 8));
  const titleC = tOpen * (1 - pg(f, S.s6 + 2, 8));
  const titleD = tPlan;

  // ④ 표
  const headP = pg(f, S.s4 + 10, 16) * (1 - pg(f, S.s5, 12));
  const tableRows = PLACES.map((p, k) => {
    const appear = pg(f, S.s4 + 16 + k * 7, 14, eOut);
    const tag = sp(f, S.s4 + 34 + k * 9, {damping: 20, stiffness: 150});
    let op = appear;
    let dx = 0;
    let bg = 'transparent';
    if (k === 0) {
      bg = `rgba(231,241,251,${pg(f, S.s5, 8) * (1 - pg(f, S.s5 + 14, 10))})`;
      op = appear * (1 - pg(f, S.s5 + 14, 12));
    } else {
      const out = pg(f, S.s5 + 8, 14);
      op = appear * (1 - out);
      dx = out * 50;
    }
    return (
      <div
        key={p.n}
        style={{
          position: 'absolute',
          left: ROW_X,
          top: TROW_Y + k * TROW_H + (1 - appear) * 14,
          width: ROW_W,
          height: TROW_H,
          opacity: op,
          transform: `translateX(${dx}px)`,
          display: 'flex',
          alignItems: 'center',
          gap: 18,
          boxSizing: 'border-box',
          paddingLeft: 8,
          background: bg,
          borderRadius: 8,
        }}
      >
        <Emoji size={48}>📄</Emoji>
        <span style={{fontSize: 48, fontWeight: 600, color: T.ink, letterSpacing: '-0.02em', whiteSpace: 'nowrap'}}>{p.n}</span>
        <div style={{position: 'absolute', left: TAG_X - ROW_X, top: (TROW_H - 66) / 2, opacity: tag, transform: `scale(${lerp(0.8, 1, tag)})`, transformOrigin: 'left center'}}>
          <Tag c={p.c}>{p.t}</Tag>
        </div>
        <div style={{position: 'absolute', left: 8, right: 8, bottom: 0, height: 1, background: T.line2}} />
      </div>
    );
  });

  // ⑤ ⑥ 문장
  const planMove = pg(f, S.s6 + 6, 30, eIO);
  const planOut = pg(f, S.s6 + 6, 14);
  const hlFade = pg(f, S.s6 + 96, 24);
  const sentences = [
    // 0: 1일차 오전에 가기 → 1일차 오전 · 불국사
    {text0: '1일차 오전에 가기', text1: '1일차 오전 · 불국사', y0: 440, y1: 412, hl: true, hlStart: S.s5 + 62},
    // 1: 다보탑 · 석가탑이 있는 절 → 아래 보조 줄
    {text0: '다보탑 · 석가탑이 있는 절', text1: '다보탑 · 석가탑이 있는 절', y0: 550, y1: 486, hl: true, hlStart: S.s5 + 74},
    // 2: 청운교 앞에서 사진 → 사라짐
    {text0: '청운교 앞에서 사진', text1: '청운교 앞에서 사진', y0: 660, y1: 660, hl: false, hlStart: 0},
  ].map((s, k) => {
    const appear = pg(f, S.s5 + 24 + k * 8, 14, eOut);
    const hlIn = s.hl ? pg(f, s.hlStart, 20, eIO) : 0;
    const hl = hlIn * (1 - hlFade);
    let op = appear * (1 - pg(f, S.s6 + 0, 4) * 0); // 유지
    let y = s.y0;
    let fs = 56;
    let col = T.ink;
    let text = s.text0;
    if (k === 0) {
      y = lerp(s.y0, s.y1, planMove);
      const swap = pg(f, S.s6 + 16, 14);
      text = swap > 0.5 ? s.text1 : s.text0;
      op = appear * (swap > 0 && swap < 1 ? Math.abs(swap - 0.5) * 2 : 1);
    } else if (k === 1) {
      y = lerp(s.y0, s.y1, planMove);
      fs = lerp(56, 48, planMove);
      col = planMove > 0 ? T.ink3 : T.ink;
    } else {
      op = appear * (1 - planOut);
    }
    return (
      <div key={k} style={{position: 'absolute', left: SENT_X, top: y, opacity: op, transform: `translateY(${(1 - appear) * 18}px)`}}>
        <span
          style={{
            ...LINE_STYLE,
            fontSize: fs,
            color: col,
            padding: '0 8px',
            marginLeft: -8,
            backgroundImage: `linear-gradient(${MARKER}, ${MARKER})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: `${hl * 100}% 100%`,
          }}
        >
          {text}
        </span>
      </div>
    );
  });

  // ⑥ 다른 형광 줄들이 날아와 모인다
  const incoming = [
    {text: '1일차 오후 · 대릉원', y: 580, sx: -620, sy: 300},
    {text: '1일차 저녁 · 황리단길', y: 684, sx: -560, sy: 560},
    {text: '2일차 · 국립경주박물관', y: 788, sx: -640, sy: 820},
  ].map((c, k) => {
    const start = S.s6 + 30 + k * 16;
    const p = pg(f, start, 30, eIO);
    if (p <= 0) return null;
    const hl = (0.35 + 0.65 * (1 - pg(f, start + 30, 12))) * (1 - hlFade) + 0; // 날아올 땐 형광, 앉으면 서서히 사라짐
    return (
      <div key={k} style={{position: 'absolute', left: lerp(c.sx, SENT_X, p), top: lerp(c.sy, c.y, p), opacity: pg(f, start, 8)}}>
        <span
          style={{
            ...LINE_STYLE,
            fontSize: 56,
            color: T.ink,
            padding: '0 8px',
            marginLeft: -8,
            backgroundImage: `linear-gradient(${MARKER}, ${MARKER})`,
            backgroundRepeat: 'no-repeat',
            backgroundSize: `${Math.min(1, hl) * 100}% 100%`,
          }}
        >
          {c.text}
        </span>
      </div>
    );
  });

  // ⑦ ChatGPT가 자료함을 읽고 일정표를 쓴다
  const W7 = {cx: 96, cw: 880, nx: 1040, nw: 784, y: 290, h: 720};
  const w7 = pg(f, S.s7 + 6, 20, eOut);
  const cap7 = pg(f, S.s7 + 4, 22, eOut);
  const bubbleP = pg(f, S.s7 + 28, 16, eOut);
  const planLines = [
    {text: '경주 1박 2일 일정표', start: S.s7 + 62, size: 52, bold: true, row: -1},
    {text: '1일차 오전 · 불국사', start: S.s7 + 90, size: 48, bold: false, row: 0},
    {text: '1일차 오후 · 대릉원', start: S.s7 + 122, size: 48, bold: false, row: 2},
    {text: '1일차 저녁 · 황리단길', start: S.s7 + 154, size: 48, bold: false, row: 5},
    {text: '2일차 · 국립경주박물관', start: S.s7 + 186, size: 48, bold: false, row: 6},
  ];
  const litRow = (r: number) => {
    const l = planLines.find((p) => p.row === r);
    return l ? pg(f, l.start, 14) : 0;
  };

  return (
    <AbsoluteFill style={{background: T.paper, fontFamily: FONT, color: T.ink, wordBreak: 'keep-all'}}>
      {/* ① 문제 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 440,
          textAlign: 'center',
          fontSize: 108,
          fontWeight: 800,
          letterSpacing: '-0.03em',
          opacity: cap1,
          transform: `translateY(${(1 - cap1) * 24}px)`,
        }}
      >
        경주 여행 정보가 여기저기
      </div>

      {/* ② 정의 */}
      <HeadAndBox f={f} />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 590,
          textAlign: 'center',
          opacity: cap2,
          transform: `translateY(${(1 - cap2) * 24}px)`,
        }}
      >
        <div style={{fontSize: 120, fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1}}>세컨드 브레인</div>
        <div style={{fontSize: 68, fontWeight: 600, letterSpacing: '-0.02em', color: T.ink2, marginTop: 14}}>= 머리 밖에 두는 나만의 기록 창고</div>
      </div>

      <StageHeader f={f} steps={STEPS} t={T} top={136} wordSize={104} subSize={52} />
      <Rail f={f} labels={['모으기', '정리하기', '추리기', '꺼내 쓰기']} starts={[S.s3, S.s4, S.s5, S.s6]} t={T} showAt={S.s3 + 4} place="top-left" endAt={S.s7 + 200} />

      {/* ③~⑥ 노션 페이지 카드 */}
      <div
        style={{
          position: 'absolute',
          left: CARD.x,
          top: CARD.y,
          width: CARD.w,
          height: CARD.h,
          background: T.white,
          border: `1px solid ${T.line}`,
          borderRadius: 16,
          boxShadow: T.sh1,
          opacity: cardP,
          transform: `translateY(${(1 - Math.min(1, pg(f, S.s3, 20, eOut))) * 30}px)`,
        }}
      >
        {[
          {op: titleA, icon: '📥', text: '받은함'},
          {op: titleB, icon: '🗂️', text: '경주 자료함'},
          {op: titleC, icon: '📄', text: '불국사'},
          {op: titleD, icon: '🗓️', text: '1박 2일 일정표'},
        ].map((t, i) => (
          <div key={i} style={{position: 'absolute', left: PAD, top: 20, display: 'flex', alignItems: 'center', gap: 20, opacity: t.op}}>
            <Emoji size={68}>{t.icon}</Emoji>
            <span style={{fontSize: 68, fontWeight: 800, letterSpacing: '-0.03em'}}>{t.text}</span>
          </div>
        ))}
        <div style={{position: 'absolute', left: PAD, right: PAD, top: 110, height: 1, background: T.line}} />
        {/* 표 머리 */}
        <div
          style={{
            position: 'absolute',
            left: PAD,
            top: CONTENT_Y - CARD.y,
            width: ROW_W,
            height: HEAD_H,
            display: 'flex',
            alignItems: 'center',
            opacity: headP,
            color: T.ink3,
            fontSize: 48,
            fontWeight: 500,
            borderBottom: `1px solid ${T.line2}`,
            boxSizing: 'border-box',
          }}
        >
          <span style={{width: TAG_X - ROW_X}}>
            <b style={{fontWeight: 600, marginRight: 16}}>Aa</b>제목
          </span>
          <span>
            <b style={{fontWeight: 600, marginRight: 16}}>◉</b>종류
          </span>
        </div>
      </div>

      {SCRAPS.map((_, k) => (
        <Scrap key={k} k={k} f={f} />
      ))}
      {ITEMS.map((_, i) => (
        <ItemView key={i} i={i} f={f} />
      ))}
      {tableRows}
      {sentences}
      {incoming}

      {/* ⑦ */}
      <div
        style={{
          position: 'absolute',
          left: 96,
          top: 136,
          fontSize: 88,
          fontWeight: 800,
          letterSpacing: '-0.03em',
          lineHeight: 1.1,
          opacity: cap7,
          transform: `translateY(${(1 - cap7) * 24}px)`,
          whiteSpace: 'nowrap',
        }}
      >
        기록이 쌓이면 AI가 꺼내 씁니다
      </div>
      <div style={{opacity: w7, transform: `translateY(${(1 - w7) * 24}px)`}}>
        {/* ChatGPT */}
        <div style={{position: 'absolute', left: W7.cx, top: W7.y, width: W7.cw, height: W7.h, background: T.white, border: `1px solid ${T.line}`, borderRadius: 20, boxShadow: T.sh2}}>
          <div style={{height: 76, borderBottom: `1px solid ${T.line2}`, display: 'flex', alignItems: 'center', padding: '0 36px'}}>
            <span style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>ChatGPT</span>
          </div>
          <div
            style={{
              position: 'absolute',
              right: 36,
              top: 104,
              padding: '16px 26px',
              background: '#f4f4f4',
              borderRadius: 28,
              fontSize: 48,
              fontWeight: 500,
              whiteSpace: 'nowrap',
              opacity: bubbleP,
              transform: `translateY(${(1 - bubbleP) * 24}px)`,
            }}
          >
            경주 1박 2일 일정표를 써 주세요
          </div>
          {planLines.map((l, k) => (
            <div
              key={k}
              style={{
                position: 'absolute',
                left: 36,
                top: k === 0 ? 250 : 338 + (k - 1) * 84,
                fontSize: l.size,
                fontWeight: l.bold ? 800 : 500,
                letterSpacing: '-0.02em',
                whiteSpace: 'nowrap',
              }}
            >
              {typed(l.text, f, l.start, 0.55)}
            </div>
          ))}
        </div>
        {/* 노션 */}
        <div style={{position: 'absolute', left: W7.nx, top: W7.y, width: W7.nw, height: W7.h, background: T.white, border: `1px solid ${T.line}`, borderRadius: 20, boxShadow: T.sh2}}>
          <div style={{height: 76, borderBottom: `1px solid ${T.line2}`, display: 'flex', alignItems: 'center', padding: '0 28px', gap: 16}}>
            <div style={{width: 56, height: 56, borderRadius: 12, background: T.black, color: '#fff', fontFamily: '"Noto Serif KR",serif', fontWeight: 900, fontSize: 48, lineHeight: '56px', textAlign: 'center'}}>N</div>
            <span style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>Notion</span>
          </div>
          <div style={{position: 'absolute', left: 28, top: 92, display: 'flex', alignItems: 'center', gap: 16}}>
            <Emoji size={56}>🗂️</Emoji>
            <span style={{fontSize: 56, fontWeight: 800, letterSpacing: '-0.03em'}}>경주 자료함</span>
          </div>
          {PLACES.map((p, r) => {
            const lit = litRow(r);
            return (
              <div
                key={p.n}
                style={{
                  position: 'absolute',
                  left: 20,
                  right: 20,
                  top: 178 + r * 76,
                  height: 72,
                  borderRadius: 10,
                  boxSizing: 'border-box',
                  paddingLeft: 24,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  background: `rgba(231,241,251,${lit})`,
                  color: lit > 0.5 ? T.accentPress : T.ink,
                  fontSize: 48,
                  fontWeight: 600,
                  letterSpacing: '-0.02em',
                  whiteSpace: 'nowrap',
                }}
              >
                {lit > 0 && <div style={{position: 'absolute', left: 0, top: 12, bottom: 12, width: 8, borderRadius: 4, background: T.accent, opacity: lit}} />}
                <Emoji size={48}>📄</Emoji>
                {p.n}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const CodeVideo: React.FC = () => (
  <Fonts>
    <CodeScene />
  </Fonts>
);

void eIn;
