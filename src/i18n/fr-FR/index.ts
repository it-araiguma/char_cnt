export default {
  app: {
    title: 'Compteur de texte',
    input: {
      placeholder: 'Entrez votre texte ici...',
      clear: 'Effacer'
    },
    counter: {
      characters: 'Caractères',
      noSpaces: 'Sans espaces et retours à la ligne'
    },
    tools: {
      title: 'Compteurs spécialisés',
      genkoTitle: 'Convertisseur Genko Yoshi (papier manuscrit)',
      genkoDesc: 'Calculez le nombre de feuilles 400 et 200 caractères avec prise en compte des retours.',
      reportTitle: 'Vérificateur de rapport et dissertation',
      reportDesc: 'Suivez votre progression par rapport à un objectif (±10%, 80%-100%, limite max).'
    }
  },
  layout: {
    header: {
      title: 'Compteur de caractères'
    },
    footer: {
      home: 'Accueil',
      genko: 'Convertisseur Genko Yoshi',
      report: 'Vérificateur de rapport',
      privacy: 'Politique de confidentialité',
      copyright: 'Copyright ',
      allRights: 'Tous droits réservés.'
    }
  },
  seo: {
    index: {
      title: 'Compteur de caractères - Comptez les caractères en ligne',
      description: 'Un outil en ligne simple pour compter les caractères de votre texte. Affiche également le nombre de caractères sans espaces ni retours à la ligne.',
      keywords: 'compteur de caractères,compteur de texte,outil en ligne'
    },
    genko: {
      title: 'Convertisseur Genko Yoshi (papier manuscrit 400/200) - Compteur de caractères',
      description: 'Calcule automatiquement le nombre de pages et de lignes de papier manuscrit japonais (Genko Yoshi 400 et 200 caractères) avec prise en compte des retours à la ligne.',
      keywords: 'genko yoshi,papier manuscrit,compteur de caractères japonais,nombre de pages'
    },
    report: {
      title: 'Vérificateur de longueur de rapport et dissertation - Compteur de caractères',
      description: 'Vérifiez en temps réel votre progression et le respect de l\'objectif de caractères (±10%, 80%-100%, limite max).',
      keywords: 'compteur rapport,longueur dissertation,objectif caractères'
    },
    privacy: {
      title: 'Politique de confidentialité - Compteur de caractères',
      description: 'Politique de confidentialité de l\'application Compteur de caractères.',
      keywords: 'politique de confidentialité,compteur de caractères,protection des données'
    }
  },
  genko: {
    title: 'Convertisseur Papier Manuscrit (Genko Yoshi)',
    subtitle: 'Calcul en temps réel du nombre de feuilles et de lignes pour 400 et 200 caractères',
    input: {
      placeholder: 'Saisissez ou collez votre texte ici...',
      clear: 'Effacer',
      copy: 'Copier',
      copied: 'Copié dans le presse-papiers',
      sample: 'Insérer un exemple'
    },
    summary: {
      totalChars: 'Total caractères',
      noSpaces: 'Sans espaces ni retours',
      totalLines: 'Total lignes (Genko Yoshi)',
      rawLines: 'Paragraphes'
    },
    cards: {
      actualTitle: 'Calcul réel (retours à la ligne inclus)',
      actualDesc: 'Sur la base de 20 caractères par ligne, reflétant fidèlement les blancs et paragraphes.',
      charTitle: 'Calcul par division de caractères (estimation)',
      charDesc: 'Division pure du nombre total de caractères par la taille de la grille (400 ou 200).',
      sheetsUnit: ' feuilles',
      exactBadge: 'Sans reste',
      remainderFormat: '{full} feuilles et {remainder} {unit}',
      linesUnit: 'lignes',
      charsUnit: 'caractères',
      preset400: 'Genko Yoshi 400 caractères (20 car. x 20 lignes)',
      preset200: 'Genko Yoshi 200 caractères (20 car. x 10 lignes)',
      customPreset: 'Grille personnalisée'
    },
    custom: {
      title: 'Personnaliser la grille',
      charsPerLine: 'Caractères par ligne',
      linesPerPage: 'Lignes par feuille',
      reset: 'Réinitialiser',
      invalidRange: 'Veuillez saisir un entier entre {min} et {max}'
    },
    guide: {
      title: 'Guide d\'écriture et règles du Genko Yoshi',
      subtitle: 'Règles fondamentales pour les rédactions et compositions japonaises',
      rule1Title: '1. Titre, nom et alinéa',
      rule1Body: '・Titre : Première ligne en laissant 2 ou 3 cases vides au début.\n・Nom : Deuxième ligne en laissant 1 ou 2 cases vides à la fin.\n・Alinéa : Débuter chaque paragraphe par une indentation d\'une case.',
      rule2Title: '2. Ponctuation et interdits de début de ligne',
      rule2Body: '・Les points et virgules ne doivent jamais être placés au début d\'une ligne.\n・Placez-les dans la dernière case avec le caractère ou suspendez-les dans la marge extérieure.',
      rule3Title: '3. Dialogues et guillemets',
      rule3Body: '・Les dialogues commencent sur une nouvelle ligne avec le guillemet ouvrant sans indentation.',
      rule4Title: '4. Chiffres et alphabet',
      rule4Body: '・En écriture verticale, privilégiez les chiffres en kanji.\n・Les chiffres arabes s\'écrivent généralement par deux dans une case.',
      tableTitle: 'Tableau d\'équivalence caractères / feuilles de 400 caractères',
      tableHeaderChars: 'Caractères',
      tableHeaderSheets: 'Feuilles (400 car.)',
      tableHeaderPurpose: 'Usage type',
      tableRow1: '400 car. (1 feuille) : Courte rédaction',
      tableRow2: '800 car. (2 feuilles) : Rédaction de lycée',
      tableRow3: '1 200 car. (3 feuilles) : Concours / Fiche de lecture',
      tableRow4: '2 000 car. (5 feuilles) : Rapport universitaire',
      tableRow5: '4 000 car. (10 feuilles) : Nouvelle courte',
      tableRow6: '8 000 car. (20 feuilles) : Roman court / Chapitre'
    }
  },
  report: {
    title: 'Vérificateur de rapport et dissertation',
    subtitle: 'Progression en temps réel et contrôle de conformité (±10%, 80%-100%, limite max)',
    units: {
      chars: 'car.'
    },
    target: {
      title: 'Objectif et critères',
      presetFormat: '{count} car.',
      customLabel: 'Objectif personnalisé',
      excludeSpaces: 'Exclure espaces et retours'
    },
    rule: {
      title: 'Règle de validation',
      around10: '±10% (Environ)',
      min80: '80%–100% (Min 80%)',
      max100: 'Max 100% (Limite)'
    },
    status: {
      ok: 'OK',
      short: 'Insuffisant',
      over: 'Dépassé',
      empty: 'Vide',
      rangeFormat: 'Plage autorisée : {min} - {max} car.',
      okMessage: 'Votre texte respecte la plage autorisée.',
      shortMessage: 'Il manque {diff} caractères pour atteindre le minimum.',
      overMessage: 'Vous dépassez la limite de {diff} caractères.',
      emptyMessage: 'Saisissez votre texte pour vérifier l\'objectif.'
    },
    input: {
      placeholder: 'Saisissez ou collez votre rapport ou dissertation ici...',
      clear: 'Effacer',
      copy: 'Copier',
      copied: 'Copié dans le presse-papiers',
      sample: 'Insérer un exemple'
    },
    summary: {
      totalChars: 'Total caractères',
      noSpaces: 'Sans espaces ni retours',
      paragraphs: 'Paragraphes',
      genkoSheets: 'Feuilles 400 car. (est.)'
    },
    guide: {
      title: 'Guide de comptage pour rapports et dissertations',
      subtitle: 'Éléments inclus dans le décompte et interprétation des consignes',
      criteriaTitle: 'Que faut-il inclure dans le décompte ?',
      criteriaHeaderItem: 'Élément',
      criteriaHeaderInclude: 'Inclus ?',
      criteriaHeaderNote: 'Règle générale',
      criteriaInclude: 'Généralement inclus',
      criteriaExclude: 'Généralement exclu',
      criteriaConditional: 'À vérifier',
      criteriaRow1Item: 'Titre, nom et numéro étudiant',
      criteriaRow1Note: 'Les limites s\'appliquent généralement au corps du texte uniquement.',
      criteriaRow2Item: 'Titres de sections',
      criteriaRow2Note: 'Les titres font partie de la structure du texte et sont comptés.',
      criteriaRow3Item: 'Bibliographie et références',
      criteriaRow3Note: 'Souvent exclue, sauf indication contraire dans la consigne.',
      criteriaRow4Item: 'Figures, légendes et notes',
      criteriaRow4Note: 'Le texte dans les figures est exclu ; vérifiez pour les légendes.',
      criteriaRow5Item: 'Espaces et retours à la ligne',
      criteriaRow5Note: 'Certains éditeurs excluent les espaces, mais les formulaires web les comptent.',
      rule1Title: '1. Interpréter les consignes de longueur',
      rule1Body: '・「Environ X car.」 : Visez ±10% autour de la cible.\n・「Au moins X car.」 : Dépassez la cible sans excès (+10% à +20%).\n・「Maximum X car.」 : Ne dépassez jamais la limite et visez au moins 80%.',
      rule2Title: '2. Différence entre éditeur et formulaire web',
      rule2Body: '・Utilisez le bouton ci-dessus pour basculer entre le comptage avec ou sans espaces.',
      tableTitle: 'Repères courants de longueur',
      tableHeaderChars: 'Objectif',
      tableHeaderVolume: 'Volume estimé',
      tableHeaderPurpose: 'Usage courant',
      tableRow1Chars: '800 car.',
      tableRow1Volume: '~0,7 page A4',
      tableRow1Purpose: 'Note de lecture, essai court',
      tableRow2Chars: '1 200 car.',
      tableRow2Volume: '~1 page A4',
      tableRow2Purpose: 'Dissertation d\'examen, court rapport',
      tableRow3Chars: '2 000 car.',
      tableRow3Volume: '~1,5–2 pages A4',
      tableRow3Purpose: 'Rapport universitaire',
      tableRow4Chars: '4 000 car.',
      tableRow4Volume: '~3–3,5 pages A4',
      tableRow4Purpose: 'Mémoire court, rapport de recherche'
    }
  },
  privacyPolicy: {
    title: 'Politique de confidentialité',
    intro: 'Ce site (ci-après dénommé « le Site ») s\'engage à protéger les informations personnelles des utilisateurs et a établi la présente politique de confidentialité. En utilisant ce Site, vous acceptez la présente politique de confidentialité.',
    section1: {
      title: '1. Informations collectées et finalités',
      intro: 'Le Site collecte des informations sur les utilisateurs pour les finalités suivantes :',
      cookieTitle: '1.1. Utilisation des cookies',
      cookieDesc: 'Le Site utilise des cookies pour offrir une meilleure expérience utilisateur. Un cookie est une information enregistrée dans votre navigateur. Bien qu\'il puisse être utilisé pour identifier un utilisateur spécifique, il ne contient aucune information personnellement identifiable.',
      cookiePurposesTitle: 'Les cookies sont utilisés aux fins suivantes :',
      cookiePurpose1: 'Analyse de l\'utilisation du site',
      cookiePurpose2: 'Amélioration de l\'expérience utilisateur',
      cookieReject: 'Vous pouvez refuser l\'utilisation des cookies via les paramètres de votre navigateur ; toutefois, certaines fonctionnalités du Site peuvent ne pas fonctionner correctement.',
      analyticsTitle: '1.2. Utilisation de Google Analytics',
      analyticsDesc1: 'Le Site utilise Google Analytics pour analyser l\'utilisation du site. Google Analytics utilise des cookies pour enregistrer le comportement des utilisateurs et effectuer des analyses de trafic. Cela permet de collecter des informations telles que les pages visitées et la durée des visites afin d\'améliorer le Site.',
      analyticsPolicy: 'Les données collectées par Google Analytics sont soumises aux {link} de Google.',
      analyticsPolicyLink: 'Règles de confidentialité',
      analyticsOptout: 'Les utilisateurs peuvent désactiver la collecte de données par Google Analytics en installant le {link} fourni par Google.',
      analyticsOptoutLink: 'Module complémentaire de désactivation de Google Analytics',
      adsenseTitle: '1.3. Utilisation de Google AdSense',
      adsenseDesc1: 'Le Site diffuse des annonces via Google AdSense. Google AdSense utilise des cookies pour afficher des annonces personnalisées en fonction des centres d\'intérêt des utilisateurs, offrant des annonces pertinentes et optimisant leur efficacité.',
      adsensePolicy: 'Pour plus d\'informations sur la collecte et l\'utilisation des données liées à Google AdSense, veuillez consulter les {link}.',
      adsensePolicyLink: 'Règles relatives aux annonces Google',
      adsenseOptout: 'Les utilisateurs peuvent gérer l\'affichage des annonces personnalisées sur la {link}.',
      adsenseOptoutLink: 'page Paramètres des annonces Google'
    },
    section2: {
      title: '2. Gestion des informations personnelles',
      desc: 'Le Site gère les informations personnelles des utilisateurs de manière appropriée et sécurisée, en prenant les mesures nécessaires pour les protéger contre tout accès non autorisé, perte, altération ou divulgation.'
    },
    section3: {
      title: '3. Transmission d\'informations personnelles à des tiers',
      desc: 'Le Site ne transmet aucune information personnelle à des tiers sans le consentement de l\'utilisateur, sauf obligation légale.'
    },
    section4: {
      title: '4. Divulgation, correction et suppression des informations personnelles',
      desc: 'En cas de demande d\'un utilisateur concernant la divulgation, la correction ou la suppression de ses informations personnelles, le Site y répondra rapidement après vérification de son identité.'
    },
    section5: {
      title: '5. Modifications de la politique de confidentialité',
      desc: 'Le contenu de cette politique de confidentialité peut être modifié en fonction des évolutions légales ou des orientations de gestion du Site. La politique modifiée prend effet dès sa publication sur le Site.'
    },
    section6: {
      title: '6. Nous contacter',
      desc: 'Pour toute question concernant cette politique de confidentialité, veuillez nous contacter via le formulaire ci-dessous.',
      contactLink: 'Formulaire de contact'
    }
  },
  failed: 'Échec de l\'action',
  success: 'Action réussie'
};
