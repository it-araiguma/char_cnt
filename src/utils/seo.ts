import { useI18n } from 'vue-i18n';
import { useHead } from '@vueuse/head';
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import {
  DEFAULT_LOCALE,
  SUPPORTED_LOCALES,
  isSupportedLocale,
  type SupportedLocale
} from 'src/i18n';

const DEFAULT_BASE_URL = 'https://count.it-araiguma.com';

/**
 * 言語に応じた正規URLを生成する（既定言語 ja-JP は ?lang= を付けない）
 */
export function buildLocalizedUrl(baseUrl: string, path: string, lang: SupportedLocale): string {
  const normalizedPath = path || '/';
  if (lang === DEFAULT_LOCALE) {
    return `${baseUrl}${normalizedPath}`;
  }
  return `${baseUrl}${normalizedPath}?lang=${encodeURIComponent(lang)}`;
}

/**
 * ロケール表記（例: ja-JP）を OGP 仕様の形式（例: ja_JP）へ変換する
 */
export function toOgLocale(lang: SupportedLocale): string {
  return lang.replace(/-/g, '_');
}

/**
 * SEOメタタグを設定するためのユーティリティ関数
 * @param pageName - ページ名（'index'や'privacy'など）
 */
export function useSeoMeta(pageName: string) {
  const { t, locale } = useI18n();
  const router = useRouter();

  // 現在のルートパスを取得
  const currentPath = computed(() => {
    return router.currentRoute.value.path;
  });

  // 現在の有効ロケールを取得
  const currentLocale = computed<SupportedLocale>(() => {
    return isSupportedLocale(locale.value) ? locale.value : DEFAULT_LOCALE;
  });

  // 言語に基づいたタイトル、説明、キーワードを計算
  const title = computed(() => t(`seo.${pageName}.title`));
  const description = computed(() => t(`seo.${pageName}.description`));
  const keywords = computed(() => t(`seo.${pageName}.keywords`));

  // ベースURLを取得
  const getBaseUrl = () => {
    return typeof window !== 'undefined' ? window.location.origin : DEFAULT_BASE_URL;
  };

  // hreflangリンクを生成
  const generateHreflangLinks = (baseUrl: string) => {
    return SUPPORTED_LOCALES.map(lang => {
      return {
        rel: 'alternate',
        hreflang: lang.toLowerCase(),
        href: buildLocalizedUrl(baseUrl, currentPath.value, lang)
      };
    });
  };

  // x-defaultのhreflangリンクを追加（既定言語の正規URL）
  const getDefaultHreflangLink = (baseUrl: string) => {
    return {
      rel: 'alternate',
      hreflang: 'x-default',
      href: buildLocalizedUrl(baseUrl, currentPath.value, DEFAULT_LOCALE)
    };
  };

  // メタタグを設定
  useHead(() => {
    const baseUrl = getBaseUrl();
    const canonicalUrl = buildLocalizedUrl(baseUrl, currentPath.value, currentLocale.value);
    const hreflangLinks = generateHreflangLinks(baseUrl);
    const defaultHreflangLink = getDefaultHreflangLink(baseUrl);
    const ogImage = `${baseUrl}/icons/icon-512x512.png`;
    const alternateOgLocales = SUPPORTED_LOCALES
      .filter(lang => lang !== currentLocale.value)
      .map(lang => ({
        key: `og:locale:alternate:${lang}`,
        property: 'og:locale:alternate',
        content: toOgLocale(lang)
      }));

    return {
      htmlAttrs: {
        lang: currentLocale.value
      },
      title: title.value,
      meta: [
        {
          name: 'description',
          content: description.value
        },
        {
          name: 'keywords',
          content: keywords.value
        },
        {
          property: 'og:title',
          content: title.value
        },
        {
          property: 'og:description',
          content: description.value
        },
        {
          property: 'og:type',
          content: 'website'
        },
        {
          property: 'og:url',
          content: canonicalUrl
        },
        {
          property: 'og:image',
          content: ogImage
        },
        {
          property: 'og:site_name',
          content: t('layout.header.title')
        },
        {
          property: 'og:locale',
          content: toOgLocale(currentLocale.value)
        },
        ...alternateOgLocales,
        {
          name: 'twitter:card',
          content: 'summary'
        },
        {
          name: 'twitter:title',
          content: title.value
        },
        {
          name: 'twitter:description',
          content: description.value
        },
        {
          name: 'twitter:image',
          content: ogImage
        }
      ],
      link: [
        {
          rel: 'canonical',
          href: canonicalUrl
        },
        ...hreflangLinks,
        defaultHreflangLink
      ]
    };
  });

  return {
    title,
    description,
    keywords
  };
}
