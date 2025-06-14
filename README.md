# Pe Foc de Lemne - Marketplace pentru Produse Locale Românești

> **Connecting Romanian Local Producers with Customers Through Digital Innovation**

Pe Foc de Lemne este o platformă digitală dedicată producătorilor locali români, oferind o soluție completă pentru comercializarea produselor tradiționale și artizanale direct către consumatori.

## 🌟 Caracteristici Principale

### Pentru Clienți
- **Produse Locale Autentice**: Acces direct la produse proaspete de la producători verificați
- **Experiență Mobilă Optimizată**: Interfață responsivă adaptată pentru toate dispozitivele
- **Verificare SMS Securizată**: Sistem de autentificare prin SMS pentru comenzi sigure
- **Căutare Inteligentă**: Filtrare avansată după categorie, producător și criterii de calitate

### Pentru Producători
- **Gestionare Completă Produse**: Adăugare, editare și gestionarea stocurilor
- **Urmărire Comenzi**: Monitorizare în timp real a comenzilor și statusurilor
- **Analiză Performanță**: Statistici detaliate despre vânzări și clienți
- **Profil Producător**: Prezentare detaliată a fermei și metodelor de producție

### Pentru Administratori
- **Panou de Control**: Dashboard complet pentru gestionarea platformei
- **Gestionare Utilizatori**: Administrarea producătorilor și clienților
- **Analiză Business**: Metrici și rapoarte pentru optimizarea platformei
- **Securitate Avansată**: Sistem complet de monitorizare și protecție

## 🏗️ Arhitectura Tehnică

### Frontend (React)
- **React 18** cu TypeScript pentru type safety
- **Tailwind CSS** pentru design responsive
- **React Router** pentru navigare SPA
- **Context API** pentru state management
- **Cypress** pentru testing end-to-end

### Backend (Flask)
- **Flask** cu Python pentru API REST
- **MongoDB** pentru stocare de date
- **Twilio** pentru verificare SMS
- **JWT** pentru autentificare securizată
- **Pytest** pentru testing unitar și de integrare

### Securitate & Performanță
- **HTTPS/SSL** enforced în producție
- **Rate limiting** și protecție anti-spam
- **Input validation** și sanitizare
- **GDPR compliance** pentru protecția datelor
- **Analytics** cu Google Analytics 4

## 🚀 Instalare și Configurare

### Prerequisite
- **Node.js** (versiunea 16 sau mai nouă)
- **Python** (versiunea 3.8 sau mai nouă)
- **MongoDB** (versiunea 4.4 sau mai nouă)
- **Git** pentru version control

### 1. Clonare Repository
```bash
git clone [repository-url]
cd pe-foc-de-lemne
```

### 2. Configurare Backend
```bash
cd backend

# Instalare dependențe Python
pip install -r requirements.txt

# Configurare variabile de mediu
cp .env.example .env
# Editați .env cu valorile corecte

# Pornire server dezvoltare
python app.py
```

### 3. Configurare Frontend
```bash
cd frontend

# Instalare dependențe Node.js
npm install

# Configurare variabile de mediu
cp .env.example .env.local
# Editați .env.local cu valorile corecte

# Pornire aplicație dezvoltare
npm start
```

### 4. Configurare Bază de Date
```bash
# Pornire MongoDB (local)
mongod

# Creare index-uri (opțional)
python -c "from backend.app.database import create_indexes; create_indexes()"
```

## 📁 Structura Proiectului

```
pe-foc-de-lemne/
├── backend/                    # API Flask
│   ├── app/
│   │   ├── models/            # Modele date MongoDB
│   │   ├── routes/            # Endpoint-uri API
│   │   ├── services/          # Logică business
│   │   ├── utils/             # Utilități și helpers
│   │   └── middleware/        # Middleware pentru securitate
│   ├── tests/                 # Teste backend
│   └── requirements.txt       # Dependențe Python
├── frontend/                  # Aplicație React
│   ├── src/
│   │   ├── components/        # Componente React
│   │   ├── pages/             # Pagini aplicației
│   │   ├── contexts/          # Context providers
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # Servicii API
│   │   └── utils/             # Utilități frontend
│   ├── public/                # Fișiere statice
│   └── package.json           # Dependențe Node.js
├── docs/                      # Documentație
│   ├── api/                   # Documentație API
│   ├── deployment/            # Ghiduri deployment
│   ├── users/                 # Ghiduri utilizatori
│   └── operations/            # Documentație operațională
└── README.md                  # Acest fișier
```

## 🌐 Variabile de Mediu

### Backend (.env)
```bash
# Configurare aplicație
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Configurare MongoDB
MONGODB_URI=mongodb://localhost:27017/pe_foc_de_lemne

# Configurare Twilio SMS
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# Configurare JWT
JWT_SECRET_KEY=your-jwt-secret

# Configurare securitate
ENCRYPTION_MASTER_KEY=your-encryption-key
```

### Frontend (.env.local)
```bash
# URL-uri API
REACT_APP_API_URL=http://localhost:8080/api

# Google Analytics
REACT_APP_GA4_MEASUREMENT_ID=your-ga4-id

# Configurare dezvoltare
REACT_APP_ENV=development
```

## 🧪 Rulare Teste

### Teste Backend
```bash
cd backend

# Teste unitare
pytest tests/ -v

# Teste cu coverage
pytest tests/ --cov=app --cov-report=html

# Teste de performanță
python tests/performance/load_test.py
```

### Teste Frontend
```bash
cd frontend

# Teste unitare
npm test

# Teste E2E cu Cypress
npm run cypress:run

# Teste performanță cu Lighthouse
npm run lighthouse
```

## 📊 Monitoring și Analytics

### Google Analytics 4
- **Enhanced E-commerce**: Tracking complet pentru comenzi
- **Custom Events**: Evenimente business specifice României
- **Conversion Tracking**: Măsurarea conversiilor și ROI

### Monitoring Sistem
- **Health Checks**: Verificări automate ale sănătății sistemului
- **Error Tracking**: Monitorizarea erorilor în timp real
- **Performance Metrics**: Metrici de performanță și disponibilitate

## 🔒 Securitate și Conformitate

### Măsuri de Securitate
- **HTTPS Enforced**: Toate comunicațiile sunt criptate
- **Input Validation**: Validare completă a datelor de intrare
- **Rate Limiting**: Protecție împotriva atacurilor automatizate
- **JWT Authentication**: Autentificare securizată cu token-uri

### Conformitate GDPR
- **Consimțământ Cookie**: Gestionarea consimțământului pentru cookie-uri
- **Dreptul la Uitare**: Ștergerea datelor la cererea utilizatorului
- **Portabilitatea Datelor**: Export de date în format standard
- **Privacy by Design**: Protecția datelor încorporată în design

## 🌍 Localizare Românească

### Adaptări Culturale
- **Limba Română**: Interfață completă în română
- **Moneda RON**: Toate prețurile în lei români
- **Adrese Românești**: Validare pentru adrese și coduri poștale
- **Telefoane Românești**: Suport pentru formatele +40, 0040, 0

### Context Business Local
- **Categorii Tradiționale**: Produse specifice culturii românești
- **Producători Locali**: Focus pe fermieri și artizani români
- **Livrare Regională**: Opțiuni adaptate pentru România
- **Support în Română**: Echipă de suport în limba română

## 📚 Documentație Detaliată

- **[Ghid Deployment](docs/deployment/production-setup.md)** - Configurare producție
- **[API Reference](docs/api/api-reference.md)** - Documentație completă API
- **[Ghid Utilizatori](docs/users/)** - Ghiduri pentru clienți și administratori
- **[Arhitectura Sistemului](docs/architecture/system-overview.md)** - Detalii tehnice

## 🤝 Contribuții

### Pentru Dezvoltatori
1. Fork repository-ul
2. Creați o ramură pentru feature (`git checkout -b feature/amazing-feature`)
3. Commit modificările (`git commit -m 'Add amazing feature'`)
4. Push la ramură (`git push origin feature/amazing-feature`)
5. Deschideți un Pull Request

### Coding Standards
- **Python**: PEP 8 compliance
- **JavaScript**: ESLint + Prettier
- **Testing**: Coverage minimum 80%
- **Documentation**: Documentație pentru toate funcțiile publice

## 📞 Support și Contact

### Echipa Tehnică
- **Email**: tech@pefocdelemne.ro
- **GitHub Issues**: Pentru bug reports și feature requests
- **Documentation**: [docs.pefocdelemne.ro](docs.pefocdelemne.ro)

### Business Inquiries
- **Email**: contact@pefocdelemne.ro
- **Telefon**: +40 XXX XXX XXX
- **Adresă**: [Adresa companiei]

## 📄 Licență

Acest proiect este licențiat sub [MIT License](LICENSE).

---

**Pe Foc de Lemne** - Susținând economia locală românească prin tehnologie modernă.

*Dezvoltat cu ❤️ pentru producătorii și consumatorii români.*