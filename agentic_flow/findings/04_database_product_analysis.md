# Database Product Analysis

Generated on: 2025-06-23T20:29:30.836040

## Summary

- **Total products**: 19
- **Unique fields found**: 9
- **Missing required fields**: 8
- **Type mismatches**: 0
- **Unexpected fields**: 1

## All Fields Found

| Field Name | Occurrences | Percentage |
|------------|-------------|------------|
| _id | 19 | 100.0% |
| active | 19 | 100.0% |
| category | 1 | 5.3% |
| createdAt | 19 | 100.0% |
| description | 19 | 100.0% |
| image | 19 | 100.0% |
| name | 19 | 100.0% |
| price | 19 | 100.0% |
| stock | 19 | 100.0% |

## Field Type Analysis

### _id
- ObjectId: 19 occurrences

### active
- bool: 19 occurrences

### category
- ObjectId: 1 occurrences

### createdAt
- datetime: 19 occurrences

### description
- string: 19 occurrences

### image
- string: 19 occurrences

### name
- string: 19 occurrences

### price
- float: 19 occurrences

### stock
- int: 19 occurrences

## Missing Required Fields

### slug
- expected_type: string
- status: completely missing

### category_id
- expected_type: ObjectId
- status: completely missing

### subcategory_id
- expected_type: ObjectId
- status: completely missing

### unit
- expected_type: string
- status: completely missing

### images
- expected_type: array
- status: completely missing

### updatedAt
- expected_type: datetime
- status: completely missing

### views
- expected_type: int
- status: completely missing

### sales
- expected_type: int
- status: completely missing

## Type Mismatches

No type mismatches found.

## Unexpected Fields

### category
- Occurrences: 1
- Types found:
  - ObjectId: 1

## Sample Products

### Product 1
```json
{
  "_id": "68598cc47dfd4e73a4b74c72",
  "name": "Br\u00e2nz\u0103 de vac\u0103 proasp\u0103t\u0103",
  "description": "Br\u00e2nz\u0103 de vac\u0103 tradi\u021bional\u0103, f\u0103cut\u0103 din lapte proasp\u0103t de la ferma local\u0103. Textur\u0103 cremoas\u0103 \u0219i gust delicat.",
  "price": 25.99,
  "active": true,
  "stock": 0,
  "image": "",
  "createdAt": "2025-06-23T17:20:04.714000"
}
```

### Product 2
```json
{
  "_id": "68598cc47dfd4e73a4b74c73",
  "name": "Telemea de oaie",
  "description": "Telemea tradi\u021bional\u0103 rom\u00e2neasc\u0103 din lapte de oaie, maturat\u0103 \u00een saramur\u0103. Gustul autentic al mun\u021bilor.",
  "price": 32.5,
  "active": true,
  "stock": 0,
  "image": "",
  "createdAt": "2025-06-23T17:20:04.744000"
}
```

### Product 3
```json
{
  "_id": "68598cc47dfd4e73a4b74c74",
  "name": "Lapte proasp\u0103t de ferm\u0103",
  "description": "Lapte integral, proasp\u0103t muls, de la vaci hr\u0103nite natural. Bogat \u00een nutrien\u021bi \u0219i vitamine.",
  "price": 8.0,
  "active": true,
  "stock": 0,
  "image": "",
  "createdAt": "2025-06-23T17:20:04.748000"
}
```

## Recommendations

Add missing required fields to all products
  - Add 'slug' field to all products
  - Add 'category_id' field to all products
  - Add 'subcategory_id' field to all products
  - Add 'unit' field to all products
  - Add 'images' field to all products
  - Add 'updatedAt' field to all products
  - Add 'views' field to all products
  - Add 'sales' field to all products
Review unexpected fields:
  - 'category' found in 1 products

## Expected Product Schema

Based on the Product model, the expected fields are:

| Field | Type | Description |
|-------|------|-------------|
| _id | ObjectId | |
| name | string | |
| slug | string | |
| description | string | |
| price | float | |
| category_id | ObjectId | |
| subcategory_id | ObjectId | |
| stock | int | |
| unit | string | |
| images | array | |
| active | bool | |
| image | string | |
| createdAt | datetime | |
| updatedAt | datetime | |
| views | int | |
| sales | int | |
