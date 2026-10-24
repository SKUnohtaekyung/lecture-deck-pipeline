import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('png');
Config.setCodec('h264');
Config.setCrf(23);
Config.setPixelFormat('yuv420p');
Config.setOverwriteOutput(true);
