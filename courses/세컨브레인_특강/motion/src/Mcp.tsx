import React from 'react';
import {AbsoluteFill, interpolateColors, useCurrentFrame} from 'remotion';
import {eIO, eIn, eOut, lerp, pg, sp, typed} from './anim';
import {Fonts} from './fonts';
import {IconKind, LineIcon} from './icons';
import {FONT, LIGHT as T, SERIF, TAG} from './theme';
import {Cursor, Emoji, Rail, Ripple, StageHeader, Step, Tag} from './ui';

// V2 mcp — 연결 · 도구 · 요청 · 승인 · 실행 (17초)
export const MCP_DURATION = 510;
const S = {s1: 0, s2: 54, s3: 135, s4: 228, s5: 330, s6: 408};

const WIN = {y: 250, w: 680, h: 640, lx: 96, rx: 1144, bar: 88};
const PLUG = {cx: 960, cy: 570, bw: 220, bh: 180, head: 100};
const REQUEST = '내 노션 「경주 여행」 페이지에 여행 기본 정보를 적어 주세요';

// 승인 카드 (전역 좌표)
const AP = {x: 580, y: 290, w: 760, h: 372, pad: 44};
const OK_BTN = {w: 190, h: 84};
const OK_CENTER = {x: AP.x + AP.w - AP.pad - OK_BTN.w / 2, y: AP.y + AP.h - AP.pad - OK_BTN.h / 2};

const STEPS: Step[] = [
  {from: S.s1, to: S.s2, word: '따로따로'},
  {from: S.s2, to: S.s3, num: 1, word: '연결', sub: 'MCP'},
  {from: S.s3, to: S.s4, num: 2, word: '도구'},
  {from: S.s4, to: S.s5, num: 3, word: '요청'},
  {from: S.s5, to: S.s6, num: 4, word: '승인'},
  {from: S.s6, num: 5, word: '실행'},
];

const TOOLS: {kind: IconKind; text: string}[] = [
  {kind: 'search', text: '검색'},
  {kind: 'pagePlus', text: '페이지 만들기'},
  {kind: 'pencil', text: '페이지 고치기'},
];

const Win: React.FC<{
  x: number;
  opacity: number;
  dy: number;
  side: 'left' | 'right';
  conn: number;
  bar: React.ReactNode;
  children: React.ReactNode;
}> = ({x, opacity, dy, side, conn, bar, children}) => {
  const slot = interpolateColors(conn, [0, 1], [TAG.gray.bg, T.accentTint]);
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: WIN.y + dy,
        width: WIN.w,
        height: WIN.h,
        opacity,
        background: T.white,
        border: `1px solid ${T.line}`,
        borderRadius: 20,
        boxShadow: T.sh2,
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          height: WIN.bar,
          borderBottom: `1px solid ${T.line2}`,
          display: 'flex',
          alignItems: 'center',
          padding: '0 28px',
          gap: 16,
          boxSizing: 'border-box',
        }}
      >
        {bar}
      </div>
      {/* USB-C 모양 포트 */}
      <div
        style={{
          position: 'absolute',
          top: WIN.h / 2 - 30,
          [side === 'left' ? 'right' : 'left']: 0,
          width: 40,
          height: 60,
          background: slot,
          borderRadius: side === 'left' ? '30px 0 0 30px' : '0 30px 30px 0',
        }}
      />
      {children}
    </div>
  );
};

export const McpScene: React.FC = () => {
  const f = useCurrentFrame();

  // ① 두 창 등장
  const inL = pg(f, 4, 26, eOut);
  const inR = pg(f, 10, 26, eOut);
  // ② 플러그가 내려와 딸깍
  const drop = sp(f, S.s2 + 4, {damping: 17, stiffness: 100});
  const snap = sp(f, S.s2 + 36, {damping: 13, stiffness: 280});
  const conn = pg(f, S.s2 + 38, 10);
  const ring = pg(f, S.s2 + 40, 34, eOut);
  const lx = WIN.lx - 36 * (1 - snap) - 40 * (1 - inL);
  const rx = WIN.rx + 36 * (1 - snap) + 40 * (1 - inR);
  const placeholder = pg(f, 14, 14) * (1 - pg(f, S.s2 + 2, 10));
  const plugOp = pg(f, S.s2 + 4, 8);
  const plugY = (1 - drop) * -460;
  const specP = pg(f, S.s2 + 44, 16, eOut); // 「MCP 규격」 라벨

  // ③ 호스트 · 서버 · 도구 목록
  const tagH = pg(f, S.s3 + 4, 14, eOut);
  const tagS = pg(f, S.s3 + 16, 14, eOut);
  const toolsIn = pg(f, S.s3 + 28, 14, eOut) * (1 - pg(f, S.s4 + 6, 12));
  const toolP = TOOLS.map((_, k) => pg(f, S.s3 + 34 + k * 16, 14, eOut));

  // ④ 요청 입력 → 보내기
  const typing = typed(REQUEST, f, S.s4 + 8, 0.6);
  const sendT = S.s4 + 66;
  const grow = pg(f, S.s4 + 2, 10);
  const shrink = pg(f, sendT + 2, 12);
  const pillH = lerp(84, 312, grow * (1 - shrink));
  const typedOp = 1 - pg(f, sendT, 8);
  const placeOp = 1 - pg(f, S.s4 + 2, 6);
  const bubbleP = pg(f, sendT + 6, 18, eOut);

  // ⑤ 승인 카드
  const apIn = pg(f, S.s5 + 4, 18, eOut);
  const apOut = pg(f, S.s5 + 58, 14, eIn);
  const apOp = apIn * (1 - apOut);
  const clickT = S.s5 + 48;
  const press = pg(f, clickT, 4) - pg(f, clickT + 6, 6);
  const curOp = pg(f, S.s5 + 8, 8) * (1 - pg(f, S.s5 + 60, 10));
  const curX = lerp(1520, OK_CENTER.x + 6, pg(f, S.s5 + 14, 30, eIO));
  const curY = lerp(850, OK_CENTER.y + 8, pg(f, S.s5 + 14, 30, eIO));
  const ripple = pg(f, clickT + 2, 20, eOut);
  const okDark = interpolateColors(press, [0, 1], [T.black, '#000000']);

  // ⑥ 노션에 세 줄
  const reply = pg(f, S.s6 + 4, 14, eOut);
  const lines = ['날짜: 11월 8~9일', '인원: 2명', '교통: KTX 경주역' + String.fromCharCode(10) + '(구 신경주역)'];
  const lineP = lines.map((_, k) => pg(f, S.s6 + 12 + k * 14, 14, eOut));

  const plugBorder = T.accent;
  const plugBg = interpolateColors(conn, [0, 1], [T.white, T.accent]);
  const plugFg = interpolateColors(conn, [0, 1], [T.accent, T.onAccent]);
  const headCol = interpolateColors(conn, [0, 1], [T.ink3, T.accentPress]);

  const usbHead = (side: 'l' | 'r') => (
    <div
      style={{
        position: 'absolute',
        left: side === 'l' ? -PLUG.head : PLUG.bw - 14,
        width: PLUG.head + 14,
        top: PLUG.bh / 2 - 28,
        height: 56,
        borderRadius: 28,
        boxSizing: 'border-box',
        border: `5px solid ${headCol}`,
        background: T.white,
        display: 'flex',
        alignItems: 'center',
        justifyContent: side === 'l' ? 'flex-start' : 'flex-end',
        padding: '0 22px',
      }}
    >
      <div style={{width: 46, height: 14, borderRadius: 7, background: headCol, opacity: 0.55}} />
    </div>
  );

  return (
    <AbsoluteFill style={{background: T.paper, fontFamily: FONT, color: T.ink, wordBreak: 'keep-all'}}>
      {/* ChatGPT 창 */}
      <Win
        x={lx}
        opacity={inL}
        dy={(1 - inL) * 24}
        side="left"
        conn={conn}
        bar={
          <>
            <span style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>ChatGPT</span>
            <span style={{opacity: tagH, transform: `scale(${lerp(0.85, 1, tagH)})`, transformOrigin: 'left center'}}>
              <Tag c="blue">호스트</Tag>
            </span>
          </>
        }
      >
        {/* 사용자 말풍선 */}
        <div
          style={{
            position: 'absolute',
            right: 36,
            top: 104,
            width: 600,
            boxSizing: 'border-box',
            padding: '20px 28px',
            background: '#f4f4f4',
            borderRadius: 28,
            fontSize: 48,
            lineHeight: 1.35,
            fontWeight: 500,
            opacity: bubbleP,
            transform: `translateY(${(1 - bubbleP) * 120}px)`,
          }}
        >
          {REQUEST}
        </div>
        {/* AI 답 */}
        <div
          style={{
            position: 'absolute',
            left: 36,
            top: 440,
            fontSize: 48,
            fontWeight: 500,
            lineHeight: 1.4,
            opacity: reply,
            transform: `translateY(${(1 - reply) * 16}px)`,
          }}
        >
          경주 여행에 적었어요
        </div>
        {/* 입력창 */}
        <div
          style={{
            position: 'absolute',
            left: 36,
            right: 36,
            top: 604 - pillH,
            height: pillH,
            boxSizing: 'border-box',
            background: '#f4f4f4',
            borderRadius: pillH > 100 ? 36 : 42,
            padding: pillH > 100 ? '22px 28px' : '0 28px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: pillH > 100 ? 'flex-start' : 'center',
            fontSize: 48,
            lineHeight: 1.4,
            fontWeight: 500,
          }}
        >
          <span style={{color: T.ink3, opacity: placeOp, position: 'absolute', whiteSpace: 'nowrap'}}>무엇이든 물어보세요</span>
          <span style={{opacity: typedOp}}>{typing}</span>
        </div>
      </Win>

      {/* 노션 창 */}
      <Win
        x={rx}
        opacity={inR}
        dy={(1 - inR) * 24}
        side="right"
        conn={conn}
        bar={
          <>
            <div
              style={{
                width: 60,
                height: 60,
                borderRadius: 12,
                background: T.black,
                color: '#fff',
                fontFamily: SERIF,
                fontWeight: 900,
                fontSize: 48,
                lineHeight: '60px',
                textAlign: 'center',
                flex: 'none',
              }}
            >
              N
            </div>
            <span style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>Notion</span>
            <span style={{opacity: tagS, transform: `scale(${lerp(0.85, 1, tagS)})`, transformOrigin: 'left center', whiteSpace: 'nowrap'}}>
              <Tag c="green">MCP 서버</Tag>
            </span>
          </>
        }
      >
        <div style={{position: 'absolute', left: 36, top: 116, display: 'flex', alignItems: 'center', gap: 18}}>
          <Emoji size={56}>🗺️</Emoji>
          <span style={{fontSize: 56, fontWeight: 800, letterSpacing: '-0.03em'}}>경주 여행</span>
        </div>
        {/* 도구 목록 */}
        {toolsIn > 0.001 && (
          <div style={{position: 'absolute', left: 36, top: 214, width: 608, opacity: toolsIn}}>
            <div style={{display: 'inline-block', marginBottom: 14, opacity: pg(f, S.s3 + 28, 12)}}>
              <Tag c="gray">도구 목록</Tag>
            </div>
            {TOOLS.map((t, k) => (
              <div
                key={t.text}
                style={{
                  height: 76,
                  marginBottom: 12,
                  borderRadius: 14,
                  border: `1px solid ${T.line}`,
                  boxShadow: T.sh1,
                  background: T.white,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 20,
                  paddingLeft: 22,
                  fontSize: 48,
                  fontWeight: 600,
                  letterSpacing: '-0.02em',
                  opacity: toolP[k],
                  transform: `translateX(${(1 - toolP[k]) * 36}px)`,
                }}
              >
                <LineIcon kind={t.kind} size={46} />
                {t.text}
              </div>
            ))}
          </div>
        )}
        {/* 적힌 세 줄 */}
        <div style={{position: 'absolute', left: 44, top: 218, width: 570, display: 'flex', flexDirection: 'column', gap: 16}}>
          {lines.map((ln, k) => (
            <div
              key={k}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 20,
                fontSize: 48,
                fontWeight: 500,
                lineHeight: 1.3,
                opacity: lineP[k],
                transform: `translateY(${(1 - lineP[k]) * 16}px)`,
              }}
            >
              <span style={{width: 14, height: 14, borderRadius: 7, background: T.ink, marginTop: 22, flex: 'none'}} />
              <span style={{whiteSpace: 'pre-line'}}>{ln}</span>
            </div>
          ))}
        </div>
      </Win>

      {/* 점선 자리 (장면 1) */}
      <div
        style={{
          position: 'absolute',
          left: PLUG.cx - PLUG.bw / 2,
          top: PLUG.cy - PLUG.bh / 2,
          width: PLUG.bw,
          height: PLUG.bh,
          boxSizing: 'border-box',
          border: `4px dashed ${T.ink4}`,
          borderRadius: 44,
          opacity: placeholder,
        }}
      />

      {/* 연결 파문 */}
      {ring > 0 && ring < 1 && (
        <div
          style={{
            position: 'absolute',
            left: PLUG.cx - lerp(130, 330, ring),
            top: PLUG.cy - lerp(110, 250, ring),
            width: lerp(130, 330, ring) * 2,
            height: lerp(110, 250, ring) * 2,
            borderRadius: 120,
            border: `6px solid ${T.accent}`,
            opacity: (1 - ring) * 0.55,
          }}
        />
      )}

      {/* MCP 플러그 (USB-C 모양) */}
      <div
        style={{
          position: 'absolute',
          left: PLUG.cx - PLUG.bw / 2,
          top: PLUG.cy - PLUG.bh / 2 + plugY,
          width: PLUG.bw,
          height: PLUG.bh,
          opacity: plugOp,
        }}
      >
        {usbHead('l')}
        {usbHead('r')}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            boxSizing: 'border-box',
            borderRadius: 44,
            border: `5px solid ${plugBorder}`,
            background: plugBg,
            color: plugFg,
            boxShadow: T.sh1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 76,
            fontWeight: 800,
            letterSpacing: '0.01em',
          }}
        >
          MCP
        </div>
        <div
          style={{
            position: 'absolute',
            left: -40,
            right: -40,
            top: PLUG.bh + 24,
            textAlign: 'center',
            fontSize: 48,
            fontWeight: 700,
            letterSpacing: '-0.02em',
            color: T.ink,
            whiteSpace: 'nowrap',
            opacity: specP,
            transform: `translateY(${(1 - specP) * 12}px)`,
          }}
        >
          MCP 규격
        </div>
      </div>

      {/* 승인 카드 */}
      {apOp > 0.001 && (
        <>
          <div style={{position: 'absolute', left: 0, right: 0, top: 220, bottom: 0, background: `rgba(246,245,244,${0.62 * apOp})`}} />
          <div
            style={{
              position: 'absolute',
              left: AP.x,
              top: AP.y,
              width: AP.w,
              height: AP.h,
              boxSizing: 'border-box',
              padding: AP.pad,
              background: T.white,
              border: `1px solid ${T.line}`,
              borderRadius: 24,
              boxShadow: T.sh2,
              opacity: apOp,
              transform: `translateY(${(1 - apIn) * 28 + apOut * 10}px) scale(${lerp(0.95, 1, apIn) - apOut * 0.03})`,
            }}
          >
            <div style={{fontSize: 52, fontWeight: 700, letterSpacing: '-0.02em'}}>Notion 사용 승인</div>
            <div style={{fontSize: 48, fontWeight: 500, color: T.ink3, marginTop: 14, lineHeight: 1.4}}>페이지에 세 줄을 씁니다</div>
            <div style={{position: 'absolute', right: AP.pad, bottom: AP.pad, display: 'flex', gap: 18}}>
              <div
                style={{
                  width: 170,
                  height: OK_BTN.h,
                  borderRadius: 42,
                  border: `2px solid ${T.line}`,
                  boxSizing: 'border-box',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 48,
                  fontWeight: 600,
                  color: T.ink2,
                }}
              >
                거부
              </div>
              <div
                style={{
                  width: OK_BTN.w,
                  height: OK_BTN.h,
                  borderRadius: 42,
                  background: okDark,
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 48,
                  fontWeight: 700,
                  transform: `scale(${1 - 0.05 * press})`,
                }}
              >
                승인
              </div>
            </div>
          </div>
          <Ripple x={OK_CENTER.x} y={OK_CENTER.y} p={ripple} color={T.black} />
          <Cursor x={curX} y={curY} press={press} opacity={curOp} />
        </>
      )}

      <StageHeader f={f} steps={STEPS} t={T} />
      <Rail f={f} labels={['연결', '도구', '요청', '승인', '실행']} starts={[S.s2, S.s3, S.s4, S.s5, S.s6]} t={T} showAt={S.s2 + 6} />
    </AbsoluteFill>
  );
};

export const McpVideo: React.FC = () => (
  <Fonts>
    <McpScene />
  </Fonts>
);
