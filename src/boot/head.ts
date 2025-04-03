import { boot } from 'quasar/wrappers';
import { createHead } from '@vueuse/head';

// Vueアプリケーションにheadを追加するためのブートファイル
export default boot(({ app }) => {
  const head = createHead();
  app.use(head);
});
