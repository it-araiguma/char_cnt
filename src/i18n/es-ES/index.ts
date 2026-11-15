export default {
  app: {
    title: 'Contador de texto',
    input: {
      placeholder: 'Introduce tu texto aquí...',
      clear: 'Borrar'
    },
    counter: {
      characters: 'Caracteres',
      noSpaces: 'Sin espacios ni saltos de línea'
    },
    tools: {
      title: 'Contadores especializados',
      genkoTitle: 'Contador de Genko Yoshi (papel manuscrito)',
      genkoDesc: 'Calcula hojas de 400 y 200 caracteres con renglones y guía de formato.'
    }
  },
  layout: {
    header: {
      title: 'Contador de caracteres'
    },
    footer: {
      home: 'Inicio',
      genko: 'Contador de Genko Yoshi',
      privacy: 'Política de privacidad',
      copyright: 'Copyright ',
      allRights: 'Todos los derechos reservados.'
    }
  },
  seo: {
    index: {
      title: 'Contador de caracteres - Cuenta caracteres en línea',
      description: 'Una herramienta en línea simple para contar los caracteres de tu texto. También muestra el número de caracteres sin espacios ni saltos de línea.',
      keywords: 'contador de caracteres,contador de texto,herramienta en línea'
    },
    genko: {
      title: 'Contador de Genko Yoshi (papel manuscrito 400/200 caracteres) - Contador de caracteres',
      description: 'Calcula automáticamente el número de hojas y renglones de papel manuscrito japonés (400 y 200 caracteres) teniendo en cuenta saltos de línea.',
      keywords: 'genko yoshi,papel manuscrito japonés,contador de caracteres,número de hojas'
    },
    privacy: {
      title: 'Política de privacidad - Contador de caracteres',
      description: 'Política de privacidad de la aplicación Contador de caracteres.',
      keywords: 'política de privacidad,contador de caracteres,protección de datos'
    }
  },
  genko: {
    title: 'Contador de Papel Manuscrito (Genko Yoshi)',
    subtitle: 'Cálculo en tiempo real de hojas y líneas para papel de 400 y 200 caracteres',
    input: {
      placeholder: 'Escribe o pega tu texto aquí...',
      clear: 'Borrar',
      copy: 'Copiar',
      copied: 'Copiado al portapapeles',
      sample: 'Insertar ejemplo'
    },
    summary: {
      totalChars: 'Caracteres totales',
      noSpaces: 'Sin espacios ni saltos',
      totalLines: 'Líneas totales (Genko Yoshi)',
      rawLines: 'Párrafos'
    },
    cards: {
      actualTitle: 'Cálculo real en papel (con saltos de línea)',
      actualDesc: 'Basado en 20 caracteres por línea, reflejando fielmente espacios en blanco y párrafos.',
      charTitle: 'Cálculo por división de caracteres (estimación)',
      charDesc: 'División simple de caracteres totales entre cuadrícula (400 o 200).',
      sheetsUnit: ' hojas',
      exactBadge: 'Exacto',
      remainderFormat: '{full} hojas y {remainder} {unit}',
      linesUnit: 'líneas',
      charsUnit: 'caracteres',
      preset400: 'Genko Yoshi de 400 caracteres (20 car. x 20 líneas)',
      preset200: 'Genko Yoshi de 200 caracteres (20 car. x 10 líneas)',
      customPreset: 'Cuadrícula personalizada'
    },
    custom: {
      title: 'Personalizar cuadrícula',
      charsPerLine: 'Caracteres por línea',
      linesPerPage: 'Líneas por hoja',
      reset: 'Restablecer'
    },
    guide: {
      title: 'Guía y reglas para escribir en Genko Yoshi',
      subtitle: 'Normas fundamentales para composiciones y redacción en japonés',
      rule1Title: '1. Título, nombre y sangría',
      rule1Body: '・Título: Primera línea dejando 2 o 3 casillas libres al inicio.\n・Nombre: Segunda línea dejando 1 o 2 casillas libres al final.\n・Sangría: Iniciar cada párrafo con 1 casilla de sangría.',
      rule2Title: '2. Signos de puntuación y prohibición al inicio de línea',
      rule2Body: '・Puntos y comas nunca deben colocarse al inicio de un renglón.\n・Deben colocarse junto con el último carácter o suspenderse en el margen derecho inferior.',
      rule3Title: '3. Diálogos y comillas',
      rule3Body: '・Los diálogos inician en una nueva línea con la comilla de apertura sin sangría.',
      rule4Title: '4. Números y alfabeto',
      rule4Body: '・En escritura vertical se prefieren números en kanji.\n・Los números arábigos suelen colocarse de dos en dos por casilla.',
      tableTitle: 'Tabla de conversión de caracteres a hojas de 400 caracteres',
      tableHeaderChars: 'Caracteres',
      tableHeaderSheets: 'Hojas (400 car.)',
      tableHeaderPurpose: 'Uso habitual',
      tableRow1: '400 car. (1 hoja): Redacción breve escolar',
      tableRow2: '800 car. (2 hojas): Ensayo de secundaria',
      tableRow3: '1.200 car. (3 hojas): Ensayo de ingreso / Reseña estándar (hasta 3 hojas)',
      tableRow4: '2.000 car. (5 hojas): Informe universitario / Pauta de concurso (hasta 5 hojas)',
      tableRow5: '4.000 car. (10 hojas): Relato corto / Artículo académico',
      tableRow6: '8.000 car. (20 hojas): Novela corta / Capítulo de tesis'
    }
  },
  privacyPolicy: {
    title: 'Política de privacidad',
    intro: 'Este sitio web (en adelante, "el Sitio") se compromete a proteger la información personal de los usuarios y establece la siguiente Política de Privacidad. Al utilizar el Sitio, se considera que acepta esta Política de Privacidad.',
    section1: {
      title: '1. Información recopilada y sus finalidades',
      intro: 'El Sitio recopila información del usuario para las siguientes finalidades:',
      cookieTitle: '1.1. Uso de Cookies',
      cookieDesc: 'El Sitio utiliza cookies para ofrecer una mejor experiencia de uso. Una cookie es una pequeña información almacenada en el navegador del usuario. Aunque se puede utilizar para identificar a un usuario determinado, no contiene información de identificación personal.',
      cookiePurposesTitle: 'Las cookies se utilizan para los siguientes fines:',
      cookiePurpose1: 'Análisis del uso del sitio web',
      cookiePurpose2: 'Mejora de la experiencia del usuario',
      cookieReject: 'Puede rechazar el uso de cookies mediante la configuración de su navegador; sin embargo, en ese caso, algunas funciones del Sitio podrían no funcionar correctamente.',
      analyticsTitle: '1.2. Uso de Google Analytics',
      analyticsDesc1: 'El Sitio utiliza Google Analytics para analizar el uso del sitio. Google Analytics utiliza cookies para registrar el comportamiento de los usuarios y realizar análisis de acceso. Esto permite recopilar información sobre qué páginas visitan los usuarios y cuánto tiempo permanecen, ayudando a mejorar el Sitio.',
      analyticsPolicy: 'Los datos recopilados por Google Analytics se rigen por la {link} de Google.',
      analyticsPolicyLink: 'Política de Privacidad',
      analyticsOptout: 'Los usuarios pueden inhabilitar la recopilación de datos de Google Analytics instalando el {link} proporcionado por Google.',
      analyticsOptoutLink: 'Complemento de inhabilitación para navegadores de Google Analytics',
      adsenseTitle: '1.3. Uso de Google AdSense',
      adsenseDesc1: 'El Sitio distribuye publicidad mediante Google AdSense. Google AdSense utiliza cookies para mostrar anuncios personalizados según los intereses de los usuarios, ofreciendo publicidad relevante y maximizando su eficacia.',
      adsensePolicy: 'Para obtener información sobre la recopilación y el uso de datos en Google AdSense, consulte las {link}.',
      adsensePolicyLink: 'Políticas de publicidad de Google',
      adsenseOptout: 'Los usuarios pueden administrar los anuncios personalizados en la {link}.',
      adsenseOptoutLink: 'página de Configuración de anuncios de Google'
    },
    section2: {
      title: '2. Gestión de la información personal',
      desc: 'El Sitio gestiona la información personal de los usuarios de forma adecuada y segura, adoptando las medidas necesarias para protegerla contra el acceso no autorizado, la pérdida, la alteración o la divulgación.'
    },
    section3: {
      title: '3. Cesión de información personal a terceros',
      desc: 'El Sitio no proporcionará información personal a terceros sin el consentimiento del usuario, salvo que la ley así lo exija.'
    },
    section4: {
      title: '4. Divulgación, rectificación y eliminación de información personal',
      desc: 'Cuando un usuario solicite la divulgación, rectificación o eliminación de su información personal, el Sitio responderá a la brevedad tras verificar su identidad.'
    },
    section5: {
      title: '5. Modificaciones de la Política de Privacidad',
      desc: 'El contenido de esta Política de Privacidad puede modificarse según cambios legislativos o directrices de funcionamiento del Sitio. La política modificada entrará en vigor desde el momento de su publicación en el Sitio.'
    },
    section6: {
      title: '6. Contacto',
      desc: 'Si tiene alguna consulta sobre esta Política de Privacidad, contáctenos mediante el siguiente formulario.',
      contactLink: 'Formulario de contacto'
    }
  },
  failed: 'Acción fallida',
  success: 'Acción realizada con éxito'
};
