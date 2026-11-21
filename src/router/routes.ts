import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/IndexPage.vue') }],
  },
  {
    path: '/genko',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/features/GenkoCountPage.vue') }],
  },
  {
    path: '/report',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/features/ReportCountPage.vue') }],
  },
  {
    path: '/privacy',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/PrivacyPage.vue') }],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;
