import { describe, expect, it } from 'vitest';
import { countGraphemes, countGraphemesWithoutLinebreaks } from './charCount';
import {
  analyzeGenko,
  calculateGenkoLines,
  calculateGenkoMetric,
  sanitizeGenkoSetting
} from './genkoCount';

describe('genkoCount', () => {
  describe('calculateGenkoLines', () => {
    it('空文字・空行・末尾改行を正しく扱う', () => {
      expect(calculateGenkoLines('')).toEqual({ totalLines: 0, rawLineCount: 0 });
      expect(calculateGenkoLines('\n')).toEqual({ totalLines: 1, rawLineCount: 1 });
      expect(calculateGenkoLines('あ\n\nい')).toEqual({ totalLines: 3, rawLineCount: 3 });
      // 末尾の単一改行は次行開始前として無視する
      expect(calculateGenkoLines('あ\n')).toEqual({ totalLines: 1, rawLineCount: 1 });
      expect(calculateGenkoLines('あ\r\nい\r\n')).toEqual({ totalLines: 2, rawLineCount: 2 });
    });

    it('20字ちょうどと21字（通常文字）の行境界を正しく判定する', () => {
      expect(calculateGenkoLines('あ'.repeat(20), 20).totalLines).toBe(1);
      expect(calculateGenkoLines('あ'.repeat(21), 20).totalLines).toBe(2);
    });

    it('行頭禁則（句読点や閉じ括弧のぶら下げ）を考慮して行数を算出する', () => {
      // 20字 + 「。」（計21字）はぶら下げにより1行に収まる
      expect(calculateGenkoLines('あ'.repeat(20) + '。', 20).totalLines).toBe(1);
      // 20字 + 「。」 + 「」」（連続した禁則文字）も1行に収まる
      expect(calculateGenkoLines('あ'.repeat(20) + '。」', 20).totalLines).toBe(1);
      // 20字 + 「。」 + 「あ」（禁則の後に通常文字）は2行になる
      expect(calculateGenkoLines('あ'.repeat(20) + '。あ', 20).totalLines).toBe(2);
      // 19字 + 「。」は20マス目に普通に収まり、次の「あ」で2行になる
      expect(calculateGenkoLines('あ'.repeat(19) + '。あ', 20).totalLines).toBe(2);
      // 行頭の句読点のみの段落は1行になる
      expect(calculateGenkoLines('。', 20).totalLines).toBe(1);
    });

    it('半角英数字を1マスに2文字入れるオプションを切り替えられる', () => {
      const alnum36 = 'a'.repeat(36);
      // 既定（true）: 36文字 = 18マス = 1行
      expect(calculateGenkoLines(alnum36, 20).totalLines).toBe(1);
      // 明示的 false: 1マス1文字 = 36マス = 2行
      expect(
        calculateGenkoLines(alnum36, 20, { halfWidthAsTwoPerCell: false }).totalLines
      ).toBe(2);

      // 半角40文字はちょうど1行（20マス）、41文字で2行
      expect(calculateGenkoLines('1'.repeat(40), 20).totalLines).toBe(1);
      expect(calculateGenkoLines('1'.repeat(41), 20).totalLines).toBe(2);

      // 全角19文字 + 半角1文字 + 全角1文字 -> 半角1文字が20マス目を使い、次の全角は2行目
      expect(calculateGenkoLines('あ'.repeat(19) + '1あ', 20).totalLines).toBe(2);
      // 全角19文字 + 半角1文字 + 「。」 -> ぶら下げにより1行
      expect(calculateGenkoLines('あ'.repeat(19) + '1。', 20).totalLines).toBe(1);
    });
  });

  describe('calculateGenkoMetric & analyzeGenko', () => {
    it('400字境界（ちょうど1枚・401字で2枚）を正しく計算する', () => {
      const exact400 = analyzeGenko('あ'.repeat(400));
      expect(exact400.genko400.actualSheets).toBe(1);
      expect(exact400.genko400.isExactSheet).toBe(true);
      expect(exact400.genko400.actualRemainingLines).toBe(0);
      expect(exact400.genko400.rawSheets).toBe(1);

      const over400 = analyzeGenko('あ'.repeat(401));
      expect(over400.genko400.actualSheets).toBe(2);
      expect(over400.genko400.isExactSheet).toBe(false);
      expect(over400.genko400.actualFullSheets).toBe(1);
      expect(over400.genko400.actualRemainingLines).toBe(1);
      expect(over400.genko400.charFullSheets).toBe(1);
      expect(over400.genko400.charRemainingChars).toBe(1);
    });

    it('カスタム設定（例: 10字×10行）と不正値フォールバックを正しく扱う', () => {
      const custom = analyzeGenko('あ'.repeat(105), { charsPerLine: 10, linesPerPage: 10 });
      expect(custom.custom.charsPerPage).toBe(100);
      expect(custom.custom.actualSheets).toBe(2);
      expect(custom.custom.actualFullSheets).toBe(1);
      expect(custom.custom.actualRemainingLines).toBe(1);
      expect(custom.custom.rawSheets).toBe(1.05);

      expect(sanitizeGenkoSetting({ charsPerLine: Infinity, linesPerPage: 0 })).toEqual({
        charsPerLine: 20,
        linesPerPage: 20
      });
      expect(calculateGenkoMetric(NaN, Infinity, { charsPerLine: 20, linesPerPage: 20 })).toEqual({
        actualSheets: 0,
        actualFullSheets: 0,
        actualRemainingLines: 0,
        isExactSheet: true,
        rawSheets: 0,
        charFullSheets: 0,
        charRemainingChars: 0,
        charsPerPage: 400
      });
    });

    it('文字数ベース換算の分子から改行を除き、字下げの全角スペースは残す', () => {
      const text = 'あ\nい';
      expect(countGraphemes(text)).toBe(3);
      expect(countGraphemesWithoutLinebreaks(text)).toBe(2);

      const result = analyzeGenko(text);
      expect(result.totalChars).toBe(3);
      expect(result.charsWithoutLinebreaks).toBe(2);
      expect(result.genko400.charFullSheets).toBe(0);
      expect(result.genko400.charRemainingChars).toBe(2);
      expect(result.genko400.rawSheets).toBe(0.01);

      const indentedResult = analyzeGenko('　あ\n　い');
      expect(indentedResult.charsWithoutLinebreaks).toBe(4);
      expect(indentedResult.genko400.charRemainingChars).toBe(4);

      const exact400WithNewlines = Array.from({ length: 10 }, () => 'あ'.repeat(40)).join('\n');
      const exactResult = analyzeGenko(exact400WithNewlines);
      expect(exactResult.charsWithoutLinebreaks).toBe(400);
      expect(exactResult.genko400.rawSheets).toBe(1);
      expect(exactResult.genko400.charFullSheets).toBe(1);
      expect(exactResult.genko400.charRemainingChars).toBe(0);
    });
  });
});
