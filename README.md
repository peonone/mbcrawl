A mother&baby E-commerce crawler powered by scrapy.
features:
 - crawl mother&baby products from global.beibei.com (And may add support for some other sites)
 - store the product meta info(such as id, name, description, skus) to PostgreSQL
 - store the product image to upyun cloud storage

### global.beibei.com
#### Product
Product is kept in table `products_beibei` which has following columns
name | type | description |
---- | ---- | ---- |
id |  int | |
name  |  string | |
description | string | |
category | string | |

#### SKU 
SKU are kept in table `skus_beibei` 
name | type | description |
---- | ---- | ---- |
id |  int | |
name | string | |
product_id | int | |
price | int | |
origin_price | int | |
stock | int | |
img_sku_attr_code | string | The SKU attribute value code which can decide the image(Image only depends on one SKU attribute, no combination). |

#### SKU Images
SKU Images are kept in table `sku_images_beibei`
name | type | description |
---- | ---- | ---- |
product_id | int | |
sku_attr_code | string | |
uploaded_path | string | |

 #### image
 It uploads the product images to 
 ```
 https://v0.api.upyun.com/mbcrawl/{bucket}/{prefix}/{uploaded_path}.jpg
 ```
The uploaded path can be retrived by following JOIN criteria from a SKU.

```
skus_beibei.product_id=sku_images_beibei.product_id and skus_beibei.img_sku_attr_code=sku_images_beibei.sku_attr_code
```

### How to run it
The suggested method is using docker compose.
```
docker-compose build 
docker-compose up
```
There are two services:
 - db, the PostgreSQL server, both user name and database are `mbcrawl` with empty password
 - crawler, the crawler 
