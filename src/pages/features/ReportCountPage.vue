<template>
  <div class="container q-pa-md">
    <div class="row justify-center">
      <div class="col-12 col-md-10 col-lg-8">
        <!-- ページタイトルと概要 -->
        <div class="text-center q-mb-md">
          <h1 class="text-h4 text-weight-bold text-primary q-my-xs">
            {{ $t('report.title') }}
          </h1>
          <p class="text-subtitle1 text-grey-8 q-mb-none">
            {{ $t('report.subtitle') }}
          </p>
        </div>

        <!-- 目標文字数・判定基準設定カード -->
        <q-card class="q-mb-md target-card">
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center">
                <q-icon name="flag" color="primary" size="sm" class="q-mr-sm" />
                <span class="text-subtitle1 text-weight-bold text-dark">
                  {{ $t('report.target.title') }}
                </span>
              </div>
              <q-toggle
                v-model="excludeSpaces"
                dense
                color="secondary"
                :label="$t('report.target.excludeSpaces')"
              />
            </div>

            <!-- プリセットと任意入力 -->
            <div class="row q-col-gutter-sm items-center q-mb-md">
              <div class="col-12 col-sm-auto">
                <div class="row q-gutter-xs">
                  <q-btn
                    v-for="preset in REPORT_PRESETS"
                    :key="preset"
                    :outline="targetChars !== preset"
                    :unelevated="targetChars === preset"
                    color="primary"
                    no-caps
                    dense
                    class="q-px-md preset-btn"
                    :label="$t('report.target.presetFormat', { count: preset.toLocaleString() })"
                    @click="selectPreset(preset)"
                  />
                </div>
              </div>
              <div class="col-12 col-sm">
                <q-input
                  v-model.number="targetCharsInput"
                  type="number"
                  min="1"
                  max="1000000"
                  dense
                  outlined
                  :label="$t('report.target.customLabel')"
                  :suffix="$t('report.units.chars')"
                  @update:model-value="onCustomTargetChange"
                />
              </div>
            </div>

            <!-- 達成判定モード選択 -->
            <div>
              <div class="text-caption text-grey-7 q-mb-xs">
                {{ $t('report.rule.title') }}
              </div>
              <q-btn-toggle
                v-model="ruleMode"
                spread
                no-caps
                unelevated
                toggle-color="primary"
                color="grey-2"
                text-color="grey-9"
                class="rule-toggle"
                :options="[
                  { label: $t('report.rule.around10'), value: 'around10' },
                  { label: $t('report.rule.min80'), value: 'min80' },
                  { label: $t('report.rule.max100'), value: 'max100' }
                ]"
              />
            </div>
          </q-card-section>
        </q-card>

        <!-- 達成判定・進捗プログレスカード -->
        <q-card class="q-mb-md status-card" :class="statusCardClass">
          <q-card-section>
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-baseline q-gutter-x-sm">
                <span class="text-h4 text-weight-bolder" :class="statusTextClass">
                  {{ analysis.activeCount.toLocaleString() }}
                </span>
                <span class="text-subtitle1 text-grey-7">
                  / {{ analysis.targetChars.toLocaleString() }} {{ $t('report.units.chars') }}
                </span>
                <span class="text-subtitle2 text-weight-bold text-grey-8">
                  ({{ analysis.progressPercent }}%)
                </span>
              </div>

              <q-badge
                :color="statusBadgeColor"
                class="status-badge text-subtitle1 text-weight-bold q-px-md q-py-xs"
              >
                <q-icon :name="statusIcon" size="xs" class="q-mr-xs" />
                {{ statusLabel }}
              </q-badge>
            </div>

            <q-linear-progress
              :value="analysis.progressRatio"
              :color="statusBadgeColor"
              track-color="grey-3"
              size="14px"
              rounded
              class="q-mb-sm"
            />

            <div class="row items-center justify-between text-body2">
              <div class="text-weight-medium" :class="statusTextClass">
                {{ statusMessage }}
              </div>
              <div class="text-caption text-grey-7">
                {{
                  $t('report.status.rangeFormat', {
                    min: analysis.evaluation.minChars.toLocaleString(),
                    max: analysis.evaluation.maxChars.toLocaleString()
                  })
                }}
              </div>
            </div>
          </q-card-section>
        </q-card>

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
              :placeholder="$t('report.input.placeholder')"
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
                :label="$t('report.input.sample')"
                class="q-px-sm"
                @click="insertSampleText"
              />
            </div>
            <div class="row q-gutter-xs">
              <q-btn
                flat
                color="primary"
                icon="content_copy"
                :label="$t('report.input.copy')"
                :disable="!text"
                class="q-px-sm"
                @click="copyText"
              />
              <q-btn
                flat
                color="negative"
                icon="delete_sweep"
                :label="$t('report.input.clear')"
                :disable="!text"
                class="q-px-sm"
                @click="clearText"
              />
            </div>
          </q-card-actions>
        </q-card>

        <!-- 基本文字数・行数サマリ -->
        <div class="row q-col-gutter-sm q-mb-md">
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('report.summary.totalChars') }}</div>
                <div class="text-h6 text-weight-bold text-primary">
                  {{ analysis.totalChars.toLocaleString() }}
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('report.summary.noSpaces') }}</div>
                <div class="text-h6 text-weight-bold text-secondary">
                  {{ analysis.charsWithoutSpaces.toLocaleString() }}
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('report.summary.paragraphs') }}</div>
                <div class="text-h6 text-weight-bold text-accent">
                  {{ analysis.paragraphCount.toLocaleString() }}
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-6 col-sm-3">
            <q-card class="summary-mini-card">
              <q-card-section class="q-pa-sm text-center">
                <div class="text-caption text-grey-7">{{ $t('report.summary.genkoSheets') }}</div>
                <div class="text-h6 text-weight-bold text-dark">
                  {{ analysis.genko400Sheets }}
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- レポート・小論文の文字数ルール解説（SEO・判断基準ガイド） -->
        <q-card class="q-mb-md guide-card">
          <q-card-section>
            <div class="row items-center q-mb-sm">
              <q-icon name="school" color="primary" size="sm" class="q-mr-sm" />
              <h2 class="text-h6 text-weight-bold text-dark q-my-none">
                {{ $t('report.guide.title') }}
              </h2>
            </div>
            <p class="text-caption text-grey-7 q-mb-md">
              {{ $t('report.guide.subtitle') }}
            </p>

            <!-- 含める・含めない判断基準テーブル -->
            <h3 class="text-subtitle1 text-weight-bold text-dark q-mb-sm">
              {{ $t('report.guide.criteriaTitle') }}
            </h3>
            <q-markup-table flat bordered dense class="conversion-table q-mb-lg">
              <thead>
                <tr class="bg-grey-2">
                  <th class="text-left">{{ $t('report.guide.criteriaHeaderItem') }}</th>
                  <th class="text-center">{{ $t('report.guide.criteriaHeaderInclude') }}</th>
                  <th class="text-left">{{ $t('report.guide.criteriaHeaderNote') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in criteriaRows" :key="idx">
                  <td class="text-weight-bold text-dark">{{ row.item }}</td>
                  <td class="text-center">
                    <q-badge :color="row.badgeColor">{{ row.include }}</q-badge>
                  </td>
                  <td class="text-grey-9">{{ row.note }}</td>
                </tr>
              </tbody>
            </q-markup-table>

            <!-- 指定表現別の目安解説 -->
            <q-list separator class="rounded-borders q-mb-lg">
              <q-expansion-item
                default-opened
                header-class="text-weight-bold text-primary"
                :label="$t('report.guide.rule1Title')"
              >
                <q-card>
                  <q-card-section class="guide-body text-body2 text-grey-9">
                    <div v-for="(line, idx) in rule1Lines" :key="idx" class="q-mb-xs">
                      {{ line }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

              <q-expansion-item
                default-opened
                header-class="text-weight-bold text-primary"
                :label="$t('report.guide.rule2Title')"
              >
                <q-card>
                  <q-card-section class="guide-body text-body2 text-grey-9">
                    <div v-for="(line, idx) in rule2Lines" :key="idx" class="q-mb-xs">
                      {{ line }}
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>
            </q-list>

            <!-- 文字数目安表 -->
            <div>
              <h3 class="text-subtitle1 text-weight-bold text-dark q-mb-sm">
                {{ $t('report.guide.tableTitle') }}
              </h3>
              <q-markup-table flat bordered dense class="conversion-table">
                <thead>
                  <tr class="bg-grey-2">
                    <th class="text-left">{{ $t('report.guide.tableHeaderChars') }}</th>
                    <th class="text-center">{{ $t('report.guide.tableHeaderVolume') }}</th>
                    <th class="text-left">{{ $t('report.guide.tableHeaderPurpose') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in guideTableRows" :key="idx">
                    <td class="text-weight-bold text-primary">{{ row.chars }}</td>
                    <td class="text-center text-weight-bold">{{ row.volume }}</td>
                    <td class="text-grey-9">{{ row.purpose }}</td>
                  </tr>
                </tbody>
              </q-markup-table>
            </div>
          </q-card-section>
        </q-card>

        <!-- 関連ツールへのナビゲーション -->
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
            icon="menu_book"
            :label="$t('layout.footer.genko')"
            to="/genko"
            class="q-px-lg"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { useQuasar } from 'quasar';
import { useSeoMeta } from 'src/utils/seo';
import { syncLocaleWithRoute } from 'src/i18n';
import {
  analyzeReport,
  normalizeTargetChars,
  REPORT_PRESETS,
  type ReportRuleMode
} from 'src/utils/reportCount';

defineOptions({
  name: 'ReportCountPage'
});

useSeoMeta('report');

const { t, locale } = useI18n();
const router = useRouter();
const route = useRoute();
const $q = useQuasar();

const text = ref('');
const targetChars = ref(2000);
const targetCharsInput = ref<number | string>(2000);
const ruleMode = ref<ReportRuleMode>('around10');
const excludeSpaces = ref(false);

const selectPreset = (preset: number) => {
  targetChars.value = preset;
  targetCharsInput.value = preset;
};

const onCustomTargetChange = (val: string | number | null) => {
  const num = typeof val === 'number' ? val : Number(val);
  if (Number.isFinite(num) && num >= 1) {
    targetChars.value = normalizeTargetChars(num);
  }
};

const analysis = computed(() => {
  return analyzeReport(text.value, targetChars.value, ruleMode.value, excludeSpaces.value);
});

const statusBadgeColor = computed(() => {
  switch (analysis.value.evaluation.status) {
    case 'ok':
      return 'positive';
    case 'short':
      return 'warning';
    case 'over':
      return 'negative';
    default:
      return 'grey-6';
  }
});

const statusTextClass = computed(() => {
  switch (analysis.value.evaluation.status) {
    case 'ok':
      return 'text-positive';
    case 'short':
      return 'text-orange-9';
    case 'over':
      return 'text-negative';
    default:
      return 'text-grey-7';
  }
});

const statusCardClass = computed(() => {
  switch (analysis.value.evaluation.status) {
    case 'ok':
      return 'status-ok';
    case 'short':
      return 'status-short';
    case 'over':
      return 'status-over';
    default:
      return '';
  }
});

const statusIcon = computed(() => {
  switch (analysis.value.evaluation.status) {
    case 'ok':
      return 'check_circle';
    case 'short':
      return 'hourglass_bottom';
    case 'over':
      return 'error';
    default:
      return 'edit';
  }
});

const statusLabel = computed(() => {
  switch (analysis.value.evaluation.status) {
    case 'ok':
      return t('report.status.ok');
    case 'short':
      return t('report.status.short');
    case 'over':
      return t('report.status.over');
    default:
      return t('report.status.empty');
  }
});

const statusMessage = computed(() => {
  const ev = analysis.value.evaluation;
  if (ev.status === 'empty') {
    return t('report.status.emptyMessage');
  }
  if (ev.status === 'short') {
    return t('report.status.shortMessage', {
      diff: ev.diffToMin.toLocaleString()
    });
  }
  if (ev.status === 'over') {
    return t('report.status.overMessage', {
      diff: ev.diffToMax.toLocaleString()
    });
  }
  return t('report.status.okMessage');
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
      message: t('report.input.copied'),
      timeout: 2000
    });
  } catch (err) {
    console.error('Clipboard copy failed:', err);
  }
};

const insertSampleText = () => {
  targetChars.value = 800;
  targetCharsInput.value = 800;
  text.value =
    '現代社会において、生成AIをはじめとするデジタル技術の急速な普及は、私たちの学び方や働き方に大きな変革をもたらしている。特に大学教育の現場では、レポート作成や情報収集におけるAIの活用が議論の対象となっており、単なる知識の暗記や要約にとどまらない「批判的思考力」の重要性がこれまで以上に高まっている。\n' +
    '第一に、情報源の信頼性を自ら検証する姿勢が不可欠である。インターネット上には膨大な情報があふれているが、そのすべてが正確な根拠に基づいているとは限らない。一次資料や査読付き論文にあたり、複数の視点を比較検討するプロセスこそが、学術的なレポートの説得力を支える基盤となる。\n' +
    '第二に、自身の主張を論理的に構造化する力が求められる。どれほど有益なデータを集めても、結論と根拠の結びつきが曖昧であれば読み手に意図は伝わらない。序論で問いを明確にし、本論で具体的な論拠を示し、結論で全体の意義をまとめる構成を意識することで、限られた文字数の中でも密度の高い議論を展開できる。\n' +
    '以上の点から、今後のレポート作成においては、ツールを補助的に活用しつつも、問いを立てて検証し、自分の言葉で論理を組み立てる主体的な姿勢が重要であると言える。';
};

const rule1Lines = computed(() => (t('report.guide.rule1Body') as string).split('\n'));
const rule2Lines = computed(() => (t('report.guide.rule2Body') as string).split('\n'));

const criteriaRows = computed(() => [
  {
    item: t('report.guide.criteriaRow1Item'),
    include: t('report.guide.criteriaExclude'),
    badgeColor: 'grey-7',
    note: t('report.guide.criteriaRow1Note')
  },
  {
    item: t('report.guide.criteriaRow2Item'),
    include: t('report.guide.criteriaInclude'),
    badgeColor: 'primary',
    note: t('report.guide.criteriaRow2Note')
  },
  {
    item: t('report.guide.criteriaRow3Item'),
    include: t('report.guide.criteriaConditional'),
    badgeColor: 'orange-8',
    note: t('report.guide.criteriaRow3Note')
  },
  {
    item: t('report.guide.criteriaRow4Item'),
    include: t('report.guide.criteriaConditional'),
    badgeColor: 'orange-8',
    note: t('report.guide.criteriaRow4Note')
  },
  {
    item: t('report.guide.criteriaRow5Item'),
    include: t('report.guide.criteriaConditional'),
    badgeColor: 'orange-8',
    note: t('report.guide.criteriaRow5Note')
  }
]);

const guideTableRows = computed(() => [
  {
    chars: t('report.guide.tableRow1Chars'),
    volume: t('report.guide.tableRow1Volume'),
    purpose: t('report.guide.tableRow1Purpose')
  },
  {
    chars: t('report.guide.tableRow2Chars'),
    volume: t('report.guide.tableRow2Volume'),
    purpose: t('report.guide.tableRow2Purpose')
  },
  {
    chars: t('report.guide.tableRow3Chars'),
    volume: t('report.guide.tableRow3Volume'),
    purpose: t('report.guide.tableRow3Purpose')
  },
  {
    chars: t('report.guide.tableRow4Chars'),
    volume: t('report.guide.tableRow4Volume'),
    purpose: t('report.guide.tableRow4Purpose')
  }
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

.target-card,
.text-editor-card,
.status-card {
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.status-card {
  border: 2px solid #e0e0e0;
  transition: border-color 0.25s ease, background-color 0.25s ease;
}

.status-ok {
  border-color: #21ba45;
  background-color: #f4fbf6;
}

.status-short {
  border-color: #f2c037;
  background-color: #fffdf5;
}

.status-over {
  border-color: #c10015;
  background-color: #fff5f6;
}

.status-badge {
  border-radius: 8px;
}

.rule-toggle {
  border: 1px solid #d0d7de;
  border-radius: 8px;
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
