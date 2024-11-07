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
      <ins class="adsbygoogle"
           style="display:block"
           data-ad-client="ca-pub-9551028273212184"
           data-ad-slot="6603589954"
           data-ad-format="auto"
           data-full-width-responsive="true"></ins>
    </q-page-container>

    <q-footer elevated class="bg-grey-8 text-white q-pt-xs q-pb-xs">
      <q-toolbar>
        <q-toolbar-title>
          <div class="copyright text-center q-mb-xs">
            <RouterLink to="/" class="q-mx-xs">ホーム</RouterLink>
            <RouterLink to="/privacy" class="q-mx-xs">プライバシーポリシー</RouterLink>
          </div>
          <div class="copyright text-center">
            Copyright © <a href="https://it-araiguma.com" target="_blank">ITアライグマ</a> AllRights Reserved.
          </div>
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
<style scoped>
.copyright {
  font-size: 14px;
}

.copyright>a {
  color: #fff;
}
</style>
