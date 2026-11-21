const CHUNK_RELOAD_KEY = 'char_cnt_chunk_reload_at';
const CHUNK_RELOAD_COOLDOWN_MS = 10_000;

let swUpdated = false;

/**
 * Service Worker が更新されたことを記録する。
 */
export function markSwUpdated(): void {
  swUpdated = true;
}

/**
 * Service Worker が更新済みかどうかを返す。
 */
export function isSwUpdated(): boolean {
  return swUpdated;
}

/**
 * 動的 import / チャンク読み込み失敗のエラーかどうかを判定する。
 */
export function isChunkLoadError(error: unknown): boolean {
  if (!(error instanceof Error)) {
    return false;
  }
  const message = error.message;
  return (
    error.name === 'ChunkLoadError' ||
    /Failed to fetch dynamically imported module/i.test(message) ||
    /error loading dynamically imported module/i.test(message) ||
    /Importing a module script failed/i.test(message) ||
    /Unable to preload CSS/i.test(message) ||
    /Loading chunk [\w-]+ failed/i.test(message)
  );
}

/**
 * クールダウン付きでページを再読み込みし、無限リロードループを防ぐ。
 * リロードを実行した場合は true、クールダウン中や実行不可の場合は false を返す。
 */
export function reloadWithCooldown(targetUrl?: string): boolean {
  if (typeof window === 'undefined') {
    return false;
  }
  try {
    const lastReloadAt = Number(window.sessionStorage.getItem(CHUNK_RELOAD_KEY) || '0');
    const now = Date.now();
    if (Number.isFinite(lastReloadAt) && now - lastReloadAt < CHUNK_RELOAD_COOLDOWN_MS) {
      return false;
    }
    window.sessionStorage.setItem(CHUNK_RELOAD_KEY, String(now));
  } catch {
    return false;
  }

  if (targetUrl) {
    window.location.assign(targetUrl);
  } else {
    window.location.reload();
  }
  return true;
}
