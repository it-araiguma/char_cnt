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
                {{ textLength }}
              </template>
            </q-input>
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md">
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

        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-card class="counter-card" :class="{'pulse-animation': textLength > 0}">
              <q-card-section>
                <div class="text-subtitle2 text-grey-7">{{ $t('app.counter.characters') }}</div>
                <div class="row items-center">
                  <q-icon name="edit" color="primary" size="sm" class="q-mr-sm" />
                  <div class="text-h4 text-weight-bold text-primary">{{ textLength }}</div>
                </div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col-12 col-sm-6">
            <q-card class="counter-card" :class="{'pulse-animation': processedTextLength > 0}">
              <q-card-section>
                <div class="text-subtitle2 text-grey-7">{{ $t('app.counter.noSpaces') }}</div>
                <div class="row items-center">
                  <q-icon name="edit_note" color="secondary" size="sm" class="q-mr-sm" />
                  <div class="text-h4 text-weight-bold text-secondary">{{ processedTextLength }}</div>
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
          </q-card-section>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useSeoMeta } from 'src/utils/seo';
import { countGraphemes, countGraphemesWithoutSpaces } from 'src/utils/charCount';
import { syncLocaleWithRoute } from 'src/i18n';
import { useRouter, useRoute } from 'vue-router';

defineOptions({
  name: 'IndexPage'
});

// SEOメタタグを設定
useSeoMeta('index');

const { locale } = useI18n();
const router = useRouter();
const route = useRoute();

const text = ref('');
const textLength = computed(() => countGraphemes(text.value));
const processedTextLength = computed(() => countGraphemesWithoutSpaces(text.value));

const clearText = () => {
  text.value = '';
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
}

.counter-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.12);
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
