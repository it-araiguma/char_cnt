export default {
  app: {
    title: '文本计数器',
    input: {
      placeholder: '在此处输入您的文本...',
      clear: '清除'
    },
    counter: {
      characters: '字符数',
      noSpaces: '无空格和换行'
    },
    tools: {
      title: '特定用途计数器',
      genkoTitle: '原稿纸字数换算器',
      genkoDesc: '自动计算400字与200字日文原稿纸页数与行数，包含换行换算及书写规范。'
    }
  },
  layout: {
    header: {
      title: '字符计数器'
    },
    footer: {
      home: '首页',
      genko: '原稿纸字数换算',
      privacy: '隐私政策',
      copyright: '版权所有 ',
      allRights: '保留所有权利。'
    }
  },
  seo: {
    index: {
      title: '字符计数器 - 在线计算文本字符数',
      description: '一个简单的在线工具，用于计算文本中的字符数。同时显示不包含空格和换行符的字符数。',
      keywords: '字符计数器,文本计数器,字数统计,在线工具'
    },
    genko: {
      title: '日文原稿纸换算计数器（400字・200字）页数行数自动计算 - 字符计数器',
      description: '实时自动计算文本换算为400字与200字原稿纸的页数与行数，同时显示考虑换行与空行的实际纸张数及字数估算。',
      keywords: '原稿纸 换算,原稿纸 字数,400字原稿纸 几张,作文 原稿纸 页数,字符计数器'
    },
    privacy: {
      title: '隐私政策 - 字符计数器',
      description: '字符计数器应用程序的隐私政策。',
      keywords: '隐私政策,字符计数器,数据保护'
    }
  },
  genko: {
    title: '原稿纸换算计数器',
    subtitle: '实时自动计算400字与200字原稿纸的页数及行数',
    input: {
      placeholder: '请在此输入或粘贴文本...',
      clear: '清空',
      copy: '复制',
      copied: '已复制到剪贴板',
      sample: '填入示例'
    },
    summary: {
      totalChars: '总字符数',
      noSpaces: '不含空格换行',
      totalLines: '实际总行数（原稿纸）',
      rawLines: '段落数（换行数）'
    },
    cards: {
      actualTitle: '实际纸张换算（考虑换行与空白）',
      actualDesc: '按每行20字计算，准确反映段落换行与空行占用的纸张数。',
      charTitle: '纯字数换算（估算）',
      charDesc: '以总字数除以单页格子数（400字/200字）得出的理论估算值。',
      sheetsUnit: '页',
      exactBadge: '整页无余',
      remainderFormat: '{full}页 又 {remainder}{unit}',
      linesUnit: '行',
      charsUnit: '字',
      preset400: '400字原稿纸（20字×20行）',
      preset200: '200字原稿纸（20字×10行）',
      customPreset: '自定义网格设置'
    },
    custom: {
      title: '自定义原稿纸规格',
      charsPerLine: '每行字数',
      linesPerPage: '每页行数',
      reset: '恢复默认'
    },
    guide: {
      title: '日文原稿纸书写规则与指南',
      subtitle: '作文、读后感、小说创作的基本格式规范',
      rule1Title: '1. 标题、姓名与段落缩进',
      rule1Body: '・标题：写在第一行，上方空2~3格。\n・姓名：写在第二行，下方空1~2格，姓与名之间空1格。\n・段落开头：段落首行必须缩进1格。',
      rule2Title: '2. 标点符号与行头禁则',
      rule2Body: '・句号与逗号不可放在行首第一格。\n・可与上一行末尾字符同挤一格，或悬挂在格子外侧右下方。',
      rule3Title: '3. 对话与引号规范',
      rule3Body: '・对话一般另起一行书写。开头的引号顶格书写，不缩进。',
      rule4Title: '4. 数字与字母的书写方式',
      rule4Body: '・竖排文本中原则上使用汉字数字。\n・若使用阿拉伯数字，通常一格内写入两位半角数字。',
      tableTitle: '字数与400字原稿纸换算参考表',
      tableHeaderChars: '字数标准',
      tableHeaderSheets: '400字纸张数',
      tableHeaderPurpose: '主要用途',
      tableRow1: '400字（1页）：小学生短篇作文、阅读简记',
      tableRow2: '800字（2页）：中考作文、常规读后感',
      tableRow3: '1,200字（3页）：高考小论文、标准读后感竞赛（3页以内）',
      tableRow4: '2,000字（5页）：大学课程报告、高中生竞赛规定（5页以内）',
      tableRow5: '4,000字（10页）：短篇小说、学术论文初稿',
      tableRow6: '8,000字（20页）：中篇小说、毕业论文准备章节'
    }
  },
  privacyPolicy: {
    title: '隐私政策',
    intro: '本网站（以下简称“本站”）致力于保护用户的个人信息，特制定以下隐私政策。使用本站即视为您同意本隐私政策。',
    section1: {
      title: '1. 收集的信息及其目的',
      intro: '本站出于以下目的收集用户信息：',
      cookieTitle: '1.1. Cookie 的使用',
      cookieDesc: '本站使用 Cookie 以提供更舒适的服务体验。Cookie 是保存在用户浏览器中的一部分信息，虽然可能用于识别特定用户，但不包含任何能够识别个人身份的信息。',
      cookiePurposesTitle: 'Cookie 用于以下目的：',
      cookiePurpose1: '分析网站使用情况',
      cookiePurpose2: '提升用户体验',
      cookieReject: '您可以通过浏览器设置拒绝接受 Cookie，但在这种情况下，本站的部分功能可能无法正常运行。',
      analyticsTitle: '1.2. Google Analytics 的使用',
      analyticsDesc1: '本站使用 Google Analytics 分析网站的使用情况。Google Analytics 使用 Cookie 记录用户行为并进行访问分析。由此收集访问者浏览了哪些页面以及停留时间等信息，用于改进网站。',
      analyticsPolicy: 'Google Analytics 收集的数据遵循 Google 的{link}。',
      analyticsPolicyLink: '隐私政策',
      analyticsOptout: '用户可以通过安装 Google 提供的{link}来停用 Google Analytics 的数据收集。',
      analyticsOptoutLink: 'Google Analytics 停用浏览器插件',
      adsenseTitle: '1.3. Google AdSense 的使用',
      adsenseDesc1: '本站通过 Google AdSense 投放广告。Google AdSense 使用 Cookie 根据用户的兴趣展示个性化广告，以提供高度相关的广告内容并最大化广告效果。',
      adsensePolicy: '有关 Google AdSense 相关数据的收集与使用，请参阅{link}。',
      adsensePolicyLink: 'Google 广告政策',
      adsenseOptout: '用户可以在{link}中管理个性化广告的显示。',
      adsenseOptoutLink: 'Google 广告设置页面'
    },
    section2: {
      title: '2. 个人信息的管理',
      desc: '本站将妥善且安全地管理用户的个人信息，并采取必要措施防止未经授权的访问、丢失、篡改或泄露。'
    },
    section3: {
      title: '3. 向第三方提供个人信息',
      desc: '除法律法规要求外，未经用户同意，本站不会将个人信息提供给第三方。'
    },
    section4: {
      title: '4. 个人信息的披露、更正与删除',
      desc: '当用户要求披露、更正或删除其个人信息时，本站在确认本人身份后将及时处理。'
    },
    section5: {
      title: '5. 隐私政策的变更',
      desc: '本隐私政策的内容可能会根据法律法规的修改或本站的运营方针进行调整。修改后的隐私政策自发布于本站之日起生效。'
    },
    section6: {
      title: '6. 联系方式',
      desc: '如有关于本隐私政策的疑问，请通过以下表单与我们联系。',
      contactLink: '咨询表单'
    }
  },
  failed: '操作失败',
  success: '操作成功'
};
