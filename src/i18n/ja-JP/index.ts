export default {
  app: {
    title: 'テキストカウンター',
    input: {
      placeholder: 'ここにテキストを入力してください...',
      clear: 'クリア',
      copy: 'コピー',
      copied: 'クリップボードにコピーしました'
    },
    counter: {
      characters: '文字数',
      charactersHint: 'スペースや改行を含めた、見た目の文字数（サロゲートペア・絵文字も1文字としてカウント）',
      noLineBreaks: '改行なし（スペース含む）',
      noLineBreaksHint: '改行だけを除き、半角・全角スペースを含めた文字数',
      noSpaces: '改行・スペースなし',
      noSpacesHint: '改行・半角スペース・全角スペース・タブを除いた実質文字数',
      linesWithEmpty: '行数（空行含む）',
      linesWithEmptyHint: '改行で区切られたすべての行数（空行を含む）',
      linesWithoutEmpty: '行数（空行除く）',
      linesWithoutEmptyHint: '空白のみの行・空行を除いた実質的な行数',
      paragraphs: '段落数',
      paragraphsHint: '空行（連続改行）で区切られた段落の数',
      fullWidth: '全角文字',
      fullWidthHint: 'ひらがな・カタカナ・漢字・全角記号・絵文字などの文字数（改行除く）',
      halfWidth: '半角文字',
      halfWidthHint: '半角英数字・半角記号・半角スペース・半角カタカナの文字数（改行除く）',
      utf8Bytes: 'バイト数 (UTF-8)',
      utf8BytesHint: 'UTF-8 エンコード時の正確なバイト数（改行含む）',
      shiftJisBytes: 'バイト数 (Shift_JIS)',
      shiftJisBytesHint: '半角1バイト・全角2バイトとして計算した Shift_JIS 概算バイト数'
    },
    tools: {
      title: '用途別便利カウンター',
      genkoTitle: '原稿用紙換算カウンター',
      genkoDesc: '400字・200字詰め原稿用紙の枚数・行数を自動計算。改行を考慮した実枚数とマナー解説付き。',
      reportTitle: 'レポート・小論文文字数チェッカー',
      reportDesc: '800〜4000字などの目標文字数に対する進捗率と達成判定（±10%・8割〜10割・10割以内）を自動チェック。'
    }
  },
  layout: {
    header: {
      title: '文字数カウント'
    },
    footer: {
      home: 'ホーム',
      genko: '原稿用紙換算',
      report: 'レポート文字数',
      privacy: 'プライバシーポリシー',
      copyright: 'Copyright ',
      allRights: 'All Rights Reserved.'
    }
  },
  seo: {
    index: {
      title: '文字数カウント - オンラインで簡単に文字数をカウント',
      description: 'テキストの文字数を簡単にカウントできるオンラインツール。スペースや改行を除いた文字数も同時に確認できます。',
      keywords: '文字数カウント,文字カウンター,テキストカウンター,オンラインツール'
    },
    genko: {
      title: '原稿用紙換算カウンター（400字・200字）枚数・行数を自動計算 - 文字数カウント',
      description: '入力したテキストが原稿用紙何枚分になるかを瞬時に自動計算。400字詰め（20×20）・200字詰め（20×10）に対応し、文字数割りの目安と改行・空きマスを考慮した正確な枚数を同時に表示します。原稿用紙の書き方ルールも解説。',
      keywords: '原稿用紙 換算,原稿用紙 文字数,400字詰め原稿用紙 何枚,作文 原稿用紙 枚数,文字数カウント'
    },
    report: {
      title: 'レポート・小論文文字数チェッカー（目標文字数・達成判定） - 文字数カウント',
      description: '大学レポートや小論文の目標文字数（800字・1200字・2000字・4000字・任意指定）に対する進捗率と達成判定（±10%・8割〜10割・10割以内）をリアルタイムで確認できるオンラインツール。タイトルや参考文献を文字数に含めるかの基準も解説。',
      keywords: 'レポート 文字数 カウント,小論文 文字数 カウント,レポート 文字数 8割,レポート 文字数 基準,文字数カウント'
    },
    privacy: {
      title: 'プライバシーポリシー - 文字数カウント',
      description: '文字数カウントアプリのプライバシーポリシーについてご確認いただけます。',
      keywords: 'プライバシーポリシー,文字数カウント,個人情報保護'
    }
  },
  genko: {
    title: '原稿用紙換算カウンター',
    subtitle: '400字詰め・200字詰めの枚数・行数をリアルタイムに自動計算',
    input: {
      placeholder: 'ここにテキストを入力または貼り付けてください...',
      clear: 'クリア',
      copy: 'コピー',
      copied: 'クリップボードにコピーしました',
      sample: '例文を入力'
    },
    summary: {
      totalChars: '全文字数',
      noSpaces: '改行・空白なし',
      totalLines: '実総行数（原稿用紙換算）',
      rawLines: '段落数（改行区切り）'
    },
    cards: {
      actualTitle: '実用紙換算（改行・空きマス考慮）',
      actualDesc: '1行20字換算。改行による余白・空行・行頭禁則（句読点等のぶら下げ）を反映した実際の用紙枚数です。',
      charTitle: '文字数ベース換算（目安）',
      charDesc: '改行を除いた文字数をマス目数（400字・200字）で単純に割った理論値です。',
      sheetsUnit: '枚',
      exactBadge: '端数なし',
      remainderFormat: '{full}枚 と {remainder}{unit}',
      linesUnit: '行',
      charsUnit: '字',
      preset400: '400字詰め原稿用紙（20字×20行）',
      preset200: '200字詰め原稿用紙（20字×10行）',
      customPreset: 'カスタム設定（自由行数・文字数）'
    },
    options: {
      halfWidthTwoPerCell: '半角英数字を1マスに2文字として換算'
    },
    custom: {
      title: '用紙マス目設定のカスタマイズ',
      charsPerLine: '1行の文字数',
      linesPerPage: '1枚の行数',
      reset: '標準に戻す',
      invalidRange: '{min}〜{max}の整数を入力してください'
    },
    guide: {
      title: '原稿用紙の書き方・基本マナー解説',
      subtitle: '作文・読書感想文・小論文・公募小説で役立つ原稿用紙のルール',
      rule1Title: '1. 題名・氏名・段落の書き出し',
      rule1Body: '・題名（タイトル）: 1行目に書き、上を2〜3マス空けて書き始めます。\n・氏名（名前）: 2行目に書き、下を1〜2マス空けて名字と名前の間は1マス空けます。\n・段落の書き出し: 本文の始まりや段落が変わる行頭は、必ず「1マス空けて（字下げ）」書き始めます。',
      rule2Title: '2. 句読点（。、）と禁則処理・ぶら下げ',
      rule2Body: '・句読点を行頭（一番上のマス）に置いてはいけません（行頭禁則）。\n・行の最後のマスに最後の文字と句読点を一緒に入れるか、マスの欄外（右下）に「ぶら下げ」て書きます。\n・閉じ括弧（」）と句点（。）が重なる場合は、同じ1マスの中に「。」と「」」をまとめて書きます。',
      rule3Title: '3. 会話文（「かぎ括弧」）の扱い',
      rule3Body: '・会話文は原則として新しい行から書き始めます。「（始まりのかぎ括弧）は一番上のマスに置きます（1マス空けません）。\n・会話文が2行以上にわたる場合、2行目以降の字下げは学校や公募の指示に従います（字下げしない方式、または1マス空ける方式があります）。\n・会話文に続く地の文は、次の行から1マス空けて書き始めます。',
      rule4Title: '4. 数字・アルファベットの書き方（縦書き）',
      rule4Body: '・縦書きの原稿用紙では、原則として漢数字（一、二、三、十、百…）を使用します。\n・西暦や日付などで算用数字（アラビア数字）を用いる場合、1マスに2文字（半角「20」「26」など）収めて書くのが一般的です。\n・英単語も短縮語（AI、SNS等）は大文字で1マスに2文字、または縦書きで1マス1文字ずつ書きます。',
      tableTitle: '文字数と400字詰め原稿用紙の換算目安表',
      tableHeaderChars: '文字数目安',
      tableHeaderSheets: '400字詰め用紙枚数',
      tableHeaderPurpose: '主な用途・提出目安',
      tableRow1: '400字（1枚）: 読書感想文（低学年）、ミニ作文',
      tableRow2: '800字（2枚）: 高校入試小論文、短めの読書感想文',
      tableRow3: '1,200字（3枚）: 大学入試小論文、読書感想文（小・中学生の全国コンクール規定：3枚以内など）',
      tableRow4: '2,000字（5枚）: 大学レポート、読書感想文（高校生規定：5枚以内など）',
      tableRow5: '4,000字（10枚）: 短編小説、学術レポート、本格的小論文',
      tableRow6: '8,000字（20枚）: 中編小説、卒業論文の準備章'
    }
  },
  report: {
    title: 'レポート・小論文文字数チェッカー',
    subtitle: '目標文字数に対する進捗率と達成判定（±10%・8割〜10割・10割以内）をリアルタイムに表示',
    units: {
      chars: '字'
    },
    target: {
      title: '目標文字数と判定条件',
      presetFormat: '{count}字',
      customLabel: '任意の目標文字数',
      excludeSpaces: '空白・改行を除外して判定'
    },
    rule: {
      title: '課題の文字数指定パターン',
      around10: '±10%（〇〇字程度）',
      min80: '8割〜10割（以上・目安）',
      max100: '10割以内（〇〇字以内）'
    },
    status: {
      ok: 'OK（達成）',
      short: '不足',
      over: '超過',
      empty: '未入力',
      rangeFormat: '許容範囲: {min} 〜 {max}字',
      okMessage: '指定の許容範囲内に収まっています。',
      shortMessage: '許容範囲の下限まであと {diff} 字不足しています。',
      overMessage: '許容範囲の上限を {diff} 字超過しています。',
      emptyMessage: 'テキストを入力すると目標文字数に対する達成判定を表示します。'
    },
    input: {
      placeholder: 'ここにレポートや小論文の本文を入力または貼り付けてください...',
      clear: 'クリア',
      copy: 'コピー',
      copied: 'クリップボードにコピーしました',
      sample: '例文を入力'
    },
    summary: {
      totalChars: '全文字数',
      noSpaces: '改行・空白なし',
      paragraphs: '段落数',
      genkoSheets: '400字換算（枚）'
    },
    guide: {
      title: 'レポート・小論文の文字数ルール解説',
      subtitle: 'タイトル・参考文献・見出し・図表キャプションの扱いと指定表現別の目安',
      criteriaTitle: '文字数に含める・含めないの判断基準',
      criteriaHeaderItem: '対象項目',
      criteriaHeaderInclude: 'カウント有無',
      criteriaHeaderNote: '一般的な判断基準・注意点',
      criteriaInclude: '原則含める',
      criteriaExclude: '原則含めない',
      criteriaConditional: '要確認（条件次第）',
      criteriaRow1Item: 'タイトル・氏名・学籍番号',
      criteriaRow1Note: '課題の文字数指定は原則「本文のみ」が対象です。表紙やタイトル行は除いてカウントします。',
      criteriaRow2Item: '見出し（章・節タイトル）',
      criteriaRow2Note: '「1. はじめに」「2. 考察」などの見出しは本文の構成要素として文字数に含めるのが一般的です。',
      criteriaRow3Item: '参考文献・引用リスト',
      criteriaRow3Note: '通常は本文の文字数に含めませんが、学会や講義によっては「参考文献を含む」指定もあるため課題要項を確認してください。',
      criteriaRow4Item: '図表・キャプション・脚注',
      criteriaRow4Note: '図表内のテキストは原則含めません。図表タイトル（キャプション）や注釈は指定がなければ除外するのが一般的です。',
      criteriaRow5Item: 'スペース・改行',
      criteriaRow5Note: 'Wordの「文字数（スペースを含めない）」を基準とする場合が多いですが、LMS等のWebフォーム提出では改行・スペースも1文字として数えられます。',
      rule1Title: '1. 「〇〇字程度」「〇〇字以上」「〇〇字以内」の許容範囲',
      rule1Body: '・「〇〇字程度」: 指定文字数の ±10% が一般的な目安です（例：2,000字程度なら 1,800〜2,200字）。\n・「〇〇字以上」: 指定文字数を必ず超えた上で、上限は +10〜20% 程度に収めると読みやすくなります。\n・「〇〇字以内」: 1文字でも超過すると減点・提出不可になる場合があります。最低でも8割以上（例：2,000字以内なら 1,600〜2,000字）書くと充実した内容になります。',
      rule2Title: '2. WordとWebフォーム（LMS）のカウント差に注意',
      rule2Body: '・Microsoft Wordのステータスバーに表示される「文字数」は標準でスペース・改行を含みません。\n・一方、大学のLMS（Moodle、Google Classroom、WebClass等）のテキストボックスに入力する場合は、改行や全角スペースも1文字として制限文字数にカウントされることがあります。\n・本ツールでは上部の「空白・改行を除外して判定」トグルで両方の基準をすぐに確認できます。',
      tableTitle: 'よく指定されるレポート・小論文の文字数目安',
      tableHeaderChars: '指定文字数',
      tableHeaderVolume: '分量の目安',
      tableHeaderPurpose: '主な用途',
      tableRow1Chars: '800字',
      tableRow1Volume: 'A4約0.7枚 / 原稿用紙2枚',
      tableRow1Purpose: '講義のリアクションペーパー、高校入試小論文',
      tableRow2Chars: '1,200字',
      tableRow2Volume: 'A4約1枚 / 原稿用紙3枚',
      tableRow2Purpose: '大学入試小論文、標準的な小レポート',
      tableRow3Chars: '2,000字',
      tableRow3Volume: 'A4約1.5〜2枚 / 原稿用紙5枚',
      tableRow3Purpose: '大学の期末レポート、ゼミ課題（最も多い形式）',
      tableRow4Chars: '4,000字',
      tableRow4Volume: 'A4約3〜3.5枚 / 原稿用紙10枚',
      tableRow4Purpose: '専門科目の期末論文、研究報告レポート'
    }
  },
  privacyPolicy: {
    title: 'プライバシーポリシー',
    intro: '当サイト（以下、「本サイト」）は、ユーザーの個人情報の保護に努め、以下のプライバシーポリシーを定めています。本サイトを利用することで、このプライバシーポリシーに同意したものとみなします。',
    section1: {
      title: '1. 収集する情報とその目的',
      intro: '本サイトでは、以下の目的のためにユーザーの情報を収集します。',
      cookieTitle: '1.1. Cookie（クッキー）の利用',
      cookieDesc: '本サイトでは、より快適にサービスを利用していただくためにCookie（クッキー）を使用しています。Cookieとは、ユーザーのブラウザに保存される情報の一部であり、特定のユーザーを識別するために使用されることがありますが、個人を特定できる情報は含まれません。',
      cookiePurposesTitle: 'Cookieは次の目的で使用されます：',
      cookiePurpose1: 'サイトの利用状況の分析',
      cookiePurpose2: 'ユーザー体験の向上',
      cookieReject: 'ブラウザの設定により、Cookieの受け入れを拒否することも可能ですが、その場合は本サイトの一部機能が正しく動作しないことがあります。',
      analyticsTitle: '1.2. Google Analyticsの利用',
      analyticsDesc1: '本サイトでは、Google Analyticsを使用してサイトの利用状況を分析しています。Google Analyticsは、Cookieを使用してユーザーの行動を記録し、アクセス解析を行います。これにより、訪問者がどのページを閲覧しているか、どれだけの時間滞在しているかなどの情報を収集し、サイトの改善に役立てています。',
      analyticsPolicy: 'Google Analyticsによって収集されたデータは、Googleの{link}に基づくものとなります。',
      analyticsPolicyLink: 'プライバシーポリシー',
      analyticsOptout: 'ユーザーはGoogleの提供する{link}をインストールすることで、Google Analyticsによるデータの収集を無効にすることが可能です。',
      analyticsOptoutLink: 'Google Analyticsオプトアウトアドオン',
      adsenseTitle: '1.3. Google AdSenseの利用',
      adsenseDesc1: '本サイトでは、Google AdSenseによる広告配信を行っています。Google AdSenseは、ユーザーの興味に基づくパーソナライズされた広告を表示するためにCookieを使用します。これにより、ユーザーに関連性の高い広告を提供し、広告の効果を最大化します。',
      adsensePolicy: 'Google AdSenseに関連するデータの収集と使用に関しては、{link}をご確認ください。',
      adsensePolicyLink: 'Googleの広告ポリシー',
      adsenseOptout: 'ユーザーは、{link}でパーソナライズド広告の表示を管理することができます。',
      adsenseOptoutLink: 'Google広告設定ページ'
    },
    section2: {
      title: '2. 個人情報の管理',
      desc: '本サイトでは、ユーザーの個人情報を適切かつ安全に管理し、不正アクセス、紛失、改ざん、漏洩から保護するために必要な措置を講じます。'
    },
    section3: {
      title: '3. 個人情報の第三者提供',
      desc: 'ユーザーの個人情報を、法令に基づく場合を除き、ユーザーの同意を得ることなく第三者に提供することはありません。'
    },
    section4: {
      title: '4. 個人情報の開示・訂正・削除',
      desc: 'ユーザーから自己の個人情報の開示、訂正、削除の依頼があった場合には、本人確認の上、速やかに対応いたします。'
    },
    section5: {
      title: '5. プライバシーポリシーの変更',
      desc: '本プライバシーポリシーの内容は、法令の改正や本サイトの運営方針に応じて変更されることがあります。変更後のプライバシーポリシーは、本サイトに掲載された時点で効力を生じます。'
    },
    section6: {
      title: '6. お問い合わせ先',
      desc: 'プライバシーポリシーに関するお問い合わせは、以下のフォームでご連絡ください。',
      contactLink: '問い合わせフォーム'
    }
  },
  pwa: {
    updateAvailable: '新しいバージョンが利用可能です。',
    reload: '更新する'
  },
  failed: 'アクションに失敗しました',
  success: 'アクションが成功しました'
};
