import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  analyzeText,
  countGraphemes,
  countGraphemesWithoutLineBreaks,
  countGraphemesWithoutSpaces,
  countShiftJisBytes,
  countUtf8Bytes
} from '../src/utils/charCount.ts';

describe('charCount', () => {
  it('空文字の場合はすべての指標が 0 になる', () => {
    assert.deepEqual(analyzeText(''), {
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
    });
  });

  it('サロゲートペア・ZWJ 絵文字・結合文字を正しくカウントする', () => {
    // 𠮷 (サロゲートペア: UTF-8 4 bytes)、😀 (絵文字: UTF-8 4 bytes)、👨‍👩‍👧‍👦 (ZWJ絵文字: UTF-8 25 bytes)
    assert.equal(countGraphemes('𠮷'), 1);
    assert.equal(countGraphemes('😀'), 1);
    assert.equal(countGraphemes('👨‍👩‍👧‍👦'), 1);

    // 結合文字（か + 濁点 U+3099）
    const combined = 'か\u3099';
    assert.equal(countGraphemes(combined), 1);

    const metrics = analyzeText(`𠮷${combined}😀`);
    assert.equal(metrics.totalChars, 3);
    assert.equal(metrics.charsWithoutLineBreaks, 3);
    assert.equal(metrics.fullWidthChars, 3);
    assert.equal(metrics.halfWidthChars, 0);
    assert.equal(metrics.utf8Bytes, 4 + 6 + 4);
  });

  it('CRLF / LF 改行とスペースを正しく区別する', () => {
    const text = 'abc def\r\nあいう　えお\r\n\r\nxyz\r\n';
    const metrics = analyzeText(text);

    assert.equal(countGraphemesWithoutLineBreaks(text), 16); // "abc def" (7) + "あいう　えお" (6) + "xyz" (3)
    assert.equal(countGraphemesWithoutSpaces(text), 14); // スペース2つを除く
    assert.equal(metrics.charsWithoutLineBreaks, 16);
    assert.equal(metrics.charsWithoutSpaces, 14);
    assert.equal(metrics.lineCountWithEmpty, 4); // 末尾の改行は次行開始前として除外
    assert.equal(metrics.lineCountWithoutEmpty, 3);
    assert.equal(metrics.paragraphCount, 2); // 空行で区切られた2段落
    assert.equal(metrics.fullWidthChars, 6); // "あいう　えお"
    assert.equal(metrics.halfWidthChars, 10); // "abc def" + "xyz"
  });

  it('UTF-8 と Shift_JIS のバイト数・全角半角を正しく計算する', () => {
    // 半角ASCII + 半角カナ + 全角日本語
    const text = 'Aｱあ';
    assert.equal(countUtf8Bytes(text), 1 + 3 + 3); // A(1) + ｱ(3) + あ(3)
    assert.equal(countShiftJisBytes(text), 1 + 1 + 2); // A(1) + ｱ(1) + あ(2)

    const metrics = analyzeText(text);
    assert.equal(metrics.fullWidthChars, 1);
    assert.equal(metrics.halfWidthChars, 2);
  });
});
