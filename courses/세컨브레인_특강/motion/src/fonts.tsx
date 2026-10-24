import React, {useEffect, useState} from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

const FACES = [
  {family: 'Pretendard', file: 'fonts/PretendardVariable.woff2', weight: '45 920'},
  {family: 'Inter', file: 'fonts/InterVariable-latin.woff2', weight: '100 900'},
  {family: 'Noto Serif KR', file: 'fonts/NotoSerifKR-900-latin.woff2', weight: '900'},
];

/** 로컬 글꼴(public/fonts)을 모두 읽은 뒤에만 장면을 그린다. */
export const Fonts: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender('local fonts'));

  useEffect(() => {
    Promise.all(
      FACES.map((f) =>
        new FontFace(f.family, `url(${staticFile(f.file)})`, {weight: f.weight}).load(),
      ),
    )
      .then((list) => {
        list.forEach((ff) => document.fonts.add(ff));
        return document.fonts.ready;
      })
      .then(() => {
        setReady(true);
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  }, [handle]);

  return ready ? <>{children}</> : null;
};
