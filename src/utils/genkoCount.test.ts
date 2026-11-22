import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { countGraphemes, countGraphemesWithoutLinebreaks } from './charCount';
import { analyzeGenko, calculateGenkoLines } from './genkoCount';

describe('genkoCount', () => {
  it('行頭禁則（句読点や閉じ括弧のぶら下げ）を考慮して行数を算出する', () => {
    // 20字 + 「。」（計21字）はぶら下げにより1行に収まる
    const text20PlusPeriod = 'あ'.repeat(20) + '。';
    assert.equal(calculateGenkoLines(text20PlusPeriod, 20).totalLines, 1);

    // 20字 + 「。」 + 「」」（連続した禁則文字）も1行に収まる
    const text20PlusPeriodAndBracket = 'あ'.repeat(20) + '。」';
    assert.equal(calculateGenkoLines(text20PlusPeriodAndBracket, 20).totalLines, 1);

    // 20字 + 「。」 + 「あ」（禁則の後に通常文字）は2行になる
    const text20PlusPeriodAndChar = 'あ'.repeat(20) + '。あ';
    assert.equal(calculateGenkoLines(text20PlusPeriodAndChar, 20).totalLines, 2);

    // 19字 + 「。」は20マス目に普通に収まり、次の「あ」で2行になる
    const text19PlusPeriodAndChar = 'あ'.repeat(19) + '。あ';
    assert.equal(calculateGenkoLines(text19PlusPeriodAndChar, 20).totalLines, 2);

    // 行頭の句読点のみの段落は1行になる
    assert.equal(calculateGenkoLines('。', 20).totalLines, 1);
  });

  it('半角英数字を1マスに2文字入れるオプションを切り替えられる', () => {
    const alnum36 = 'a'.repeat(36);
    // 既定（true）: 36文字 = 18マス = 1行
    assert.equal(calculateGenkoLines(alnum36, 20).totalLines, 1);
    // 明示的 false: 1マス1文字 = 36マス = 2行
    assert.equal(
      calculateGenkoLines(alnum36, 20, { halfWidthAsTwoPerCell: false }).totalLines,
      2
    );

    // 半角40文字はちょうど1行（20マス）、41文字で2行
    assert.equal(calculateGenkoLines('1'.repeat(40), 20).totalLines, 1);
    assert.equal(calculateGenkoLines('1'.repeat(41), 20).totalLines, 2);

    // 全角19文字 + 半角1文字 + 全角1文字 -> 半角1文字が20マス目を使い、次の全角は2行目
    assert.equal(calculateGenkoLines('あ'.repeat(19) + '1あ', 20).totalLines, 2);

    // 全角19文字 + 半角1文字 + 「。」 -> ぶら下げにより1行
    assert.equal(calculateGenkoLines('あ'.repeat(19) + '1。', 20).totalLines, 1);
  });

  it('文字数ベース換算の分子から改行を除き、字下げの全角スペースは残す', () => {
    const text = 'あ\nい';
    assert.equal(countGraphemes(text), 3);
    assert.equal(countGraphemesWithoutLinebreaks(text), 2);

    const result = analyzeGenko(text);
    assert.equal(result.totalChars, 3);
    assert.equal(result.charsWithoutLinebreaks, 2);
    assert.equal(result.genko400.charFullSheets, 0);
    assert.equal(result.genko400.charRemainingChars, 2);
    assert.equal(result.genko400.rawSheets, 0.01);

    // 字下げの全角スペースは1マスとして数え続ける（'　あ\n　い' -> 4文字）
    const indentedText = '　あ\n　い';
    const indentedResult = analyzeGenko(indentedText);
    assert.equal(indentedResult.charsWithoutLinebreaks, 4);
    assert.equal(indentedResult.genko400.charRemainingChars, 4);

    // 400文字 + 改行10個 -> 文字数ベース換算は400字ちょうど（1枚・余り0字）
    const exact400WithNewlines = Array.from({ length: 10 }, () => 'あ'.repeat(40)).join('\n');
    const exactResult = analyzeGenko(exact400WithNewlines);
    assert.equal(exactResult.charsWithoutLinebreaks, 400);
    assert.equal(exactResult.genko400.rawSheets, 1);
    assert.equal(exactResult.genko400.charFullSheets, 1);
    assert.equal(exactResult.genko400.charRemainingChars, 0);
  });
});
