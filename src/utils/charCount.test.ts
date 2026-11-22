import { describe, expect, it } from 'vitest';
import {
  countGraphemes,
  countGraphemesWithoutLinebreaks,
  countGraphemesWithoutSpaces
} from './charCount';

describe('charCount', () => {
  it('空文字を0としてカウントする', () => {
    expect(countGraphemes('')).toBe(0);
    expect(countGraphemesWithoutSpaces('')).toBe(0);
    expect(countGraphemesWithoutLinebreaks('')).toBe(0);
  });

  it('サロゲートペア（𠮷、😀）を1文字としてカウントする', () => {
    expect(countGraphemes('𠮷')).toBe(1);
    expect(countGraphemes('😀')).toBe(1);
    expect(countGraphemes('𠮷野家😀')).toBe(4);
  });

  it('ZWJ 結合絵文字（👨‍👩‍👧‍👦）を1文字としてカウントする', () => {
    expect(countGraphemes('👨‍👩‍👧‍👦')).toBe(1);
    expect(countGraphemes('家族👨‍👩‍👧‍👦です')).toBe(5);
  });

  it('結合文字（が＝か＋゛）を1文字としてカウントする', () => {
    const combiningGa = 'か\u3099';
    expect(combiningGa.length).toBe(2);
    expect(countGraphemes(combiningGa)).toBe(1);
  });

  it('異体字セレクタ（IVS）付きの文字を1文字としてカウントする', () => {
    const ivsKatsura = '葛\u{E0100}';
    expect(countGraphemes(ivsKatsura)).toBe(1);
    expect(countGraphemes(`${ivsKatsura}飾`)).toBe(2);
  });

  it('CRLF 改行の扱いを正しくカウントする', () => {
    const crlf = 'あ\r\nい';
    expect(countGraphemes(crlf)).toBe(3);
    expect(countGraphemesWithoutSpaces(crlf)).toBe(2);
    expect(countGraphemesWithoutLinebreaks(crlf)).toBe(2);
  });

  it('全角スペース・半角スペース・NBSP を除外してカウントする', () => {
    const text = 'あ　い う\u00A0え';
    expect(countGraphemes(text)).toBe(7);
    expect(countGraphemesWithoutSpaces(text)).toBe(4);
    expect(countGraphemesWithoutLinebreaks(text)).toBe(7);
  });
});
