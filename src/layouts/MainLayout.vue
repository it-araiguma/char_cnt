<template>
  <q-layout view="hhh lpR fff">

    <q-header elevated>
      <q-toolbar>
        <q-icon name="edit_note" size="md" class="cursor-pointer" @click="router.push('/')" />
        <q-toolbar-title class="cursor-pointer" @click="router.push('/')">
          {{ $t('layout.header.title') }}
        </q-toolbar-title>
        <q-btn flat dense no-caps icon="description" :label="$t('layout.footer.genko')" to="/genko" class="q-mr-sm" />
        <q-btn flat dense no-caps icon="assignment" :label="$t('layout.footer.report')" to="/report" class="q-mr-sm" />
        <q-space />
        <!-- 言語切り替えアイコンボタン -->
        <q-btn-dropdown flat dense dropdown-icon="" class="q-ml-md">
          <template #label>
            <q-icon name="language" size="md" />
          </template>
          <q-list>
            <q-item v-for="opt in localeOptions" :key="opt.value" clickable @click="changeLocale(opt.value)">
              <q-item-section>
                <span :class="{ 'text-primary': selectedLocale === opt.value }">{{ opt.label }}</span>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
      <ins ref="adSlot" class="adsbygoogle" style="display:block" data-ad-client="ca-pub-9551028273212184" data-ad-slot="6603589954"
        data-ad-format="auto" data-full-width-responsive="true"></ins>
    </q-page-container>

    <q-footer elevated class="bg-grey-8 text-white q-pt-xs q-pb-xs">
      <q-toolbar>
        <q-toolbar-title>
          <div class="copyright text-center q-mb-xs">
            <RouterLink to="/" class="q-mx-xs">{{ $t('layout.footer.home') }}</RouterLink>
            <RouterLink to="/genko" class="q-mx-xs">{{ $t('layout.footer.genko') }}</RouterLink>
            <RouterLink to="/report" class="q-mx-xs">{{ $t('layout.footer.report') }}</RouterLink>
            <RouterLink to="/privacy" class="q-mx-xs">{{ $t('layout.footer.privacy') }}</RouterLink>
          </div>
          <div class="copyright text-center">
            {{ $t('layout.footer.copyright') }}<a href="https://it-araiguma.com" target="_blank">ITアライグマ</a> {{
              $t('layout.footer.allRights') }}
          </div>
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>

  </q-layout>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { computed, nextTick, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { isSupportedLocale, replaceLocaleQuery, saveLocale, type SupportedLocale } from 'src/i18n';

defineOptions({
  name: 'MainLayout'
});

const { locale } = useI18n();
const router = useRouter();
const route = useRoute();
const adSlot = ref<HTMLElement | null>(null);

function initAdSense() {
  if (typeof window === 'undefined') {
    return;
  }
  if (adSlot.value?.getAttribute('data-adsbygoogle-status')) {
    return;
  }
  try {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  } catch (error) {
    console.warn('AdSense push failed:', error);
  }
}

onMounted(() => {
  void nextTick(() => {
    if (adSlot.value && adSlot.value.clientWidth > 0) {
      initAdSense();
    } else {
      window.requestAnimationFrame(() => {
        initAdSense();
      });
    }
  });
});

const localeOptions: { label: string; value: SupportedLocale }[] = [
  { label: '日本語', value: 'ja-JP' },
  { label: 'English', value: 'en-US' },
  { label: '中文', value: 'zh-CN' },
  { label: 'Français', value: 'fr-FR' },
  { label: 'Español', value: 'es-ES' }
];

const selectedLocale = computed(() => locale.value);

function changeLocale(val: SupportedLocale) {
  if (!isSupportedLocale(val)) {
    return;
  }
  locale.value = val;
  saveLocale(val);
  replaceLocaleQuery(route, router, val);
}
</script>
<style scoped>
.copyright {
  font-size: 14px;
}

.copyright>a {
  color: #fff;
}
</style>
