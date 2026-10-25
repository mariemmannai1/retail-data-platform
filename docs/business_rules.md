# Règles métier — Retail Data Platform 2026

## 1. Périmètre des ventes
- Une vente compte uniquement si `order_status = 'Completed'`.
- Commandes Refunded (225, soit 2,25 %) : exclues des ventes, suivies à part. Montant concerné : 6 031,18.
- Commandes Cancelled (186, soit 1,86 %) : exclues. Leur `total_amount` vaut 0,00.

## 2. Devise
- Les montants sont en GBP (£), d'après data_dictionary.csv (12 colonnes décrites « Currency value in GBP »).
- Le jeu de données est fictif.

## 3. Indicateurs officiels
| Indicateur | Définition | Valeur 2025 |
|---|---|---|
| Net Sales | SUM(line_net_amount), Completed, hors TVA | 228 457,01 |
| Revenue TTC | SUM(total_amount), Completed, TVA et livraison incluses | 249 520,30 |
| Orders | Nombre de commandes Completed (order_id distincts) | 9 589 |
| Quantity | SUM(quantity), Completed | 90 585 |
| Average Order Value | Revenue TTC / Orders | 26,02 |

## 4. Règles d'usage
- Le dashboard affiche Net Sales par défaut ; il permet les filtres magasin et catégorie.
- daily_sales et la prévision utilisent Revenue TTC (niveau commande).
- Ne jamais additionner `order_total_amount` sur fact_sales : il est répété sur chaque ligne.
- Les commandes anonymes (customer_id vide : 2 768) sont conservées.

## 5. Stock
- Alerte si `stock_on_hand < reorder_level` (92 couples magasin-produit aujourd'hui).