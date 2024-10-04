<template>
  <div class="row justify-center">
    <div class="q-pa-md full-width">
      <q-input v-model="text" filled type="textarea" counter rows="20" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineOptions({
  name: 'IndexPage'
});
const text = ref('');
</script>
