// English translations

export default {
  app: {
    title: 'Text Counter',
    input: {
      placeholder: 'Enter your text here...',
      clear: 'Clear'
    },
    counter: {
      characters: 'Characters',
      noSpaces: 'No Spaces & Linebreaks'
    },
    tools: {
      title: 'Specialized Counters',
      genkoTitle: 'Manuscript Paper (Genko Yoshi) Counter',
      genkoDesc: 'Calculate 400 and 200-character manuscript paper sheets with line breaks and formatting guide.',
      reportTitle: 'Report & Essay Character Checker',
      reportDesc: 'Check progress and target compliance (±10%, 80%-100%, within limit) for 800-4000+ character reports.'
    }
  },
  layout: {
    header: {
      title: 'Character Counter'
    },
    footer: {
      home: 'Home',
      genko: 'Manuscript Paper Counter',
      report: 'Report Checker',
      privacy: 'Privacy Policy',
      copyright: 'Copyright ',
      allRights: 'All Rights Reserved.'
    }
  },
  seo: {
    index: {
      title: 'Character Counter - Count Text Characters Online',
      description: 'A simple online tool to count characters in your text. Also shows character count without spaces and line breaks.',
      keywords: 'character counter,text counter,word count,online tool'
    },
    genko: {
      title: 'Genko Yoshi Manuscript Paper Counter (400 / 200 chars) - Character Counter',
      description: 'Automatically calculates the number of Japanese manuscript paper sheets (400 and 200 characters). Real-time sheet and line calculation considering line breaks.',
      keywords: 'manuscript paper,genko yoshi counter,japanese manuscript sheet,character count'
    },
    report: {
      title: 'Report & Essay Character Checker (Target & Progress) - Character Counter',
      description: 'Check real-time progress and target compliance (±10%, 80%-100%, within limit) for academic reports and essays.',
      keywords: 'report character counter,essay length checker,target character count'
    },
    privacy: {
      title: 'Privacy Policy - Character Counter',
      description: 'Privacy policy for the Character Counter application.',
      keywords: 'privacy policy,character counter,data protection'
    }
  },
  genko: {
    title: 'Japanese Manuscript Paper (Genko Yoshi) Counter',
    subtitle: 'Real-time calculation of sheet and line counts for 400 and 200-character paper',
    input: {
      placeholder: 'Type or paste your text here...',
      clear: 'Clear',
      copy: 'Copy',
      copied: 'Copied to clipboard',
      sample: 'Insert Sample'
    },
    summary: {
      totalChars: 'Total Characters',
      noSpaces: 'Without Spaces & Linebreaks',
      totalLines: 'Total Lines (Paper basis)',
      rawLines: 'Paragraphs'
    },
    cards: {
      actualTitle: 'Actual Paper Calculation (Linebreaks considered)',
      actualDesc: 'Based on 20 chars/line. Reflects blank lines, margin breaks, and hanging punctuation.',
      charTitle: 'Character Division (Estimate)',
      charDesc: 'Simple theoretical calculation dividing character count (excluding linebreaks) by grid size (400 or 200).',
      sheetsUnit: ' sheets',
      exactBadge: 'Exact',
      remainderFormat: '{full} sheets and {remainder} {unit}',
      linesUnit: 'lines',
      charsUnit: 'chars',
      preset400: '400-char Genko Yoshi (20 chars x 20 lines)',
      preset200: '200-char Genko Yoshi (20 chars x 10 lines)',
      customPreset: 'Custom Grid'
    },
    options: {
      halfWidthTwoPerCell: 'Count 2 half-width alphanumeric characters per square'
    },
    custom: {
      title: 'Customize Paper Grid',
      charsPerLine: 'Characters per line',
      linesPerPage: 'Lines per sheet',
      reset: 'Reset to default',
      invalidRange: 'Enter an integer between {min} and {max}'
    },
    guide: {
      title: 'Manuscript Paper Rules & Writing Guide',
      subtitle: 'Essential guidelines for Japanese essays, novel writing, and book reports',
      rule1Title: '1. Title, Name, and Paragraph Indentation',
      rule1Body: '・Title: Write on the first line, leaving 2-3 empty squares at the top.\n・Name: Write on the second line, leaving 1-2 empty squares at the bottom.\n・Paragraphs: Start each paragraph with a 1-square indentation.',
      rule2Title: '2. Punctuation Marks and Line-head Prohibition',
      rule2Body: '・Periods and commas should never appear at the top of a line.\n・Place them in the last square alongside the last character, or hang them in the outer margin.',
      rule3Title: '3. Dialogue and Quotation Marks',
      rule3Body: '・Start dialogues on a new line. The opening quotation mark occupies the top square without indentation.',
      rule4Title: '4. Numbers and Alphabetical Characters',
      rule4Body: '・Kanji numerals are generally preferred for vertical writing.\n・Arabic numerals can be written two digits per square.',
      tableTitle: 'Character Count to 400-Character Sheets Conversion Table',
      tableHeaderChars: 'Characters',
      tableHeaderSheets: '400-char Sheets',
      tableHeaderPurpose: 'Standard Purpose',
      tableRow1: '400 chars (1 sheet): Short essay / Elementary report',
      tableRow2: '800 chars (2 sheets): High school essay / Short book report',
      tableRow3: '1,200 chars (3 sheets): College entrance essay / Contest guideline (within 3 sheets)',
      tableRow4: '2,000 chars (5 sheets): University report / High school contest guideline (within 5 sheets)',
      tableRow5: '4,000 chars (10 sheets): Short story / Academic paper',
      tableRow6: '8,000 chars (20 sheets): Novelette / Thesis chapter'
    }
  },
  report: {
    title: 'Report & Essay Character Checker',
    subtitle: 'Real-time progress bar and compliance check (±10%, 80%-100%, within limit)',
    units: {
      chars: 'chars'
    },
    target: {
      title: 'Target Length & Settings',
      presetFormat: '{count} chars',
      customLabel: 'Custom target',
      excludeSpaces: 'Exclude spaces & linebreaks'
    },
    rule: {
      title: 'Target Rule Pattern',
      around10: '±10% (Approx.)',
      min80: '80%–100% (Minimum 80%)',
      max100: 'Within 100% (Max limit)'
    },
    status: {
      ok: 'OK',
      short: 'Short',
      over: 'Over',
      empty: 'Empty',
      rangeFormat: 'Allowed range: {min} - {max} chars',
      okMessage: 'Your text is within the target range.',
      shortMessage: '{diff} more characters needed to reach the minimum.',
      overMessage: '{diff} characters over the maximum limit.',
      emptyMessage: 'Enter your text to check progress against your target length.'
    },
    input: {
      placeholder: 'Type or paste your report or essay here...',
      clear: 'Clear',
      copy: 'Copy',
      copied: 'Copied to clipboard',
      sample: 'Insert Sample'
    },
    summary: {
      totalChars: 'Total Characters',
      noSpaces: 'Without Spaces & Linebreaks',
      paragraphs: 'Paragraphs',
      genkoSheets: '400-char Sheets (est.)'
    },
    guide: {
      title: 'Report & Essay Length Guidelines',
      subtitle: 'What counts toward the character limit and how to interpret target ranges',
      criteriaTitle: 'What Should Be Included in the Count?',
      criteriaHeaderItem: 'Element',
      criteriaHeaderInclude: 'Included?',
      criteriaHeaderNote: 'Standard Guideline',
      criteriaInclude: 'Usually Included',
      criteriaExclude: 'Usually Excluded',
      criteriaConditional: 'Check Guidelines',
      criteriaRow1Item: 'Title, Name & Student ID',
      criteriaRow1Note: 'Character limits usually apply to the main body text only.',
      criteriaRow2Item: 'Section Headings',
      criteriaRow2Note: 'Headings are part of the body structure and are generally counted.',
      criteriaRow3Item: 'References & Bibliography',
      criteriaRow3Note: 'Typically excluded, though some assignments specify including references.',
      criteriaRow4Item: 'Figures, Captions & Footnotes',
      criteriaRow4Note: 'Text inside figures is excluded; check your syllabus for captions and footnotes.',
      criteriaRow5Item: 'Spaces & Linebreaks',
      criteriaRow5Note: 'Word processors often exclude spaces, whereas online LMS forms usually count them.',
      rule1Title: '1. Interpreting Target Phrasing',
      rule1Body: '・"Approx. X chars": Aim for within ±10% of the target.\n・"At least X chars": Exceed the target without going overly long (+10% to +20%).\n・"Up to X chars": Never exceed the limit; aim for at least 80% of the maximum.',
      rule2Title: '2. Word Processor vs. Web Form Counts',
      rule2Body: '・Desktop editors often exclude spaces by default, while web submission forms count every character including linebreaks.\n・Use the toggle above to check both modes instantly.',
      tableTitle: 'Common Report & Essay Length Benchmarks',
      tableHeaderChars: 'Target',
      tableHeaderVolume: 'Estimated Volume',
      tableHeaderPurpose: 'Common Use Case',
      tableRow1Chars: '800 chars',
      tableRow1Volume: '~0.7 A4 page / 2 sheets',
      tableRow1Purpose: 'Reaction paper, short essay',
      tableRow2Chars: '1,200 chars',
      tableRow2Volume: '~1 A4 page / 3 sheets',
      tableRow2Purpose: 'Entrance exam essay, standard short report',
      tableRow3Chars: '2,000 chars',
      tableRow3Volume: '~1.5–2 A4 pages / 5 sheets',
      tableRow3Purpose: 'University term report, seminar assignment',
      tableRow4Chars: '4,000 chars',
      tableRow4Volume: '~3–3.5 A4 pages / 10 sheets',
      tableRow4Purpose: 'Research paper, final course report'
    }
  },
  privacyPolicy: {
    title: 'Privacy Policy',
    intro: 'This website (hereinafter referred to as "the Site") is committed to protecting users\' personal information and has established the following Privacy Policy. By using the Site, you are deemed to have agreed to this Privacy Policy.',
    section1: {
      title: '1. Information Collected and Its Purpose',
      intro: 'The Site collects user information for the following purposes:',
      cookieTitle: '1.1. Use of Cookies',
      cookieDesc: 'The Site uses cookies to provide a better user experience. A cookie is a piece of information stored on your browser. While it may be used to identify a specific browser session, it contains no personally identifiable information.',
      cookiePurposesTitle: 'Cookies are used for the following purposes:',
      cookiePurpose1: 'Analysis of site usage',
      cookiePurpose2: 'Improvement of user experience',
      cookieReject: 'You can disable cookies through your browser settings; however, some features of the Site may not function properly as a result.',
      analyticsTitle: '1.2. Use of Google Analytics',
      analyticsDesc1: 'The Site uses Google Analytics to analyze website traffic. Google Analytics uses cookies to record user behavior and perform access analytics. This helps us understand which pages visitors view and how long they stay, allowing us to improve the site.',
      analyticsPolicy: 'Data collected by Google Analytics is governed by Google\'s {link}.',
      analyticsPolicyLink: 'Privacy Policy',
      analyticsOptout: 'You can opt out of Google Analytics data collection by installing the {link} provided by Google.',
      analyticsOptoutLink: 'Google Analytics Opt-out Browser Add-on',
      adsenseTitle: '1.3. Use of Google AdSense',
      adsenseDesc1: 'The Site delivers advertisements through Google AdSense. Google AdSense uses cookies to display personalized ads based on user interests, providing more relevant ads and maximizing advertising effectiveness.',
      adsensePolicy: 'For more information on data collection and use regarding Google AdSense, please review {link}.',
      adsensePolicyLink: 'Google Ads Policies',
      adsenseOptout: 'You can manage personalized ad settings on the {link}.',
      adsenseOptoutLink: 'Google Ad Settings page'
    },
    section2: {
      title: '2. Management of Personal Information',
      desc: 'The Site manages users\' personal information properly and securely, taking necessary measures to protect it from unauthorized access, loss, alteration, or disclosure.'
    },
    section3: {
      title: '3. Provision of Personal Information to Third Parties',
      desc: 'The Site will not provide personal information to third parties without prior consent, except where required by law.'
    },
    section4: {
      title: '4. Disclosure, Correction, and Deletion of Personal Information',
      desc: 'Upon request from a user to disclose, correct, or delete their personal information, the Site will promptly respond after verifying the identity of the requester.'
    },
    section5: {
      title: '5. Changes to the Privacy Policy',
      desc: 'The contents of this Privacy Policy may be revised in response to amendments to laws or changes in site operation policies. The revised Privacy Policy becomes effective upon publication on the Site.'
    },
    section6: {
      title: '6. Contact Us',
      desc: 'For inquiries regarding this Privacy Policy, please contact us using the form below.',
      contactLink: 'Contact Form'
    }
  },
  pwa: {
    updateAvailable: 'A new version is available.',
    reload: 'Reload'
  },
  failed: 'Action failed',
  success: 'Action was successful'
};
