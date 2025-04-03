<template>
  <div class="container q-pa-md">
    <div class="row justify-center">
      <div class="col-12 col-md-8">
        <q-card class="text-editor-card q-mb-md">
          <q-card-section>
            <h5 class="text-h5 q-mt-sm q-mb-md text-primary text-center">テキストカウンター</h5>
            <q-input 
              v-model="text" 
              filled 
              type="textarea" 
              counter 
              rows="15"
              class="text-area"
              placeholder="ここにテキストを入力してください..."
              bg-color="grey-1"
            />
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md">
            <q-btn 
              color="negative" 
              label="クリア" 
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
                <div class="text-subtitle2 text-grey-7">文字数</div>
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
                <div class="text-subtitle2 text-grey-7">改行・スペースなし</div>
                <div class="row items-center">
                  <q-icon name="edit_note" color="secondary" size="sm" class="q-mr-sm" />
                  <div class="text-h4 text-weight-bold text-secondary">{{ processedTextLength }}</div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

defineOptions({
  name: 'IndexPage'
});
const text = ref('');
const textLength = computed(() => text.value.length);
const processedTextLength = computed(() => {
  return text.value
    .replace(/[\r\n]/g, '')
    .trim()
    .replace(/\s/g, '').length;
});

const clearText = () => {
  text.value = '';
};
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
</style>
