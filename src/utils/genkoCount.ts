import { countGraphemes, countGraphemesWithoutSpaces } from './charCount';

export const GENKO_MIN_GRID = 1;
export const GENKO_MAX_GRID = 100;
export const GENKO_DEFAULT_CHARS_PER_LINE = 20;
export const GENKO_DEFAULT_LINES_PER_PAGE = 20;

export interface GenkoSetting {
  charsPerLine: number; // 1行あたりの文字数（通常20）
  linesPerPage: number; // 1枚あたりの行数（400字なら20、200字なら10）
}

/**
 * 原稿用紙のマス目設定値（1〜100の整数）として有効か判定する
 */
export function isValidGenkoGridValue(value: unknown): value is number {
  return (
    typeof value === 'number' &&
    Number.isInteger(value) &&
    value >= GENKO_MIN_GRID &&
    value <= GENKO_MAX_GRID
  );
}

/**
 * 不正なマス目設定値を既定値へフォールバックする
 */
export function sanitizeGenkoGridValue(
  value: unknown,
  fallback = GENKO_DEFAULT_CHARS_PER_LINE
): number {
  if (isValidGenkoGridValue(value)) {
    return value;
  }
  return isValidGenkoGridValue(fallback) ? fallback : GENKO_DEFAULT_CHARS_PER_LINE;
}

/**
 * 原稿用紙設定を安全な値（1〜100の整数）へ正規化する
 */
export function sanitizeGenkoSetting(setting?: Partial<GenkoSetting> | null): GenkoSetting {
  return {
    charsPerLine: sanitizeGenkoGridValue(setting?.charsPerLine, GENKO_DEFAULT_CHARS_PER_LINE),
    linesPerPage: sanitizeGenkoGridValue(setting?.linesPerPage, GENKO_DEFAULT_LINES_PER_PAGE)
  };
}

export interface GenkoMetric {
  // 実用紙（行数・改行考慮）換算
  actualSheets: number; // 必要枚数（切り上げ）
  actualFullSheets: number; // 端数内訳：満杯枚数
  actualRemainingLines: number; // 端数内訳：余り行数
  isExactSheet: boolean; // 端数なし（ピッタリ枚数）かどうか

  // 文字数ベース（文字数 ÷ 1枚マス目）換算
  rawSheets: number; // 小数点表記（例: 1.25）
  charFullSheets: number; // 端数内訳：枚数
  charRemainingChars: number; // 端数内訳：余り文字数

  // 基準値
  charsPerPage: number;
}

export interface GenkoAnalysisResult {
  // 基本テキスト情報
  totalChars: number;
  charsWithoutSpaces: number;
  totalLines: number; // 実用紙上の総行数
  rawLineCount: number; // 改行で区切られた段落・行数

  // プリセット換算結果
  genko400: GenkoMetric;
  genko200: GenkoMetric;

  // カスタム設定換算結果
  custom: GenkoMetric;
}

/**
 * テキストから原稿用紙上の総行数を算出する。
 * 改行で分割し、各段落の文字数に応じた行数（ceil(文字数 / charsPerLine)）を合算。
 * 空行は1行としてカウント。末尾の単一改行による空文字は無視。
 */
export function calculateGenkoLines(
  text: string,
  charsPerLine = GENKO_DEFAULT_CHARS_PER_LINE
): { totalLines: number; rawLineCount: number } {
  if (!text) {
    return { totalLines: 0, rawLineCount: 0 };
  }

  const safeCharsPerLine = sanitizeGenkoGridValue(charsPerLine, GENKO_DEFAULT_CHARS_PER_LINE);

  let lines = text.split(/\r?\n/);

  // 末尾が改行で終わっている場合、直後の空文字は「次行開始前」として除外
  if (lines.length > 1 && lines[lines.length - 1] === '') {
    lines = lines.slice(0, -1);
  }

  let totalLines = 0;
  for (const line of lines) {
    const chars = countGraphemes(line);
    if (chars === 0) {
      totalLines += 1; // 空行も原稿用紙では1行消費
    } else {
      totalLines += Math.ceil(chars / safeCharsPerLine);
    }
  }

  return {
    totalLines,
    rawLineCount: lines.length
  };
}

/**
 * 指定された設定（1行文字数、1枚行数）で原稿用紙換算を行う
 */
export function calculateGenkoMetric(
  totalChars: number,
  totalLines: number,
  setting: GenkoSetting
): GenkoMetric {
  const safeSetting = sanitizeGenkoSetting(setting);
  const charsPerPage = safeSetting.charsPerLine * safeSetting.linesPerPage;
  const safeTotalChars = Number.isFinite(totalChars) ? Math.max(0, totalChars) : 0;
  const safeTotalLines = Number.isFinite(totalLines) ? Math.max(0, totalLines) : 0;

  if (safeTotalChars === 0 || safeTotalLines === 0) {
    return {
      actualSheets: 0,
      actualFullSheets: 0,
      actualRemainingLines: 0,
      isExactSheet: true,
      rawSheets: 0,
      charFullSheets: 0,
      charRemainingChars: 0,
      charsPerPage
    };
  }

  // 実用紙（行数・改行考慮）
  const actualSheets = Math.ceil(safeTotalLines / safeSetting.linesPerPage);
  const actualFullSheets = Math.floor(safeTotalLines / safeSetting.linesPerPage);
  const actualRemainingLines = safeTotalLines % safeSetting.linesPerPage;
  const isExactSheet = actualRemainingLines === 0;

  // 文字数ベース（文字数 ÷ 1枚マス目）
  const rawSheets = Number((safeTotalChars / charsPerPage).toFixed(2));
  const charFullSheets = Math.floor(safeTotalChars / charsPerPage);
  const charRemainingChars = safeTotalChars % charsPerPage;

  return {
    actualSheets,
    actualFullSheets,
    actualRemainingLines,
    isExactSheet,
    rawSheets,
    charFullSheets,
    charRemainingChars,
    charsPerPage
  };
}

/**
 * テキスト全体の原稿用紙総合換算を実行する
 */
export function analyzeGenko(
  text: string,
  customSetting: GenkoSetting = {
    charsPerLine: GENKO_DEFAULT_CHARS_PER_LINE,
    linesPerPage: GENKO_DEFAULT_LINES_PER_PAGE
  }
): GenkoAnalysisResult {
  const safeCustomSetting = sanitizeGenkoSetting(customSetting);
  const totalChars = countGraphemes(text);
  const charsWithoutSpaces = countGraphemesWithoutSpaces(text);

  // 400字詰め（20字×20行）
  const lines20 = calculateGenkoLines(text, 20);
  const genko400 = calculateGenkoMetric(totalChars, lines20.totalLines, {
    charsPerLine: 20,
    linesPerPage: 20
  });

  // 200字詰め（20字×10行）
  const genko200 = calculateGenkoMetric(totalChars, lines20.totalLines, {
    charsPerLine: 20,
    linesPerPage: 10
  });

  // カスタム設定
  const customLines =
    safeCustomSetting.charsPerLine === 20
      ? lines20
      : calculateGenkoLines(text, safeCustomSetting.charsPerLine);
  const custom = calculateGenkoMetric(
    totalChars,
    customLines.totalLines,
    safeCustomSetting
  );

  return {
    totalChars,
    charsWithoutSpaces,
    totalLines: lines20.totalLines,
    rawLineCount: lines20.rawLineCount,
    genko400,
    genko200,
    custom
  };
}
