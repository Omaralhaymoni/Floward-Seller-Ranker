# 🌸 Floward Seller Ranker

A **Streamlit-based dashboard** that lets you upload your own sales data and instantly rank best-selling products by **Sales**, **Cost**, **Price**, or **Margin**.

---

## 🚀 Features

- 📂 Upload **CSV or Excel** files directly in the app  
- 🧭 Filter data by:
  - Date range  
  - Product type  
  - Brand name  
  - Hierarchical levels (`mc0` – `mc4`)
- 📊 Rank results by:
  - Sales  
  - Cost  
  - Price  
  - Margin (average)
- 📈 Interactive bar charts and data tables  
- 💾 Download top N results as CSV  
- 🎨 Custom dark theme and modern Streamlit UI

---

## 🧰 Tech Stack

| Layer | Technology |
|:------|:------------|
| UI | Streamlit |
| Data | Pandas, NumPy |
| Runtime | Python 3 |
| Visualization | Streamlit native charts |
| Styling | Custom CSS |


---

## 📊 Dataset Description

Your uploaded dataset should contain the following columns:

| Column | Type | Description |
|:--------|:------|:-------------|
| `date` | datetime | Transaction date |
| `product_type_description` | string | Product category/type |
| `brand_name` | string | Brand name |
| `mc0`–`mc4` | string | Hierarchical marketing levels |
| `product_sales` | float | Total sales amount |
| `product_cost` | float | Product cost |
| `product_price` | float | Selling price |
| `margin` | float | Profit margin per unit or order |

> ⚠️ **Note:** Missing columns are allowed — the app will show a warning but still run.

### Example CSV

```csv
date,product_type_description,brand_name,mc0,mc1,margin,product_price,product_cost,product_sales
2024-03-01,Perfume,BrandA,Beauty,Fragrance,0.35,120,78,24000
2024-03-02,Perfume,BrandB,Beauty,Fragrance,0.28,95,68,15000


## 📁 Project Structure

