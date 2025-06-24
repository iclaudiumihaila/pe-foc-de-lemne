# Test Data Used During Testing Session

## User Accounts

### Admin User
- **Phone**: +40700000000
- **Password**: admin123
- **Role**: Admin
- **Created By**: seed_data.py

### Test User (Registration)
- **First Name**: Claudiu
- **Last Name**: Test
- **Phone**: 0775156791
- **Email**: claudiu.test@example.com
- **Password**: Test123!
- **Role**: Customer

### Test Customer (Checkout)
- **First Name**: Ion
- **Last Name**: Popescu
- **Phone**: 0712345678
- **Email**: ion.popescu@example.com
- **Address**: Strada Mihai Eminescu Nr 23, Bloc A2, Scara 1, Ap 5
- **City**: București
- **County**: București
- **Postal Code**: 010123
- **Notes**: Vă rog sunați înainte de livrare

---

## Categories (5 total)

1. **Lactate**
   - Description: Produse lactate proaspete de la ferma
   - Display Order: 1
   - Product Count: 3

2. **Carne și Mezeluri**
   - Description: Carne proaspătă și mezeluri tradiționale
   - Display Order: 2
   - Product Count: 2

3. **Legume și Fructe**
   - Description: Legume și fructe de sezon
   - Display Order: 3
   - Product Count: 2

4. **Produse de Panificație**
   - Description: Pâine și produse de patiserie artizanale
   - Display Order: 4
   - Product Count: 2

5. **Conserve și Dulcețuri**
   - Description: Conserve și dulcețuri făcute în casă
   - Display Order: 5
   - Product Count: 2

---

## Products (11 total)

### Lactate Category
1. **Brânză de vacă proaspătă**
   - Price: 25.50 RON
   - Stock: 50
   - Image: https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d

2. **Lapte proaspăt de fermă**
   - Price: 8.00 RON
   - Stock: 100
   - Image: https://images.unsplash.com/photo-1563636619-e9143da7973b

3. **Smântână 30% grăsime**
   - Price: 12.00 RON
   - Stock: 40
   - Image: https://images.unsplash.com/photo-1628088062854-d1870b4553da

### Carne și Mezeluri Category
4. **Cârnați de casă afumați**
   - Price: 45.00 RON
   - Stock: 30
   - Image: https://images.unsplash.com/photo-1601924582970-9238bcb495d9

5. **Slănină afumată**
   - Price: 35.00 RON
   - Stock: 25
   - Image: https://images.unsplash.com/photo-1607623814075-e51df1bdc82f

### Legume și Fructe Category
6. **Roșii de grădină**
   - Price: 8.50 RON
   - Stock: 80
   - Image: https://images.unsplash.com/photo-1592924357228-91a4daadcfea

7. **Mere ionatan**
   - Price: 5.00 RON
   - Stock: 120
   - Image: https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6

### Produse de Panificație Category
8. **Pâine de casă cu maia**
   - Price: 12.00 RON
   - Stock: 20
   - Image: https://images.unsplash.com/photo-1549931319-a545dcf3bc73

9. **Cozonac cu nucă**
   - Price: 35.00 RON
   - Stock: 15
   - Image: https://images.unsplash.com/photo-1509440159596-0249088772ff

### Conserve și Dulcețuri Category
10. **Dulceață de caise**
    - Price: 18.00 RON
    - Stock: 35
    - Image: https://images.unsplash.com/photo-1562967914-608f82629710

11. **Zacuscă de vinete**
    - Price: 22.00 RON
    - Stock: 40
    - Image: https://images.unsplash.com/photo-1601001435957-74f0958a93c8

---

## Cart Test Data

### Items Added
1. **Brânză de țară** (might be same as Brânză de vacă)
   - Price: 15.00 RON
   - Quantity: 1

2. **Mere ionatan**
   - Price: 4.50 RON
   - Quantity: 1

### Cart Summary
- Subtotal: 19.50 RON
- TVA (19%): 3.71 RON
- Total: 23.21 RON
- Delivery: Free (local)

---

## API Test Endpoints

1. **Categories**: GET http://localhost:8000/api/categories/
2. **Products**: GET http://localhost:8000/api/products/?available_only=true&sort_by=name&sort_order=asc
3. **Login**: POST http://localhost:8000/api/auth/login
4. **Logout**: POST http://localhost:8000/api/auth/logout

---

## Browser Test Environment

- **User Agent**: MCP Browser Automation
- **Viewport**: Desktop (responsive testing pending)
- **Network**: 4G with poor quality
- **Console Logging**: Enabled for debugging

---

## Database State After Testing

- **Users**: 2 (admin + test user)
- **Categories**: 5 (all active)
- **Products**: 11 (all available with proper images)
- **Orders**: 0 (checkout tested but not completed)
- **Cart Sessions**: Active session with 2 items