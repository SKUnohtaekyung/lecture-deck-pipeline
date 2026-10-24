import React from 'react';
import {Composition} from 'remotion';
import {CODE_DURATION, CodeVideo} from './Code';
import {MCP_DURATION, McpVideo} from './Mcp';
import {OBSIDIAN_DURATION, ObsidianVideo} from './Obsidian';
import {RAG_DURATION, RagVideo} from './Rag';
import {FPS} from './anim';
import {H, W} from './theme';

export const Root: React.FC = () => (
  <>
    <Composition id="code" component={CodeVideo} durationInFrames={CODE_DURATION} fps={FPS} width={W} height={H} />
    <Composition id="mcp" component={McpVideo} durationInFrames={MCP_DURATION} fps={FPS} width={W} height={H} />
    <Composition id="rag" component={RagVideo} durationInFrames={RAG_DURATION} fps={FPS} width={W} height={H} />
    <Composition id="obsidian" component={ObsidianVideo} durationInFrames={OBSIDIAN_DURATION} fps={FPS} width={W} height={H} />
  </>
);
