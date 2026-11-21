import { countGraphemes, countGraphemesWithoutSpaces } from './charCount';

export type ReportRuleMode = 'around10' | 'min80' | 'max100';
export type ReportStatus = 'empty' | 'short' | 'ok' | 'over';

export interface ReportRuleEvaluation {
  mode: ReportRuleMode;
  status: ReportStatus;
  minChars: number;
  maxChars: number;
  diffToMin: number;
  diffToMax: number;
  diffToTarget: number;
}

export interface ReportAnalysisResult {
  totalChars: number;
  charsWithoutSpaces: number;
  lineCount: number;
  paragraphCount: number;
  genko400Sheets: number;
  targetChars: number;
  activeCount: number;
  progressRatio: number;
  progressPercent: number;
  evaluation: ReportRuleEvaluation;
}

export const REPORT_PRESETS = [800, 1200, 2000, 4000] as const;

/**
 * 目標文字数を安全な正の整数に正規化する。
 */
export function normalizeTargetChars(targetChars: number): number {
  if (!Number.isFinite(targetChars) || targetChars < 1) {
    return 1;
  }
  return Math.min(Math.floor(targetChars), 1000000);
}

/**
 * 指定された達成判定モードに応じて、最小・最大許容文字数と達成ステータスを算出する。
 */
export function evaluateReportRule(
  count: number,
  targetChars: number,
  mode: ReportRuleMode
): ReportRuleEvaluation {
  const safeTarget = normalizeTargetChars(targetChars);
  const safeCount = Math.max(0, Math.floor(count));

  let minChars = 1;
  let maxChars = safeTarget;

  if (mode === 'around10') {
    minChars = Math.max(1, Math.ceil(safeTarget * 0.9));
    maxChars = Math.max(minChars, Math.floor(safeTarget * 1.1));
  } else if (mode === 'min80') {
    minChars = Math.max(1, Math.ceil(safeTarget * 0.8));
    maxChars = safeTarget;
  } else {
    minChars = 1;
    maxChars = safeTarget;
  }

  let status: ReportStatus = 'empty';
  if (safeCount > 0) {
    if (safeCount < minChars) {
      status = 'short';
    } else if (safeCount > maxChars) {
      status = 'over';
    } else {
      status = 'ok';
    }
  }

  return {
    mode,
    status,
    minChars,
    maxChars,
    diffToMin: safeCount < minChars ? minChars - safeCount : 0,
    diffToMax: safeCount > maxChars ? safeCount - maxChars : 0,
    diffToTarget: safeCount - safeTarget
  };
}

/**
 * テキスト全体のレポート・小論文向け文字数解析と達成判定を行う。
 */
export function analyzeReport(
  text: string,
  targetChars: number,
  mode: ReportRuleMode = 'around10',
  excludeSpaces = false
): ReportAnalysisResult {
  const totalChars = countGraphemes(text);
  const charsWithoutSpaces = countGraphemesWithoutSpaces(text);

  let lineCount = 0;
  let paragraphCount = 0;
  if (text) {
    const lines = text.split(/\r?\n/);
    lineCount =
      lines.length > 1 && lines[lines.length - 1] === ''
        ? lines.length - 1
        : lines.length;
    paragraphCount = lines.filter((line) => line.trim().length > 0).length;
  }

  const safeTarget = normalizeTargetChars(targetChars);
  const activeCount = excludeSpaces ? charsWithoutSpaces : totalChars;
  const rawRatio = activeCount / safeTarget;
  const progressRatio = Math.max(0, Math.min(rawRatio, 1));
  const progressPercent = Number((rawRatio * 100).toFixed(1));
  const genko400Sheets = Number((totalChars / 400).toFixed(1));

  const evaluation = evaluateReportRule(activeCount, safeTarget, mode);

  return {
    totalChars,
    charsWithoutSpaces,
    lineCount,
    paragraphCount,
    genko400Sheets,
    targetChars: safeTarget,
    activeCount,
    progressRatio,
    progressPercent,
    evaluation
  };
}
