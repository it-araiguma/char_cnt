const graphemeSegmenter =
  typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function'
    ? new Intl.Segmenter(undefined, { granularity: 'grapheme' })
    : null;

/**
 * テキストを書記素クラスタ（見た目の1文字）の配列に分割する。
 * サロゲートペア（𠮷、😀 等）・ZWJ 結合絵文字（👨‍👩‍👧‍👦 等）・結合文字も1要素として扱う。
 * Intl.Segmenter 未対応環境ではコードポイント単位（[...text]）にフォールバックする。
 */
export function splitGraphemes(text: string): string[] {
  if (!text) {
    return [];
  }

  if (graphemeSegmenter) {
    return Array.from(graphemeSegmenter.segment(text), (s) => s.segment);
  }

  return [...text];
}

/**
 * 書記素クラスタ（見た目の1文字）単位で文字数をカウントする。
 * サロゲートペア（𠮷、😀 等）・ZWJ 結合絵文字（👨‍👩‍👧‍👦 等）・結合文字も1文字として数える。
 * Intl.Segmenter 未対応環境ではコードポイント単位（[...text]）にフォールバックする。
 */
export function countGraphemes(text: string): number {
  return splitGraphemes(text).length;
}

/**
 * 改行文字（CR・LF）を除いた書記素単位の文字数をカウントする。
 * 全角・半角スペースは1文字として残す。
 */
export function countGraphemesWithoutLinebreaks(text: string): number {
  if (!text) {
    return 0;
  }

  return countGraphemes(text.replace(/[\r\n]+/g, ''));
}

/**
 * 空白・改行（半角スペース・全角スペース・タブ・改行等）を除いた書記素単位の文字数をカウントする。
 */
export function countGraphemesWithoutSpaces(text: string): number {
  if (!text) {
    return 0;
  }

  return countGraphemes(text.replace(/\s+/g, ''));
}
