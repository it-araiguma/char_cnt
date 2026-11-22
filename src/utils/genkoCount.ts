import {
  countGraphemes,
  countGraphemesWithoutLinebreaks,
  countGraphemesWithoutSpaces,
  splitGraphemes
} from './charCount';

export const GENKO_MIN_GRID = 1;
export const GENKO_MAX_GRID = 100;
export const GENKO_DEFAULT_CHARS_PER_LINE = 20;
export const GENKO_DEFAULT_LINES_PER_PAGE = 20;

// 行頭禁則文字（行末を超えた場合、前の行の最終マスにぶら下げる）
const HANGING_PUNCTUATION_REGEX = /^[。、．，」』）］｝】〉》〕”’.,)\]}]+$/u;
// 半角英数字（1マスに2文字入れる対象）
const HALF_WIDTH_ALNUM_REGEX = /^[0-9A-Za-z]$/;

export interface GenkoSetting {
  charsPerLine: number; // 1行あたりの文字数（通常20）
  linesPerPage: number; // 1枚あたりの行数（400字なら20、200字なら10）
}

export interface GenkoCountOptions {
  /** 半角英数字を1マスに2文字入れるか（既定: true） */
  halfWidthAsTwoPerCell?: boolean;
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
  charsWithoutLinebreaks: number;
  totalLines: number; // 実用紙上の総行数
  rawLineCount: number; // 改行で区切られた段落・行数

  // プリセット換算結果
  genko400: GenkoMetric;
  genko200: GenkoMetric;

  // カスタム設定換算結果
  custom: GenkoMetric;
}

/**
 * 1段落分のテキストが原稿用紙上で消費する行数を計算する。
 * - 行頭禁則文字（。、」』）など）が行末を超えた場合は前の行の最終マスにぶら下げる。
 * - halfWidthAsTwoPerCell が true の場合、連続する半角英数字を1マスに2文字入れる。
 */
function calculateParagraphLines(
  paragraph: string,
  charsPerLine: number,
  halfWidthAsTwoPerCell: boolean
): number {
  const graphemes = splitGraphemes(paragraph);
  if (graphemes.length === 0) {
    return 1; // 空行も原稿用紙では1行消費
  }

  let lineCount = 1;
  let col = 0;

  for (const grapheme of graphemes) {
    if (HANGING_PUNCTUATION_REGEX.test(grapheme)) {
      if (Math.ceil(col) < charsPerLine) {
        col = Math.ceil(col) + 1;
      } else if (col > 0) {
        // 前の文字が行末マスにあるため、同じ行の最終マスにぶら下げる
        col = charsPerLine;
      } else {
        col = 1;
      }
      continue;
    }

    if (halfWidthAsTwoPerCell && HALF_WIDTH_ALNUM_REGEX.test(grapheme)) {
      if (col + 0.5 > charsPerLine) {
        lineCount += 1;
        col = 0.5;
      } else {
        col += 0.5;
      }
      continue;
    }

    // 半角英数字1文字の端数（0.5）が残っている場合は次のマスへ進めてから全角1マスを配置する
    const alignedCol = Math.ceil(col);
    if (alignedCol + 1 > charsPerLine) {
      lineCount += 1;
      col = 1;
    } else {
      col = alignedCol + 1;
    }
  }

  return lineCount;
}

/**
 * テキストから原稿用紙上の総行数を算出する。
 * 改行で分割し、各段落の行数（行頭禁則のぶら下げ・半角英数字2文字詰めを考慮）を合算。
 * 空行は1行としてカウント。末尾の単一改行による空文字は無視。
 */
export function calculateGenkoLines(
  text: string,
  charsPerLine = GENKO_DEFAULT_CHARS_PER_LINE,
  options: GenkoCountOptions = {}
): { totalLines: number; rawLineCount: number } {
  if (!text) {
    return { totalLines: 0, rawLineCount: 0 };
  }

  const safeCharsPerLine = sanitizeGenkoGridValue(charsPerLine, GENKO_DEFAULT_CHARS_PER_LINE);
  const halfWidthAsTwoPerCell = options.halfWidthAsTwoPerCell ?? true;

  let lines = text.split(/\r?\n/);

  // 末尾が改行で終わっている場合、直後の空文字は「次行開始前」として除外
  if (lines.length > 1 && lines[lines.length - 1] === '') {
    lines = lines.slice(0, -1);
  }

  let totalLines = 0;
  for (const line of lines) {
    totalLines += calculateParagraphLines(line, safeCharsPerLine, halfWidthAsTwoPerCell);
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
  },
  options: GenkoCountOptions = {}
): GenkoAnalysisResult {
  const safeCustomSetting = sanitizeGenkoSetting(customSetting);
  const totalChars = countGraphemes(text);
  const charsWithoutSpaces = countGraphemesWithoutSpaces(text);
  const charsWithoutLinebreaks = countGraphemesWithoutLinebreaks(text);

  // 400字詰め（20字×20行）
  const lines20 = calculateGenkoLines(text, 20, options);
  const genko400 = calculateGenkoMetric(charsWithoutLinebreaks, lines20.totalLines, {
    charsPerLine: 20,
    linesPerPage: 20
  });

  // 200字詰め（20字×10行）
  const genko200 = calculateGenkoMetric(charsWithoutLinebreaks, lines20.totalLines, {
    charsPerLine: 20,
    linesPerPage: 10
  });

  // カスタム設定
  const customLines =
    safeCustomSetting.charsPerLine === 20
      ? lines20
      : calculateGenkoLines(text, safeCustomSetting.charsPerLine, options);
  const custom = calculateGenkoMetric(
    charsWithoutLinebreaks,
    customLines.totalLines,
    safeCustomSetting
  );

  return {
    totalChars,
    charsWithoutSpaces,
    charsWithoutLinebreaks,
    totalLines: lines20.totalLines,
    rawLineCount: lines20.rawLineCount,
    genko400,
    genko200,
    custom
  };
}
