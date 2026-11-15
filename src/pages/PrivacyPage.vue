<template>
  <div class="q-pa-md">
    <div class="q-gutter-y-md column">
      <div class="q-gutter-md">
        <h1 class="text-h4 q-mb-none">
          {{ $t('privacyPolicy.title') }}
        </h1>
      </div>
      <div class="q-gutter-md">
        <div>
          {{ $t('privacyPolicy.intro') }}
        </div>
      </div>
      <div class="q-gutter-md">
        <div class="text-h5">{{ $t('privacyPolicy.section1.title') }}</div>
        <div>{{ $t('privacyPolicy.section1.intro') }}</div>
        <div class="text-h6">{{ $t('privacyPolicy.section1.cookieTitle') }}</div>
        <div>
          {{ $t('privacyPolicy.section1.cookieDesc') }}
        </div>
        <div>
          {{ $t('privacyPolicy.section1.cookiePurposesTitle') }}
        </div>
        <ul>
          <li>{{ $t('privacyPolicy.section1.cookiePurpose1') }}</li>
          <li>{{ $t('privacyPolicy.section1.cookiePurpose2') }}</li>
        </ul>
        <div>
          {{ $t('privacyPolicy.section1.cookieReject') }}
        </div>
      </div>
      <div class="q-gutter-md">
        <div class="text-h6">{{ $t('privacyPolicy.section1.analyticsTitle') }}</div>
        <div>
          {{ $t('privacyPolicy.section1.analyticsDesc1') }}
        </div>
        <i18n-t keypath="privacyPolicy.section1.analyticsPolicy" tag="div">
          <template #link>
            <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">
              {{ $t('privacyPolicy.section1.analyticsPolicyLink') }}
            </a>
          </template>
        </i18n-t>
        <i18n-t keypath="privacyPolicy.section1.analyticsOptout" tag="div">
          <template #link>
            <a href="https://support.google.com/analytics/answer/181881" target="_blank" rel="noopener noreferrer">
              {{ $t('privacyPolicy.section1.analyticsOptoutLink') }}
            </a>
          </template>
        </i18n-t>
      </div>
      <div class="q-gutter-md">
        <div class="text-h6">{{ $t('privacyPolicy.section1.adsenseTitle') }}</div>
        <div>
          {{ $t('privacyPolicy.section1.adsenseDesc1') }}
        </div>
        <i18n-t keypath="privacyPolicy.section1.adsensePolicy" tag="div">
          <template #link>
            <a href="https://support.google.com/adspolicy/answer/6008942" target="_blank" rel="noopener noreferrer">
              {{ $t('privacyPolicy.section1.adsensePolicyLink') }}
            </a>
          </template>
        </i18n-t>
        <i18n-t keypath="privacyPolicy.section1.adsenseOptout" tag="div">
          <template #link>
            <a href="https://myadcenter.google.com/home?sasb=true&ref=ad-settings" target="_blank" rel="noopener noreferrer">
              {{ $t('privacyPolicy.section1.adsenseOptoutLink') }}
            </a>
          </template>
        </i18n-t>
      </div>
      <div class="q-gutter-md">
        <div class="text-h5">{{ $t('privacyPolicy.section2.title') }}</div>
        <div>
          {{ $t('privacyPolicy.section2.desc') }}
        </div>
      </div>
      <div class="q-gutter-md">
        <div class="text-h5">{{ $t('privacyPolicy.section3.title') }}</div>
        <div>
          {{ $t('privacyPolicy.section3.desc') }}
        </div>
      </div>
      <div class="q-gutter-md">
        <div class="text-h5">{{ $t('privacyPolicy.section4.title') }}</div>
        <div>
          {{ $t('privacyPolicy.section4.desc') }}
        </div>
      </div>
      <div class="q-gutter-md">
        <div class="text-h5">{{ $t('privacyPolicy.section5.title') }}</div>
        <div>
          {{ $t('privacyPolicy.section5.desc') }}
        </div>
      </div>
      <div class="q-gutter-md">
        <div class="text-h5">{{ $t('privacyPolicy.section6.title') }}</div>
        <div>
          {{ $t('privacyPolicy.section6.desc') }}<br>
          <a href="https://it-araiguma.com/contact_form/" target="_blank" rel="noopener noreferrer">
            {{ $t('privacyPolicy.section6.contactLink') }}
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSeoMeta } from 'src/utils/seo';
import { syncLocaleWithRoute } from 'src/i18n';
import { useRouter, useRoute } from 'vue-router';

defineOptions({
  name: 'PrivacyPage'
});

// SEOメタタグを設定
useSeoMeta('privacy');

// i18nを初期化
const { locale } = useI18n();
const router = useRouter();
const route = useRoute();

// ページ読み込み時の処理
onMounted(() => {
  syncLocaleWithRoute(route, router, locale);
});
</script>
