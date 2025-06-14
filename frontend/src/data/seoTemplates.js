/**
 * SEO Templates for Local Producer Web Application
 * 
 * Pre-defined SEO templates for different page types
 * with Romanian language optimization.
 */

export const SEO_TEMPLATES = {
  // Homepage template
  home: {
    title: 'Pe Foc de Lemne - Produse Locale Românești de la Producători Verificați',
    description: 'Descoperă produse locale românești autentice: lactate, carne, legume, fructe proaspete. Comandă online de la producători verificați. Livrare rapidă în România.',
    keywords: [
      'produse locale',
      'producători români',
      'mâncare tradițională',
      'produse naturale',
      'fermieri locali',
      'alimente bio',
      'comandă online',
      'livrare acasă',
      'mâncare sănătoasă',
      'românesc'
    ],
    type: 'website'
  },

  // Products listing page template
  products: {
    title: 'Produse Locale Românești - Catalog Complet',
    description: 'Catalog complet cu produse locale românești: lactate, carne, legume, fructe, panificație și conserve. Produse naturale de la producători verificați.',
    keywords: [
      'catalog produse locale',
      'produse românești',
      'lactate naturale',
      'carne de țară',
      'legume proaspete',
      'fructe de sezon',
      'panificație tradițională',
      'conserve casnice'
    ],
    type: 'website'
  },

  // Product details page template
  product: (product, category) => ({
    title: `${product.name} - ${category?.name || 'Produs Local'} | Pe Foc de Lemne`,
    description: `${product.description?.substring(0, 150)}${product.description?.length > 150 ? '...' : ''} Comandă ${product.name} de la ${product.producer || 'producătorul local'}. Preț: ${product.price} RON. Livrare rapidă.`,
    keywords: [
      product.name,
      category?.name || '',
      'produs local',
      'românesc',
      'natural',
      'comandă online',
      product.producer || '',
      'livrare rapidă'
    ].filter(Boolean),
    type: 'product'
  }),

  // Category page template
  category: (category, productCount = 0) => ({
    title: `${category.name} - Produse Locale Românești | Pe Foc de Lemne`,
    description: `Descoperă ${productCount} produse din categoria ${category.name}. ${category.description || 'Produse locale românești de calitate superioară de la producători verificați.'} Comandă online cu livrare rapidă.`,
    keywords: [
      category.name,
      `produse ${category.name}`,
      `${category.name} locale`,
      `${category.name} românești`,
      'produse naturale',
      'producători verificați',
      'comandă online'
    ],
    type: 'website'
  }),

  // Cart page template
  cart: {
    title: 'Coșul de Cumpărături - Pe Foc de Lemne',
    description: 'Verifică produsele din coșul tău de cumpărături. Produse locale românești selectate cu grijă. Finalizează comanda pentru livrare rapidă.',
    keywords: [
      'coș cumpărături',
      'comandă produse locale',
      'finalizare comandă',
      'livrare produse românești'
    ],
    type: 'website',
    robots: 'noindex, follow'
  },

  // Checkout page template
  checkout: {
    title: 'Finalizare Comandă - Pe Foc de Lemne',
    description: 'Finalizează comanda de produse locale românești. Completează datele de livrare și plată pentru a primi produsele fresh la ușa ta.',
    keywords: [
      'finalizare comandă',
      'plată online',
      'livrare produse locale',
      'comandă produse românești'
    ],
    type: 'website',
    robots: 'noindex, nofollow'
  },

  // Order confirmation template
  orderConfirmation: {
    title: 'Comandă Confirmată - Pe Foc de Lemne',
    description: 'Comanda ta de produse locale românești a fost confirmată cu succes. Vei primi un SMS cu detaliile livrării.',
    keywords: [
      'comandă confirmată',
      'produse locale',
      'confirmare livrare'
    ],
    type: 'website',
    robots: 'noindex, nofollow'
  },

  // Search results template
  search: (query, resultCount = 0) => ({
    title: `Căutare: "${query}" - ${resultCount} rezultate | Pe Foc de Lemne`,
    description: `${resultCount} rezultate găsite pentru "${query}". Produse locale românești de la producători verificați. Descoperă și comandă online.`,
    keywords: [
      query,
      'căutare produse',
      'produse locale',
      'românești',
      'rezultate căutare'
    ],
    type: 'website',
    robots: 'noindex, follow'
  }),

  // Admin pages template
  admin: {
    title: 'Administrare - Pe Foc de Lemne',
    description: 'Panou de administrare pentru gestionarea produselor, comenzilor și clienților.',
    keywords: [
      'administrare',
      'panou admin',
      'gestionare produse'
    ],
    type: 'website',
    robots: 'noindex, nofollow'
  },

  // Error pages template
  error404: {
    title: 'Pagina nu a fost găsită - Pe Foc de Lemne',
    description: 'Pagina căutată nu există. Descoperă produsele noastre locale românești în catalogul complet.',
    keywords: [
      'eroare 404',
      'pagina nu există',
      'produse locale românești'
    ],
    type: 'website',
    robots: 'noindex, follow'
  },

  error500: {
    title: 'Eroare de server - Pe Foc de Lemne',
    description: 'Întâmpinăm probleme tehnice temporare. Te rugăm să încerci din nou în câteva minute.',
    keywords: [
      'eroare server',
      'probleme tehnice',
      'produse locale'
    ],
    type: 'website',
    robots: 'noindex, follow'
  }
};

// Category-specific SEO data
export const CATEGORY_SEO_DATA = {
  lactate: {
    keywords: [
      'lactate naturale',
      'lapte proaspăt',
      'brânză de țară',
      'smântână',
      'iaurt natural',
      'unt de casă',
      'telemea',
      'cașcaval'
    ],
    description: 'Lactate naturale și proaspete de la ferme locale românești. Lapte, brânză, smântână și iaurt fără conservanți, produse tradițional.'
  },
  
  carne: {
    keywords: [
      'carne proaspătă',
      'carne de vită',
      'carne de porc',
      'pui de țară',
      'carne bio',
      'mezeluri naturale',
      'cârnați de casă'
    ],
    description: 'Carne proaspătă și naturală de la fermele locale. Vită, porc și pui crescute în condiții naturale, fără hormoni și antibiotice.'
  },

  legume: {
    keywords: [
      'legume proaspete',
      'legume de sezon',
      'legume bio',
      'salate',
      'roșii',
      'castraveti',
      'ceapă',
      'cartofi'
    ],
    description: 'Legume proaspete de sezon de la grădinile locale. Cultivate natural, fără pesticide, cu gust autentic.'
  },

  fructe: {
    keywords: [
      'fructe proaspete',
      'fructe de sezon',
      'mere',
      'pere',
      'prune',
      'căpșuni',
      'zmeură',
      'cireșe'
    ],
    description: 'Fructe proaspete și dulci de la livezile locale românești. Fructe de sezon culese la maturitate perfectă.'
  },

  panificatie: {
    keywords: [
      'pâine de casă',
      'pâine tradițională',
      'cozonac',
      'prăjituri',
      'produse de panificație',
      'pâine neagră',
      'baghete'
    ],
    description: 'Produse de panificație artizanale făcute cu ingrediente naturale. Pâine, cozonac și prăjituri după rețete tradiționale.'
  },

  conserve: {
    keywords: [
      'conserve naturale',
      'murături',
      'gem de casă',
      'dulceață',
      'siropuri naturale',
      'compot',
      'conserve de legume'
    ],
    description: 'Conserve naturale și murături făcute în casă după rețete tradiționale românești. Fără conservanți artificiali.'
  },

  miere: {
    keywords: [
      'miere naturală',
      'miere de albine',
      'miere poliflora',
      'miere de salcâm',
      'miere de tei',
      'produse apicole',
      'propolis'
    ],
    description: 'Miere naturală și produse apicole de la stupinele locale. Miere pură, necumpărată, cu proprietăți nutritive excepționale.'
  },

  bauturi: {
    keywords: [
      'băuturi naturale',
      'sucuri naturale',
      'țuică',
      'pălincă',
      'vin de casă',
      'kombucha',
      'băuturi tradiționale'
    ],
    description: 'Băuturi naturale și tradiționale românești. Sucuri proaspete, țuică și pălincă artizanale, vin de casă.'
  }
};

// Common Romanian food terms and keywords
export const ROMANIAN_FOOD_KEYWORDS = [
  'mâncare românească',
  'produse tradiționale',
  'rețete bătrânești',
  'gustul copilăriei',
  'făcut în casă',
  'ca la mama acasă',
  'produse de țară',
  'alimente sănătoase',
  'hrană naturală',
  'fără conservanți',
  'bio și natural',
  'crescut local',
  'produs în România'
];

// Local SEO keywords for Romanian regions
export const ROMANIAN_REGIONS_KEYWORDS = [
  'București',
  'Cluj-Napoca',
  'Timișoara',
  'Iași',
  'Constanța',
  'Craiova',
  'Brașov',
  'Galați',
  'Ploiești',
  'Oradea',
  'Arad',
  'Pitești',
  'Sibiu',
  'Bacău',
  'Târgu Mureș',
  'Baia Mare',
  'Buzău',
  'Botoșani',
  'Satu Mare',
  'Râmnicu Vâlcea'
];

export default SEO_TEMPLATES;