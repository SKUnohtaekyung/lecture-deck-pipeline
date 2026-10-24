import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {eIO, eOut, lerp, pg, sp, typed} from './anim';
import {Fonts} from './fonts';
import {DARK as T, FONT, OBS_LOGO, OBS_NODE} from './theme';
import {Cursor, Rail, Ripple, StageHeader, Step} from './ui';

// V4 obsidian — 노트 파일 · [[링크]] · 그래프 보기 (11초) · 옵시디언 무드(어두운 면 · 보라)
export const OBSIDIAN_DURATION = 330;
const S = {s1: 0, s2: 60, s3: 150};

const PY = 240;
const PH = 660;
const BAR = 76;
const SIDE = {x: 96, w: 400};
const EDIT = {x: 520, w: 640};
const GRAPH = {x: 1184, w: 640};

const NOTES = ['경주 여행', '불국사', '숙소'];
const LINES = ['가볼 곳 [[불국사]]', '잘 곳 [[숙소]]'];

const STEPS: Step[] = [
  {from: S.s1, to: S.s2, num: 1, word: '노트 파일'},
  {from: S.s2, to: S.s3, num: 2, word: '[[링크]]'},
  {from: S.s3, num: 3, word: '그래프 보기'},
];

type Node = {id: string; x: number; y: number; r: number; label?: string; at: number; ph: number};
const G0 = S.s3;
const NODES: Node[] = [
  {id: 'hub', x: 1500, y: 600, r: 22, label: '경주 여행', at: G0 + 2, ph: 0.3},
  {id: 'prep', x: 1360, y: 450, r: 18, label: '불국사', at: G0 + 12, ph: 1.4},
  {id: 'rev', x: 1640, y: 740, r: 18, label: '숙소', at: G0 + 22, ph: 2.6},
  {id: 'h1', x: 1650, y: 470, r: 13, at: G0 + 32, ph: 3.1},
  {id: 'h2', x: 1370, y: 745, r: 13, at: G0 + 36, ph: 0.9},
  {id: 'a1', x: 1255, y: 385, r: 12, at: G0 + 40, ph: 2.0},
  {id: 'a2', x: 1240, y: 530, r: 12, at: G0 + 44, ph: 4.0},
  {id: 'a3', x: 1420, y: 370, r: 12, at: G0 + 48, ph: 1.1},
  {id: 'b1', x: 1765, y: 650, r: 12, at: G0 + 52, ph: 3.6},
  {id: 'b2', x: 1555, y: 865, r: 12, at: G0 + 56, ph: 2.2},
  {id: 'b3', x: 1745, y: 845, r: 12, at: G0 + 60, ph: 0.5},
  {id: 'd1', x: 1750, y: 395, r: 12, at: G0 + 64, ph: 1.8},
  {id: 'd2', x: 1795, y: 520, r: 12, at: G0 + 68, ph: 3.3},
  {id: 'c1', x: 1265, y: 800, r: 12, at: G0 + 72, ph: 2.8},
  {id: 'c2', x: 1320, y: 862, r: 12, at: G0 + 76, ph: 0.2},
  {id: 'c3', x: 1230, y: 690, r: 12, at: G0 + 80, ph: 1.6},
];
const EDGES: [string, string][] = [
  ['hub', 'prep'],
  ['hub', 'rev'],
  ['hub', 'h1'],
  ['hub', 'h2'],
  ['prep', 'a1'],
  ['prep', 'a2'],
  ['prep', 'a3'],
  ['a1', 'a3'],
  ['rev', 'b1'],
  ['rev', 'b2'],
  ['rev', 'b3'],
  ['b2', 'b3'],
  ['d1', 'd2'],
  ['c1', 'c2'],
  ['c2', 'c3'],
  ['c3', 'c1'],
];
const SELECTED = 'hub';
const NEIGHBORS = new Set(['hub', 'prep', 'rev', 'h1', 'h2']);
const byId = (id: string) => NODES.find((n) => n.id === id) as Node;

const Panel: React.FC<{x: number; w: number; opacity?: number; title: React.ReactNode; children?: React.ReactNode}> = ({
  x,
  w,
  opacity = 1,
  title,
  children,
}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: PY,
      width: w,
      height: PH,
      background: T.white,
      border: `1px solid ${T.line}`,
      borderRadius: 16,
      boxShadow: T.sh1,
      opacity,
      transform: `translateY(${(1 - opacity) * 20}px)`,
      overflow: 'hidden',
    }}
  >
    <div style={{height: BAR, borderBottom: `1px solid ${T.line}`, display: 'flex', alignItems: 'center', padding: '0 28px', gap: 14}}>{title}</div>
    {children}
  </div>
);

const DocIcon: React.FC<{color: string}> = ({color}) => (
  <svg width={36} height={44} viewBox="0 0 36 44" fill="none">
    <path d="M6 3h16l10 10v28H6z" stroke={color} strokeWidth={3} strokeLinejoin="round" />
    <path d="M22 3v10h10" stroke={color} strokeWidth={3} strokeLinejoin="round" />
    <path d="M12 24h14M12 31h14" stroke={color} strokeWidth={3} strokeLinecap="round" />
  </svg>
);

const Gem: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 80 80" fill="none">
    <path d="M40 4 L66 22 L72 52 L48 76 L22 74 L8 46 L16 20 Z" fill={OBS_LOGO} />
    <path d="M40 4 L66 22 L40 38 L16 20 Z" fill="#ffffff" opacity={0.28} />
    <path d="M40 38 L66 22 L72 52 L48 76 Z" fill="#000000" opacity={0.22} />
    <path d="M40 38 L16 20 L8 46 L22 74 Z" fill="#ffffff" opacity={0.1} />
  </svg>
);

/** 타이핑 중인 한 줄 — [[ ]] 구간은 보라 */
const LinkLine: React.FC<{text: string}> = ({text}) => {
  const parts: React.ReactNode[] = [];
  const re = /\[\[[^\]]*\]{0,2}/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(<span key={k++}>{text.slice(last, m.index)}</span>);
    parts.push(
      <span key={k++} style={{color: T.accent, textDecoration: 'underline', textDecorationThickness: 3, textUnderlineOffset: 8}}>
        {m[0]}
      </span>,
    );
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(<span key={k++}>{text.slice(last)}</span>);
  return <>{parts}</>;
};

export const ObsidianScene: React.FC = () => {
  const f = useCurrentFrame();

  // 노드 위치 (부드럽게 떠 있음)
  const sel = pg(f, G0 + 108, 20, eIO); // 클릭 뒤 강조
  const pos = (n: Node) => ({
    x: n.x + Math.sin((f / 30) * 0.7 + n.ph) * 4,
    y: n.y + Math.cos((f / 30) * 0.6 + n.ph * 1.3) * 4,
  });
  const nodeIn = (n: Node) => sp(f, n.at, {damping: 16, stiffness: 150});

  // 편집기
  const edIn = pg(f, S.s2 + 2, 14, eOut);
  const titleP = pg(f, S.s2 + 8, 12, eOut);
  const l1 = typed(LINES[0], f, S.s2 + 18, 0.5);
  const l2 = typed(LINES[1], f, S.s2 + 50, 0.5);

  // 커서 클릭
  const hub = byId(SELECTED);
  const hp = pos(hub);
  const clickT = G0 + 100;
  const press = pg(f, clickT, 4) - pg(f, clickT + 6, 6);
  const curOp = pg(f, G0 + 66, 8);
  const mv = pg(f, G0 + 70, 28, eIO);
  const curX = lerp(1700, hp.x + 6, mv);
  const curY = lerp(880, hp.y + 8, mv);
  const ripple = pg(f, clickT + 2, 20, eOut);

  const dim = (id: string) => (NEIGHBORS.has(id) ? 1 : 1 - 0.6 * sel);

  return (
    <AbsoluteFill style={{background: T.paper, fontFamily: FONT, color: T.ink, wordBreak: 'keep-all'}}>
      <StageHeader f={f} steps={STEPS} t={T} />

      <div style={{position: 'absolute', right: 96, top: 66, display: 'flex', alignItems: 'center', gap: 20, opacity: pg(f, 6, 16)}}>
        <Gem size={84} />
        <span style={{fontSize: 56, fontWeight: 700, letterSpacing: '-0.02em', color: T.ink}}>Obsidian</span>
      </div>

      {/* 탐색기 */}
      <Panel
        x={SIDE.x}
        w={SIDE.w}
        opacity={pg(f, 2, 18, eOut)}
        title={
          <>
            <svg width={44} height={44} viewBox="0 0 44 44" fill="none">
              <path d="M5 10h13l4 5h17v22H5z" stroke={T.ink3} strokeWidth={3} strokeLinejoin="round" />
            </svg>
            <span style={{fontSize: 48, fontWeight: 600, color: T.ink2}}>금고</span>
          </>
        }
      >
        {NOTES.map((n, i) => {
          const p = sp(f, 14 + i * 14, {damping: 18, stiffness: 140});
          const open = i === 0 ? pg(f, S.s2, 12) : 0;
          return (
            <div
              key={n}
              style={{
                position: 'absolute',
                left: 16,
                right: 16,
                top: BAR + 16 + i * 88,
                height: 80,
                borderRadius: 12,
                background: `rgba(138,92,245,${0.18 * open})`,
                display: 'flex',
                alignItems: 'center',
                gap: 18,
                paddingLeft: 18,
                fontSize: 48,
                fontWeight: 500,
                color: open > 0.5 ? T.ink : T.ink2,
                opacity: p,
                transform: `translateX(${(1 - p) * -40}px)`,
                whiteSpace: 'nowrap',
              }}
            >
              <DocIcon color={open > 0.5 ? T.accent : T.ink3} />
              {n}
            </div>
          );
        })}
      </Panel>

      {/* 편집기 */}
      <Panel
        x={EDIT.x}
        w={EDIT.w}
        opacity={pg(f, 4, 18, eOut)}
        title={
          <span style={{fontSize: 48, fontWeight: 600, color: T.ink2, opacity: edIn}}>경주 여행</span>
        }
      >
        <div
          style={{
            position: 'absolute',
            left: 36,
            top: BAR + 36,
            fontSize: 72,
            fontWeight: 800,
            letterSpacing: '-0.03em',
            opacity: titleP,
            transform: `translateY(${(1 - titleP) * 16}px)`,
          }}
        >
          경주 여행
        </div>
        <div style={{position: 'absolute', left: 36, top: BAR + 170, fontSize: 48, fontWeight: 500, lineHeight: 1.4, whiteSpace: 'nowrap'}}>
          <LinkLine text={l1} />
        </div>
        <div style={{position: 'absolute', left: 36, top: BAR + 260, fontSize: 48, fontWeight: 500, lineHeight: 1.4, whiteSpace: 'nowrap'}}>
          <LinkLine text={l2} />
        </div>
      </Panel>

      {/* 그래프 보기 */}
      <Panel x={GRAPH.x} w={GRAPH.w} opacity={pg(f, 6, 18, eOut)} title={<span style={{fontSize: 48, fontWeight: 600, color: T.ink2}}>그래프 보기</span>} />

      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {EDGES.map(([a, b]) => {
          const A = byId(a);
          const B = byId(b);
          const t0 = Math.max(A.at, B.at) + 3;
          const dr = pg(f, t0, 14, eIO);
          if (dr <= 0) return null;
          const pa = pos(A);
          const pb = pos(B);
          const hi = (a === SELECTED || b === SELECTED) && NEIGHBORS.has(a) && NEIGHBORS.has(b);
          const o = hi ? 1 : 1 - 0.6 * sel;
          const x2 = lerp(pa.x, pb.x, dr);
          const y2 = lerp(pa.y, pb.y, dr);
          return (
            <line
              key={a + b}
              x1={pa.x}
              y1={pa.y}
              x2={x2}
              y2={y2}
              stroke={hi && sel > 0.01 ? T.accent : OBS_NODE}
              strokeOpacity={hi && sel > 0.01 ? lerp(0.35, 1, sel) * o : 0.35 * o}
              strokeWidth={hi && sel > 0.01 ? lerp(3, 6, sel) : 3}
              strokeLinecap="round"
            />
          );
        })}
        {NODES.map((n) => {
          const p = nodeIn(n);
          if (p <= 0.001) return null;
          const q = pos(n);
          const isSel = n.id === SELECTED;
          const hi = NEIGHBORS.has(n.id) && sel > 0.01;
          const r = n.r * p * (isSel ? 1 + 0.35 * sel : 1);
          const fill = hi ? T.accent : OBS_NODE;
          return (
            <g key={n.id} opacity={dim(n.id)}>
              {isSel && sel > 0.01 && <circle cx={q.x} cy={q.y} r={r + 18 * sel} fill={T.accent} opacity={0.25 * sel} />}
              <circle cx={q.x} cy={q.y} r={r} fill={fill} />
            </g>
          );
        })}
      </svg>
      {NODES.filter((n) => n.label).map((n) => {
        const p = nodeIn(n);
        if (p <= 0.05) return null;
        const q = pos(n);
        const below = n.id === 'rev';
        const leftSide = n.id === 'hub';
        return (
          <div
            key={n.id}
            style={{
              position: 'absolute',
              left: below ? q.x - 120 : leftSide ? q.x - 300 - 38 : q.x + 30,
              top: below ? q.y + n.r + 12 : q.y - 33,
              width: below ? 240 : leftSide ? 300 : undefined,
              textAlign: below ? 'center' : leftSide ? 'right' : undefined,
              fontSize: 48,
              fontWeight: 600,
              color: T.ink,
              opacity: Math.min(1, p) * dim(n.id),
              whiteSpace: 'nowrap',
            }}
          >
            {n.label}
          </div>
        );
      })}

      <Ripple x={hp.x} y={hp.y} p={ripple} color={T.accent} />
      <Cursor x={curX} y={curY} press={press} opacity={curOp} />

      <Rail f={f} labels={['노트 파일', '[[링크]]', '그래프 보기']} starts={[S.s1 + 6, S.s2, S.s3]} t={T} showAt={4} />
    </AbsoluteFill>
  );
};

export const ObsidianVideo: React.FC = () => (
  <Fonts>
    <ObsidianScene />
  </Fonts>
);
