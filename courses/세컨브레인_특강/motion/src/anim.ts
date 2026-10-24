import {Easing, interpolate, spring} from 'remotion';

export const FPS = 30;

export const eIO = Easing.bezier(0.4, 0, 0.2, 1);
export const eOut = Easing.bezier(0.16, 1, 0.3, 1);
export const eIn = Easing.bezier(0.4, 0, 1, 1);
export const eSoft = Easing.bezier(0.5, 0, 0.15, 1);

/** start 프레임부터 dur 프레임 동안 0→1 */
export const pg = (
  f: number,
  start: number,
  dur: number,
  easing: (t: number) => number = eIO,
): number =>
  interpolate(f, [start, start + dur], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing,
  });

export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

export const sp = (
  f: number,
  start: number,
  opts?: {damping?: number; stiffness?: number; mass?: number},
): number => {
  const fr = f - start;
  if (fr <= 0) return 0;
  return spring({
    frame: fr,
    fps: FPS,
    config: {
      damping: opts?.damping ?? 22,
      stiffness: opts?.stiffness ?? 120,
      mass: opts?.mass ?? 1,
    },
  });
};

/** 글자 하나씩 나타나는 타이핑 (cps = 프레임당 글자 수) */
export const typed = (text: string, f: number, start: number, cpf: number): string => {
  const n = Math.max(0, Math.min(text.length, Math.floor((f - start) * cpf)));
  return text.slice(0, n);
};

/** 여러 키프레임 구간을 부드럽게 잇는 y 위치 등 */
export const path = (f: number, frames: number[], values: number[]): number =>
  interpolate(f, frames, values, {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: eIO,
  });
