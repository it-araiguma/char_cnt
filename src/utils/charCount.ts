const graphemeSegmenter =
  typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function'
    ? new Intl.Segmenter(undefined, { granularity: 'grapheme' })
    : null;

/**
 * 書記素クラスタ（見た目の1文字）単位で文字数をカウントする。
 * サロゲートペア（𠮷、😀 等）・ZWJ 結合絵文字（👨‍👩‍👧‍👦 等）・結合文字も1文字として数える。
 * Intl.Segmenter 未対応環境ではコードポイント単位（[...text]）にフォールバックする。
 */
export function countGraphemes(text: string): number {
  if (!text) {
    return 0;
  }

  if (graphemeSegmenter) {
    return Array.from(graphemeSegmenter.segment(text)).length;
  }

  return [...text].length;
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
