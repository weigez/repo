import scrapy
import json

class NikeProductsSpider(scrapy.Spider):
    name = "nike_products"
    allowed_domains = ["nike.com.cn"]
    start_urls = ["https://www.nike.com.cn/w/"]

    def parse(self, response):
        # 提取前48个产品链接
        product_links = response.xpath('//a[@class="product-card__link-overlay"]/@href').getall()[:48]

        for link in product_links:
            yield scrapy.Request(url=link, callback=self.parse_product)

    def parse_product(self, response):
        script_data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if not script_data:
            self.logger.warning("未找到 __NEXT_DATA__ 数据")
            return

        try:
            data = json.loads(script_data)
        except json.JSONDecodeError:
            self.logger.warning("JSON 解析失败")
            return

        page_props = data.get("props", {}).get("pageProps", {})

        # 获取 colorwayImages 中的第一个商品数据（主款）
        colorway_images = page_props.get("colorwayImages", [])
        if not colorway_images:
            return

        main_product = colorway_images[0]
        sku = main_product.get("styleColor")  # 主要 SKU

        # 获取产品组中的详细信息
        product_groups = page_props.get("productGroups", [])
        if not product_groups:
            return

        products = product_groups[0].get("products", {})
        product_info = products.get(sku, {})

        # 提取标题
        title = main_product.get("altText", "").strip()

        # 提取颜色
        color = main_product.get("colorDescription", "")

        # 提取货号
        style_color = product_info.get("styleColor", "")

        # 提取价格
        price_info = product_info.get("prices", {})
        current_price = price_info.get("currentPrice")

        # 提取尺码列表
        sizes = [size.get("label") for size in product_info.get("sizes", []) if size.get("status") == "ACTIVE"]

        # 提取详情描述
        product_description = product_info.get("productInfo", {}).get("productDescription", "").strip()

        # 提取产品细节
        product_details = product_info.get("productInfo", {}).get("productDetails", [])
        details_list = []
        for detail_section in product_details:
            header = detail_section.get("header", "")
            body_items = detail_section.get("body", [])
            details_list.append(f"{header}: {'; '.join(body_items)}")

        details = "\n".join(details_list)

        # 提取图片 URL 列表
        img_items = product_info.get("contentImages", [])
        img_urls = [
            img.get("properties", {}).get("squarish", {}).get("url")
            for img in img_items
            if img.get("properties", {}).get("squarish", {}).get("url")
        ]

        yield {
            "title": title,
            "price": current_price,
            "color": color,
            "sizes": sizes,
            "sku": style_color,
            "description": product_description,
            "details": details,
            "img_urls": img_urls,
            "url": response.url
        }