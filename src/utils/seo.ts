import { useI18n } from 'vue-i18n';
import { useHead } from '@vueuse/head';
import { computed } from 'vue';
import { useRouter } from 'vue-router';

// サポートされている言語のリスト
const supportedLocales = ['ja-JP', 'en-US', 'zh-CN', 'fr-FR', 'es-ES'];

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

  // 言語に基づいたタイトル、説明、キーワードを計算
  const title = computed(() => t(`seo.${pageName}.title`));
  const description = computed(() => t(`seo.${pageName}.description`));
  const keywords = computed(() => t(`seo.${pageName}.keywords`));

  // 現在のURL（ハッシュなし）を取得
  const currentUrl = computed(() => {
    const baseUrl = window.location.origin;
    return `${baseUrl}${currentPath.value}`;
  });

  // hreflangリンクを生成
  const generateHreflangLinks = () => {
    return supportedLocales.map(lang => {
      return {
        rel: 'alternate',
        hreflang: lang.toLowerCase(),
        href: `${currentUrl.value}?lang=${lang}`
      };
    });
  };

  // x-defaultのhreflangリンクを追加
  const getDefaultHreflangLink = () => {
    return {
      rel: 'alternate',
      hreflang: 'x-default',
      href: `${currentUrl.value}?lang=en-US`
    };
  };

  // メタタグを設定
  useHead(() => {
    const hreflangLinks = generateHreflangLinks();
    const defaultHreflangLink = getDefaultHreflangLink();

    return {
      htmlAttrs: {
        lang: locale.value
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
          property: 'og:locale',
          content: locale.value
        },
        {
          name: 'twitter:title',
          content: title.value
        },
        {
          name: 'twitter:description',
          content: description.value
        }
      ],
      link: [
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
