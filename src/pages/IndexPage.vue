<template>
  <div class="row justify-center">
    <div class="q-pa-md full-width">
      <q-input v-model="text" filled type="textarea" counter rows="20" />
    </div>
    <div class="row q-px-md">
      <div class="col-12 col-md-12" :class="{ 'q-pb-sm': $q.screen.lt.sm, 'q-pr-sm': $q.screen.gt.md }">
        <q-input outlined bottom-slots v-model="textLength" label="本文" maxlength="12">
          <template v-slot:before>
            <q-icon name="edit" />
          </template>
        </q-input>
        <q-input outlined bottom-slots v-model="processedTextLength" label="改行とスペースなし" maxlength="12">
          <template v-slot:before>
            <q-icon name="edit_note" />
          </template>
        </q-input>
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
</script>
