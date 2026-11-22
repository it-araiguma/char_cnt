<template>
  <div class="container q-pa-md">
    <div class="row justify-center">
      <div class="col-12 col-md-10 col-lg-8">
        <!-- ページタイトルと概要 -->
        <div class="text-center q-mb-md">
          <h1 class="text-h4 text-weight-bold text-primary q-my-xs">
            {{ $t('genko.title') }}
          </h1>
          <p class="text-subtitle1 text-grey-8 q-mb-none">
            {{ $t('genko.subtitle') }}
          </p>
        </div>

        <!-- テキスト入力カード -->
        <q-card class="text-editor-card q-mb-md">
          <q-card-section>
            <q-input
              v-model="text"
              filled
              type="textarea"
              counter
              rows="12"
              class="text-area"
              :placeholder="$t('genko.input.placeholder')"
              bg-color="grey-1"
            >
              <template #counter>
                {{ analysis.totalChars }}
              </template>
            </q-input>
          </q-card-section>

          <q-card-actions align="between" class="q-px-md q-pb-md">
            <div>
              <q-btn
                flat
                color="secondary"
                icon="auto_stories"
                :label="$t('genko.input.sample')"
                class="q-px-sm"
                @click="insertSampleText"
              />
            </div>
            <div class="row q-gutter-xs">
              <q-btn
                flat
                color="primary"
                icon="content_copy"
                :label="$t('genko.input.copy')"
                :disable="!text"
                class="q-px-sm"
                @click="copyText"
              />
              <q-btn
                flat
                color="negative"
                icon="delete_sweep"
                :label="$t('genko.input.clear')"
                :disable="!text"
                class="q-px-sm"
                @click="clearText"
              />
            </div>
          </q-card-actions>
        </q-card>

        <!-- 基本文字数・行数サマリ -->
        <div class="row q-col-gutter-sm q-mb-sm">
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('genko.summary.totalChars') }}</div>
                <div class="text-h6 text-weight-bold text-primary">{{ analysis.totalChars }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('genko.summary.noSpaces') }}</div>
                <div class="text-h6 text-weight-bold text-secondary">{{ analysis.charsWithoutSpaces }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('genko.summary.totalLines') }}</div>
                <div class="text-h6 text-weight-bold text-accent">{{ analysis.totalLines }}</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('genko.summary.rawLines') }}</div>
                <div class="text-h6 text-weight-bold text-dark">{{ analysis.rawLineCount }}</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- 計算オプション -->
        <div class="row items-center justify-end q-mb-md">
          <q-toggle
            v-model="halfWidthAsTwoPerCell"
            color="primary"
            dense
            :label="$t('genko.options.halfWidthTwoPerCell')"
          />
        </div>

        <!-- 400字詰め原稿用紙換算カード -->
        <q-card class="q-mb-md genko-card" :class="{ 'pulse-border': analysis.totalChars > 0 }">
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center">
                <q-icon name="menu_book" color="primary" size="sm" class="q-mr-sm" />
                <span class="text-subtitle1 text-weight-bold text-primary">
                  {{ $t('genko.cards.preset400') }}
                </span>
              </div>
              <q-badge v-if="analysis.totalChars > 0 && analysis.genko400.isExactSheet" color="positive">
                {{ $t('genko.cards.exactBadge') }}
              </q-badge>
            </div>

            <div class="row q-col-gutter-md items-stretch">
              <!-- 実用紙換算 -->
              <div class="col-12 col-sm-6">
                <div class="calc-box actual-box">
                  <div class="calc-label text-weight-bold text-primary">
                    <q-icon name="fact_check" size="xs" class="q-mr-xs" />
                    {{ $t('genko.cards.actualTitle') }}
                  </div>
                  <div class="calc-main text-primary text-weight-bolder">
                    {{ analysis.genko400.actualSheets }}
                    <span class="calc-unit">{{ $t('genko.cards.sheetsUnit') }}</span>
                  </div>
                  <div class="calc-detail text-grey-8">
                    <span v-if="analysis.totalChars === 0">-</span>
                    <span v-else-if="analysis.genko400.isExactSheet">
                      {{ analysis.genko400.actualSheets }}{{ $t('genko.cards.sheetsUnit') }}（{{ $t('genko.cards.exactBadge') }}）
                    </span>
                    <span v-else>
                      {{
                        $t('genko.cards.remainderFormat', {
                          full: analysis.genko400.actualFullSheets,
                          remainder: analysis.genko400.actualRemainingLines,
                          unit: $t('genko.cards.linesUnit')
                        })
                      }}
                    </span>
                  </div>
                  <div class="text-caption text-grey-6 q-mt-xs">
                    {{ $t('genko.cards.actualDesc') }}
                  </div>
                </div>
              </div>

              <!-- 文字数ベース換算 -->
              <div class="col-12 col-sm-6">
                <div class="calc-box char-box">
                  <div class="calc-label text-weight-bold text-secondary">
                    <q-icon name="calculate" size="xs" class="q-mr-xs" />
                    {{ $t('genko.cards.charTitle') }}
                  </div>
                  <div class="calc-main text-secondary text-weight-bolder">
                    {{ analysis.genko400.rawSheets }}
                    <span class="calc-unit">{{ $t('genko.cards.sheetsUnit') }}</span>
                  </div>
                  <div class="calc-detail text-grey-8">
                    <span v-if="analysis.totalChars === 0">-</span>
                    <span v-else>
                      {{
                        $t('genko.cards.remainderFormat', {
                          full: analysis.genko400.charFullSheets,
                          remainder: analysis.genko400.charRemainingChars,
                          unit: $t('genko.cards.charsUnit')
                        })
                      }}
                    </span>
                  </div>
                  <div class="text-caption text-grey-6 q-mt-xs">
                    {{ $t('genko.cards.charDesc') }}
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- 200字詰め原稿用紙換算カード -->
        <q-card class="q-mb-md genko-card">
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center">
                <q-icon name="import_contacts" color="teal" size="sm" class="q-mr-sm" />
                <span class="text-subtitle1 text-weight-bold text-teal">
                  {{ $t('genko.cards.preset200') }}
                </span>
              </div>
              <q-badge v-if="analysis.totalChars > 0 && analysis.genko200.isExactSheet" color="positive">
                {{ $t('genko.cards.exactBadge') }}
              </q-badge>
            </div>

            <div class="row q-col-gutter-md items-stretch">
              <!-- 実用紙換算 -->
              <div class="col-12 col-sm-6">
                <div class="calc-box actual-box">
                  <div class="calc-label text-weight-bold text-teal">
                    <q-icon name="fact_check" size="xs" class="q-mr-xs" />
                    {{ $t('genko.cards.actualTitle') }}
                  </div>
                  <div class="calc-main text-teal text-weight-bolder">
                    {{ analysis.genko200.actualSheets }}
                    <span class="calc-unit">{{ $t('genko.cards.sheetsUnit') }}</span>
                  </div>
                  <div class="calc-detail text-grey-8">
                    <span v-if="analysis.totalChars === 0">-</span>
                    <span v-else-if="analysis.genko200.isExactSheet">
                      {{ analysis.genko200.actualSheets }}{{ $t('genko.cards.sheetsUnit') }}（{{ $t('genko.cards.exactBadge') }}）
                    </span>
                    <span v-else>
                      {{
                        $t('genko.cards.remainderFormat', {
                          full: analysis.genko200.actualFullSheets,
                          remainder: analysis.genko200.actualRemainingLines,
                          unit: $t('genko.cards.linesUnit')
                        })
                      }}
                    </span>
                  </div>
                  <div class="text-caption text-grey-6 q-mt-xs">
                    {{ $t('genko.cards.actualDesc') }}
                  </div>
                </div>
              </div>

              <!-- 文字数ベース換算 -->
              <div class="col-12 col-sm-6">
                <div class="calc-box char-box">
                  <div class="calc-label text-weight-bold text-grey-8">
                    <q-icon name="calculate" size="xs" class="q-mr-xs" />
                    {{ $t('genko.cards.charTitle') }}
                  </div>
                  <div class="calc-main text-grey-8 text-weight-bolder">
                    {{ analysis.genko200.rawSheets }}
                    <span class="calc-unit">{{ $t('genko.cards.sheetsUnit') }}</span>
                  </div>
                  <div class="calc-detail text-grey-8">
                    <span v-if="analysis.totalChars === 0">-</span>
                    <span v-else>
                      {{
                        $t('genko.cards.remainderFormat', {
                          full: analysis.genko200.charFullSheets,
                          remainder: analysis.genko200.charRemainingChars,
                          unit: $t('genko.cards.charsUnit')
                        })
                      }}
                    </span>
                  </div>
                  <div class="text-caption text-grey-6 q-mt-xs">
                    {{ $t('genko.cards.charDesc') }}
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- カスタム用紙設定アコーディオン -->
        <q-expansion-item
          icon="tune"
          :label="$t('genko.custom.title')"
          class="q-mb-md bg-white rounded-borders shadow-1"
          header-class="text-weight-bold text-grey-8"
        >
          <q-card>
            <q-card-section>
              <div class="row q-col-gutter-md items-center">
                <div class="col-12 col-sm-5">
                  <q-input
                    v-model.number="customInput.charsPerLine"
                    type="number"
                    :min="GENKO_MIN_GRID"
                    :max="GENKO_MAX_GRID"
                    step="1"
                    dense
                    outlined
                    hide-bottom-space
                    :rules="[validateGridValue]"
                    :label="$t('genko.custom.charsPerLine')"
                  />
                </div>
                <div class="col-12 col-sm-5">
                  <q-input
                    v-model.number="customInput.linesPerPage"
                    type="number"
                    :min="GENKO_MIN_GRID"
                    :max="GENKO_MAX_GRID"
                    step="1"
                    dense
                    outlined
                    hide-bottom-space
                    :rules="[validateGridValue]"
                    :label="$t('genko.custom.linesPerPage')"
                  />
                </div>
                <div class="col-12 col-sm-2 text-right">
                  <q-btn flat dense color="grey-7" :label="$t('genko.custom.reset')" @click="resetCustomSetting" />
                </div>
              </div>

              <!-- カスタム計算結果 -->
              <div class="row q-col-gutter-md q-mt-xs">
                <div class="col-12 col-sm-6">
                  <div class="calc-box actual-box">
                    <div class="calc-label text-weight-bold text-primary">
                      {{ $t('genko.cards.actualTitle') }}
                    </div>
                    <div class="calc-main text-primary text-weight-bolder">
                      {{ analysis.custom.actualSheets }}
                      <span class="calc-unit">{{ $t('genko.cards.sheetsUnit') }}</span>
                    </div>
                    <div class="calc-detail text-grey-8">
                      <span v-if="analysis.totalChars === 0">-</span>
                      <span v-else-if="analysis.custom.isExactSheet">
                        {{ analysis.custom.actualSheets }}{{ $t('genko.cards.sheetsUnit') }}
                      </span>
                      <span v-else>
                        {{
                          $t('genko.cards.remainderFormat', {
                            full: analysis.custom.actualFullSheets,
                            remainder: analysis.custom.actualRemainingLines,
                            unit: $t('genko.cards.linesUnit')
                          })
                        }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="col-12 col-sm-6">
                  <div class="calc-box char-box">
                    <div class="calc-label text-weight-bold text-secondary">
                      {{ $t('genko.cards.charTitle') }}
                    </div>
                    <div class="calc-main text-secondary text-weight-bolder">
                      {{ analysis.custom.rawSheets }}
                      <span class="calc-unit">{{ $t('genko.cards.sheetsUnit') }}</span>
                    </div>
                    <div class="calc-detail text-grey-8">
                      <span v-if="analysis.totalChars === 0">-</span>
                      <span v-else>
                        {{
                          $t('genko.cards.remainderFormat', {
                            full: analysis.custom.charFullSheets,
                            remainder: analysis.custom.charRemainingChars,
                            unit: $t('genko.cards.charsUnit')
                          })
                        }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </q-expansion-item>

        <!-- 原稿用紙の書き方ガイド（解説コンテンツ・SEO） -->
        <q-card class="q-mb-md guide-card">
          <q-card-section>
            <div class="row items-center q-mb-sm">
              <q-icon name="school" color="primary" size="sm" class="q-mr-sm" />
              <h2 class="text-h6 text-weight-bold text-dark q-my-none">
                {{ $t('genko.guide.title') }}
              </h2>
            </div>
            <p class="text-caption text-grey-7 q-mb-md">
              {{ $t('genko.guide.subtitle') }}
            </p>

            <q-list separator class="rounded-borders">
              <!-- ルール1: 題名・氏名・段落 -->
              <q-expansion-item
                default-opened
                header-class="text-weight-bold text-primary"
                :label="$t('genko.guide.rule1Title')"
              >
                <q-card>
                  <q-card-section class="guide-body text-body2 text-grey-9">
                    <div v-for="(line, idx) in rule1Lines" :key="idx" class="q-mb-xs">
                      {{ line }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- ルール2: 句読点・禁則 -->
              <q-expansion-item
                default-opened
                header-class="text-weight-bold text-primary"
                :label="$t('genko.guide.rule2Title')"
              >
                <q-card>
                  <q-card-section class="guide-body text-body2 text-grey-9">
                    <div v-for="(line, idx) in rule2Lines" :key="idx" class="q-mb-xs">
                      {{ line }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- ルール3: 会話文 -->
              <q-expansion-item
                default-opened
                header-class="text-weight-bold text-primary"
                :label="$t('genko.guide.rule3Title')"
              >
                <q-card>
                  <q-card-section class="guide-body text-body2 text-grey-9">
                    <div v-for="(line, idx) in rule3Lines" :key="idx" class="q-mb-xs">
                      {{ line }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <!-- ルール4: 数字・英字 -->
              <q-expansion-item
                default-opened
                header-class="text-weight-bold text-primary"
                :label="$t('genko.guide.rule4Title')"
              >
                <q-card>
                  <q-card-section class="guide-body text-body2 text-grey-9">
                    <div v-for="(line, idx) in rule4Lines" :key="idx" class="q-mb-xs">
                      {{ line }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </q-list>

            <!-- 文字数・枚数対応目安表 -->
            <div class="q-mt-lg">
              <h3 class="text-subtitle1 text-weight-bold text-dark q-mb-sm">
                {{ $t('genko.guide.tableTitle') }}
              </h3>
              <q-markup-table flat bordered dense class="conversion-table">
                <thead>
                  <tr class="bg-grey-2">
                    <th class="text-left">{{ $t('genko.guide.tableHeaderChars') }}</th>
                    <th class="text-center">{{ $t('genko.guide.tableHeaderSheets') }}</th>
                    <th class="text-left">{{ $t('genko.guide.tableHeaderPurpose') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in conversionRows" :key="idx">
                    <td class="text-weight-bold text-primary">{{ row.chars }}</td>
                    <td class="text-center text-weight-bold">{{ row.sheets }}</td>
                    <td class="text-grey-9">{{ row.purpose }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </div>
          </q-card-section>
        </q-card>

        <!-- 他のツールへのナビゲーション -->
        <div class="row justify-center q-gutter-sm q-my-lg">
          <q-btn
            outline
            color="primary"
            icon="arrow_back"
            :label="$t('layout.footer.home')"
            to="/"
            class="q-px-lg"
          />
          <q-btn
            outline
            color="secondary"
            icon="assignment"
            :label="$t('layout.footer.report')"
            to="/report"
            class="q-px-lg"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { useSeoMeta } from 'src/utils/seo';
import { syncLocaleWithRoute } from 'src/i18n';
import {
  analyzeGenko,
  GENKO_MIN_GRID,
  GENKO_MAX_GRID,
  GENKO_DEFAULT_CHARS_PER_LINE,
  GENKO_DEFAULT_LINES_PER_PAGE,
  isValidGenkoGridValue,
  type GenkoSetting
} from 'src/utils/genkoCount';

defineOptions({
  name: 'GenkoCountPage'
});

// SEOメタタグ設定
useSeoMeta('genko');

const { t, locale } = useI18n();
const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const text = ref('');
const halfWidthAsTwoPerCell = ref(true);

const customInput = reactive<{ charsPerLine: number | string; linesPerPage: number | string }>({
  charsPerLine: GENKO_DEFAULT_CHARS_PER_LINE,
  linesPerPage: GENKO_DEFAULT_LINES_PER_PAGE
});

// 不正値入力中は直前の有効値（初期値 20）を維持して計算が破綻しないようにする
const customSetting = reactive<GenkoSetting>({
  charsPerLine: GENKO_DEFAULT_CHARS_PER_LINE,
  linesPerPage: GENKO_DEFAULT_LINES_PER_PAGE
});

watch(
  () => customInput.charsPerLine,
  (val) => {
    if (isValidGenkoGridValue(val)) {
      customSetting.charsPerLine = val;
    }
  }
);

watch(
  () => customInput.linesPerPage,
  (val) => {
    if (isValidGenkoGridValue(val)) {
      customSetting.linesPerPage = val;
    }
  }
);

const validateGridValue = (val: unknown): true | string => {
  if (isValidGenkoGridValue(val)) {
    return true;
  }
  return t('genko.custom.invalidRange', {
    min: GENKO_MIN_GRID,
    max: GENKO_MAX_GRID
  });
};

const resetCustomSetting = () => {
  customInput.charsPerLine = GENKO_DEFAULT_CHARS_PER_LINE;
  customInput.linesPerPage = GENKO_DEFAULT_LINES_PER_PAGE;
  customSetting.charsPerLine = GENKO_DEFAULT_CHARS_PER_LINE;
  customSetting.linesPerPage = GENKO_DEFAULT_LINES_PER_PAGE;
};

// 計算結果
const analysis = computed(() => {
  return analyzeGenko(text.value, customSetting, {
    halfWidthAsTwoPerCell: halfWidthAsTwoPerCell.value
  });
});

const clearText = () => {
  text.value = '';
};

const copyText = async () => {
  if (!text.value) return;
  try {
    await navigator.clipboard.writeText(text.value);
    $q.notify({
      type: 'positive',
      message: t('genko.input.copied'),
      timeout: 2000
    });
  } catch (err) {
    console.error('Clipboard copy failed:', err);
  }
};

const insertSampleText = () => {
  text.value =
    '　吾輩は猫である。名前はまだ無い。\n' +
    '　どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。吾輩はここで始めて人間というものを見た。しかもあとで聞くとそれは書生という人間中で一番獰悪な種族であったそうだ。\n' +
    '　この書生というのは時々我々を捕えて煮て食うという話である。しかしその当時は何という考もなかったから別段恐しいとも思わなかった。ただ彼の掌に載せられてスーと持ち上げられた時何だかフワフワした感じがあったばかりである。';
};

const rule1Lines = computed(() => (t('genko.guide.rule1Body') as string).split('\n'));
const rule2Lines = computed(() => (t('genko.guide.rule2Body') as string).split('\n'));
const rule3Lines = computed(() => (t('genko.guide.rule3Body') as string).split('\n'));
const rule4Lines = computed(() => (t('genko.guide.rule4Body') as string).split('\n'));

const conversionRows = computed(() => [
  { chars: '400字', sheets: '1枚', purpose: '読書感想文（低学年）、ミニ作文' },
  { chars: '800字', sheets: '2枚', purpose: '高校入試小論文、短めの読書感想文' },
  { chars: '1,200字', sheets: '3枚', purpose: '大学入試小論文、全国コンクール規定（3枚以内）' },
  { chars: '2,000字', sheets: '5枚', purpose: '大学レポート、高校生規定（5枚以内）' },
  { chars: '4,000字', sheets: '10枚', purpose: '短編小説、学術レポート' },
  { chars: '8,000字', sheets: '20枚', purpose: '中編小説、卒業論文の準備章' }
]);

onMounted(() => {
  syncLocaleWithRoute(route, router, locale);
});
</script>

<style scoped>
.container {
  max-width: 1000px;
  margin: 0 auto;
}

.text-editor-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.text-area {
  font-size: 1rem;
  line-height: 1.6;
}

.summary-mini-card {
  border-radius: 8px;
  background-color: #fafafa;
  border: 1px solid #e0e0e0;
}

.genko-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.pulse-border {
  border-color: var(--q-primary);
}

.calc-box {
  padding: 16px;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.actual-box {
  background: #f0f7ff;
  border: 1px solid #cce3ff;
}

.char-box {
  background: #fdfaf3;
  border: 1px solid #fae6cb;
}

.calc-label {
  font-size: 0.95rem;
  margin-bottom: 4px;
}

.calc-main {
  font-size: 2.2rem;
  line-height: 1.1;
  margin: 6px 0;
}

.calc-unit {
  font-size: 1.1rem;
  font-weight: normal;
  margin-left: 2px;
}

.calc-detail {
  font-size: 0.9rem;
  font-weight: 500;
}

.guide-card {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.guide-body {
  line-height: 1.7;
}

.conversion-table {
  border-radius: 8px;
  overflow: hidden;
}
</style>
