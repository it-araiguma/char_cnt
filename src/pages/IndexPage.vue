<template>
  <div class="container q-pa-md">
    <div class="row justify-center">
      <div class="col-12 col-md-8">
        
        <q-card class="text-editor-card q-mb-md">
          <q-card-section>
            <h1 class="text-h5 q-mt-sm q-mb-md text-primary text-center">{{ $t('app.title') }}</h1>
            <q-input 
              v-model="text" 
              filled 
              type="textarea" 
              counter 
              rows="15"
              class="text-area"
              :placeholder="$t('app.input.placeholder')"
              bg-color="grey-1"
            >
              <template #counter>
                {{ metrics.totalChars }}
              </template>
            </q-input>
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md q-gutter-xs">
            <q-btn
              color="primary"
              :label="$t('app.input.copy')"
              @click="copyText"
              icon="content_copy"
              :disable="!text"
              class="q-px-md"
              flat
              v-ripple
            />
            <q-btn
              color="negative"
              :label="$t('app.input.clear')"
              @click="clearText"
              icon="delete_sweep"
              :disable="!text"
              class="q-px-md"
              flat
              v-ripple
            />
          </q-card-actions>
        </q-card>

        <!-- メインカウンター -->
        <div class="row q-col-gutter-md q-mb-md">
          <div v-for="item in primaryCounters" :key="item.key" class="col-12 col-sm-4">
            <q-card class="counter-card" :class="{ 'pulse-animation': item.value > 0 }">
              <q-card-section>
                <div class="row items-center justify-between no-wrap q-mb-xs">
                  <div class="text-subtitle2 text-grey-7">{{ item.label }}</div>
                  <q-icon
                    name="help_outline"
                    size="xs"
                    color="grey-6"
                    class="cursor-pointer q-ml-xs"
                    tabindex="0"
                    :aria-label="item.hint"
                  >
                    <q-tooltip max-width="240px">{{ item.hint }}</q-tooltip>
                  </q-icon>
                </div>
                <div class="row items-center">
                  <q-icon :name="item.icon" :color="item.color" size="sm" class="q-mr-sm" />
                  <div class="text-h4 text-weight-bold" :class="`text-${item.color}`">
                    {{ item.value }}
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 詳細カウンター（行数・段落・全角半角・バイト数） -->
        <div class="row q-col-gutter-sm">
          <div
            v-for="item in detailCounters"
            :key="item.key"
            :class="item.colClass"
          >
            <q-card class="detail-counter-card" flat bordered>
              <q-card-section class="q-pa-sm">
                <div class="row items-center justify-between no-wrap">
                  <div class="text-caption text-grey-7 ellipsis">{{ item.label }}</div>
                  <q-icon
                    name="help_outline"
                    size="14px"
                    color="grey-5"
                    class="cursor-pointer q-ml-xs"
                    tabindex="0"
                    :aria-label="item.hint"
                  >
                    <q-tooltip max-width="240px">{{ item.hint }}</q-tooltip>
                  </q-icon>
                </div>
                <div class="text-h6 text-weight-bold q-mt-xs" :class="item.textClass">
                  {{ item.value }}
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 用途別機能への導線 -->
        <q-card class="q-mt-lg feature-nav-card" flat bordered>
          <q-card-section>
            <div class="text-subtitle2 text-weight-bold text-grey-8 q-mb-xs">
              {{ $t('app.tools.title') }}
            </div>
            <q-item clickable v-ripple to="/genko" class="rounded-borders feature-item q-pa-sm">
              <q-item-section avatar>
                <q-avatar color="primary" text-color="white" icon="menu_book" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold text-primary text-subtitle1">
                  {{ $t('app.tools.genkoTitle') }}
                </q-item-label>
                <q-item-label caption class="text-grey-7">
                  {{ $t('app.tools.genkoDesc') }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-icon name="chevron_right" color="primary" />
              </q-item-section>
            </q-item>
            <q-item clickable v-ripple to="/report" class="rounded-borders feature-item q-pa-sm q-mt-sm">
              <q-item-section avatar>
                <q-avatar color="secondary" text-color="white" icon="assignment" />
              </q-item-section>
              <q-item-section>
                <q-item-label class="text-weight-bold text-secondary text-subtitle1">
                  {{ $t('app.tools.reportTitle') }}
                </q-item-label>
                <q-item-label caption class="text-grey-7">
                  {{ $t('app.tools.reportDesc') }}
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-icon name="chevron_right" color="secondary" />
              </q-item-section>
            </q-item>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useQuasar } from 'quasar';
import { useSeoMeta } from 'src/utils/seo';
import { analyzeText } from 'src/utils/charCount';
import { syncLocaleWithRoute } from 'src/i18n';
import { useRouter, useRoute } from 'vue-router';

defineOptions({
  name: 'IndexPage'
});

// SEOメタタグを設定
useSeoMeta('index');

const { t, locale } = useI18n();
const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const text = ref('');
const metrics = computed(() => analyzeText(text.value));

const primaryCounters = computed(() => [
  {
    key: 'totalChars',
    label: t('app.counter.characters'),
    hint: t('app.counter.charactersHint'),
    value: metrics.value.totalChars,
    icon: 'edit',
    color: 'primary'
  },
  {
    key: 'noLineBreaks',
    label: t('app.counter.noLineBreaks'),
    hint: t('app.counter.noLineBreaksHint'),
    value: metrics.value.charsWithoutLineBreaks,
    icon: 'format_align_left',
    color: 'teal'
  },
  {
    key: 'noSpaces',
    label: t('app.counter.noSpaces'),
    hint: t('app.counter.noSpacesHint'),
    value: metrics.value.charsWithoutSpaces,
    icon: 'edit_note',
    color: 'secondary'
  }
]);

const detailCounters = computed(() => [
  {
    key: 'linesWithEmpty',
    label: t('app.counter.linesWithEmpty'),
    hint: t('app.counter.linesWithEmptyHint'),
    value: metrics.value.lineCountWithEmpty,
    colClass: 'col-6 col-sm-4',
    textClass: 'text-dark'
  },
  {
    key: 'linesWithoutEmpty',
    label: t('app.counter.linesWithoutEmpty'),
    hint: t('app.counter.linesWithoutEmptyHint'),
    value: metrics.value.lineCountWithoutEmpty,
    colClass: 'col-6 col-sm-4',
    textClass: 'text-dark'
  },
  {
    key: 'paragraphs',
    label: t('app.counter.paragraphs'),
    hint: t('app.counter.paragraphsHint'),
    value: metrics.value.paragraphCount,
    colClass: 'col-12 col-sm-4',
    textClass: 'text-dark'
  },
  {
    key: 'fullWidth',
    label: t('app.counter.fullWidth'),
    hint: t('app.counter.fullWidthHint'),
    value: metrics.value.fullWidthChars,
    colClass: 'col-6 col-sm-3',
    textClass: 'text-primary'
  },
  {
    key: 'halfWidth',
    label: t('app.counter.halfWidth'),
    hint: t('app.counter.halfWidthHint'),
    value: metrics.value.halfWidthChars,
    colClass: 'col-6 col-sm-3',
    textClass: 'text-secondary'
  },
  {
    key: 'utf8Bytes',
    label: t('app.counter.utf8Bytes'),
    hint: t('app.counter.utf8BytesHint'),
    value: metrics.value.utf8Bytes,
    colClass: 'col-6 col-sm-3',
    textClass: 'text-grey-8'
  },
  {
    key: 'shiftJisBytes',
    label: t('app.counter.shiftJisBytes'),
    hint: t('app.counter.shiftJisBytesHint'),
    value: metrics.value.shiftJisBytes,
    colClass: 'col-6 col-sm-3',
    textClass: 'text-grey-8'
  }
]);

const clearText = () => {
  text.value = '';
};

const copyText = async () => {
  if (!text.value) return;
  try {
    await navigator.clipboard.writeText(text.value);
    $q.notify({
      type: 'positive',
      message: t('app.input.copied'),
      timeout: 2000
    });
  } catch (err) {
    console.error('Clipboard copy failed:', err);
  }
};

// ページ読み込み時の処理
onMounted(() => {
  syncLocaleWithRoute(route, router, locale);
});
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
}

.text-editor-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.text-editor-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.text-area {
  font-size: 16px;
}

.counter-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  height: 100%;
}

.counter-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
}

.detail-counter-card {
  border-radius: 8px;
  background-color: #fafafa;
  height: 100%;
}

.pulse-animation {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 149, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 149, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 149, 255, 0);
  }
}

.feature-nav-card {
  border-radius: 12px;
  background-color: #fafafa;
}

.feature-item {
  transition: all 0.2s ease;
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
}

.feature-item:hover {
  background-color: #f0f7ff;
  border-color: #90caf9;
}
</style>
