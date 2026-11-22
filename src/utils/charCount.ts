const graphemeSegmenter =
  typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function'
    ? new Intl.Segmenter(undefined, { granularity: 'grapheme' })
    : null;

const utf8Encoder = typeof TextEncoder !== 'undefined' ? new TextEncoder() : null;

export interface TextMetrics {
  totalChars: number;
  charsWithoutLineBreaks: number;
  charsWithoutSpaces: number;
  lineCountWithEmpty: number;
  lineCountWithoutEmpty: number;
  paragraphCount: number;
  utf8Bytes: number;
  shiftJisBytes: number;
  fullWidthChars: number;
  halfWidthChars: number;
}

/**
 * テキストを書記素クラスタ（見た目の1文字）の配列へ分割する。
 */
function segmentGraphemes(text: string): string[] {
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
  return segmentGraphemes(text).length;
}

/**
 * 改行文字（CRLF / CR / LF）のみを除いた書記素単位の文字数をカウントする。
 * 半角スペース・全角スペース・タブはカウントに含める。
 */
export function countGraphemesWithoutLineBreaks(text: string): number {
  if (!text) {
    return 0;
  }

  return countGraphemes(text.replace(/\r\n|\r|\n/g, ''));
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

/**
 * 単一コードポイントが半角文字（ASCII または半角カタカナ等）かどうかを判定する。
 */
function isHalfWidthCodePoint(cp: number): boolean {
  return (
    (cp >= 0x0000 && cp <= 0x007f) ||
    (cp >= 0xff61 && cp <= 0xff9f) ||
    cp === 0x00a5 || // ¥
    cp === 0x203e // ‾
  );
}

/**
 * 書記素クラスタが半角文字かどうかを判定する。
 * 単一コードポイントで構成され、かつ ASCII / 半角カタカナ範囲に収まる場合のみ半角とみなす。
 */
function isHalfWidthGrapheme(grapheme: string): boolean {
  const codePoints = [...grapheme];
  if (codePoints.length !== 1) {
    return false;
  }
  const cp = codePoints[0].codePointAt(0);
  return cp !== undefined && isHalfWidthCodePoint(cp);
}

/**
 * テキストを改行コード（CRLF / CR / LF）で分割する。
 * 末尾の単一改行による空文字は「次行開始前」として除外する。
 */
function splitLinesNormalized(text: string): string[] {
  if (!text) {
    return [];
  }

  const lines = text.split(/\r\n|\r|\n/);
  if (lines.length > 1 && lines[lines.length - 1] === '') {
    return lines.slice(0, -1);
  }
  return lines;
}

/**
 * UTF-8 バイト数を算出する。
 */
export function countUtf8Bytes(text: string): number {
  if (!text) {
    return 0;
  }

  if (utf8Encoder) {
    return utf8Encoder.encode(text).length;
  }

  // フォールバック: URI エンコード長から算出
  return encodeURIComponent(text).replace(/%[0-9A-F]{2}/gi, 'x').length;
}

/**
 * Shift_JIS 概算バイト数を算出する。
 * ASCII・半角カタカナを 1 バイト、それ以外の文字を 2 バイトとして計算する。
 */
export function countShiftJisBytes(text: string): number {
  if (!text) {
    return 0;
  }

  let bytes = 0;
  for (const ch of text) {
    const cp = ch.codePointAt(0);
    if (cp !== undefined && isHalfWidthCodePoint(cp)) {
      bytes += 1;
    } else {
      bytes += 2;
    }
  }
  return bytes;
}

/**
 * テキストの各種カウント指標を一括で算出する。
 */
export function analyzeText(text: string): TextMetrics {
  if (!text) {
    return {
      totalChars: 0,
      charsWithoutLineBreaks: 0,
      charsWithoutSpaces: 0,
      lineCountWithEmpty: 0,
      lineCountWithoutEmpty: 0,
      paragraphCount: 0,
      utf8Bytes: 0,
      shiftJisBytes: 0,
      fullWidthChars: 0,
      halfWidthChars: 0
    };
  }

  const totalChars = countGraphemes(text);
  const withoutLineBreaksText = text.replace(/\r\n|\r|\n/g, '');
  const withoutLineBreaksGraphemes = segmentGraphemes(withoutLineBreaksText);
  const charsWithoutLineBreaks = withoutLineBreaksGraphemes.length;
  const charsWithoutSpaces = countGraphemesWithoutSpaces(text);

  let fullWidthChars = 0;
  let halfWidthChars = 0;
  for (const grapheme of withoutLineBreaksGraphemes) {
    if (isHalfWidthGrapheme(grapheme)) {
      halfWidthChars++;
    } else {
      fullWidthChars++;
    }
  }

  const lines = splitLinesNormalized(text);
  const lineCountWithEmpty = lines.length;
  let lineCountWithoutEmpty = 0;
  let paragraphCount = 0;
  let inParagraph = false;

  for (const line of lines) {
    if (line.trim().length > 0) {
      lineCountWithoutEmpty++;
      if (!inParagraph) {
        paragraphCount++;
        inParagraph = true;
      }
    } else {
      inParagraph = false;
    }
  }

  return {
    totalChars,
    charsWithoutLineBreaks,
    charsWithoutSpaces,
    lineCountWithEmpty,
    lineCountWithoutEmpty,
    paragraphCount,
    utf8Bytes: countUtf8Bytes(text),
    shiftJisBytes: countShiftJisBytes(text),
    fullWidthChars,
    halfWidthChars
  };
}
