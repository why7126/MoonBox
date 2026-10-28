import {defineConfig, mergeConfig} from 'vite';
import config from '../vite.config';

// Production bundling of the actual page for the isolated browser fixture.
export default mergeConfig(config, defineConfig({
  build: {
    outDir: '/tmp/moonbox-bug0056-web',
    rollupOptions: {input: 'e2e/context-performance.html'},
    target: 'esnext',
  },
  preview: {proxy: config.server?.proxy},
}));
