import type { WritableComputedRef } from 'vue';
import type { RouteLocationNormalizedLoaded, Router } from 'vue-router';
import enUS from './en-US';
import jaJP from './ja-JP';
import zhCN from './zh-CN';
import frFR from './fr-FR';
import esES from './es-ES';

export const DEFAULT_LOCALE = 'ja-JP';
export const LOCALE_STORAGE_KEY = 'char-counter-locale';
export const SUPPORTED_LOCALES = ['ja-JP', 'en-US', 'zh-CN', 'fr-FR', 'es-ES'] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export function isSupportedLocale(val: unknown): val is SupportedLocale {
  return typeof val === 'string' && (SUPPORTED_LOCALES as readonly string[]).includes(val);
}

export function getSavedLocale(): SupportedLocale | null {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    const saved = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    return isSupportedLocale(saved) ? saved : null;
  } catch {
    return null;
  }
}

export function saveLocale(lang: SupportedLocale): void {
  if (typeof window === 'undefined') {
    return;
  }
  try {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, lang);
  } catch {
    // ignore storage errors
  }
}

export function getQueryLocaleFromLocation(): SupportedLocale | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const searchLang = new URLSearchParams(window.location.search).get('lang');
  if (isSupportedLocale(searchLang)) {
    return searchLang;
  }
  const hash = window.location.hash;
  const queryIndex = hash.indexOf('?');
  if (queryIndex !== -1) {
    const hashLang = new URLSearchParams(hash.slice(queryIndex)).get('lang');
    if (isSupportedLocale(hashLang)) {
      return hashLang;
    }
  }
  return null;
}

export function resolveInitialLocale(): SupportedLocale {
  const queryLocale = getQueryLocaleFromLocation();
  if (queryLocale) {
    saveLocale(queryLocale);
    return queryLocale;
  }
  const savedLocale = getSavedLocale();
  if (savedLocale) {
    return savedLocale;
  }
  return DEFAULT_LOCALE;
}

export function replaceLocaleQuery(
  route: RouteLocationNormalizedLoaded,
  router: Router,
  targetLocale: SupportedLocale
): void {
  const currentLang = Array.isArray(route.query.lang) ? route.query.lang[0] : route.query.lang;

  if (targetLocale === DEFAULT_LOCALE) {
    if ('lang' in route.query) {
      const restQuery = { ...route.query };
      delete restQuery.lang;
      void router.replace({ query: restQuery });
    }
    return;
  }

  if (currentLang !== targetLocale) {
    void router.replace({
      query: {
        ...route.query,
        lang: targetLocale
      }
    });
  }
}

export function syncLocaleWithRoute(
  route: RouteLocationNormalizedLoaded,
  router: Router,
  locale: WritableComputedRef<string>
): void {
  const rawRouteLang = Array.isArray(route.query.lang) ? route.query.lang[0] : route.query.lang;

  if (isSupportedLocale(rawRouteLang)) {
    locale.value = rawRouteLang;
    saveLocale(rawRouteLang);
    if (rawRouteLang === DEFAULT_LOCALE) {
      replaceLocaleQuery(route, router, DEFAULT_LOCALE);
    }
  } else {
    const savedLocale = getSavedLocale();
    const nextLocale = savedLocale ?? DEFAULT_LOCALE;
    locale.value = nextLocale;
    replaceLocaleQuery(route, router, nextLocale);
  }
}

export default {
  'ja-JP': jaJP,
  'en-US': enUS,
  'zh-CN': zhCN,
  'fr-FR': frFR,
  'es-ES': esES
};
