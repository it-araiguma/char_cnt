<template>
  <q-layout view="hhh lpR fff">

    <q-header elevated>
      <q-toolbar>
        <q-icon name="edit_note" size="md" />
        <q-toolbar-title>
          文字数カウント
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer elevated class="bg-grey-8 text-white">
      <q-toolbar>
        <q-toolbar-title>
        </q-toolbar-title>
      </q-toolbar>
    </q-footer>

  </q-layout>
</template>

<script setup lang="ts">
defineOptions({
  name: 'MainLayout'
});
</script>
