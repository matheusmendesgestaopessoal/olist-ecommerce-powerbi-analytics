SELECT
    COUNT(*) AS total,

    COUNT(*) FILTER (
        WHERE order_id IS NULL OR TRIM(order_id) = ''
    ) AS order_id_nulo,

    COUNT(*) FILTER (
        WHERE customer_id IS NULL OR TRIM(customer_id) = ''
    ) AS customer_id_nulo,

    COUNT(*) FILTER (
        WHERE order_status IS NULL OR TRIM(order_status) = ''
    ) AS order_status_nulo,

    COUNT(*) FILTER (
        WHERE order_purchase_timestamp IS NULL
           OR TRIM(order_purchase_timestamp) = ''
    ) AS purchase_timestamp_nulo,

    COUNT(*) FILTER (
        WHERE order_approved_at IS NULL
           OR TRIM(order_approved_at) = ''
    ) AS approved_at_nulo,

    COUNT(*) FILTER (
        WHERE order_delivered_customer_date IS NULL
           OR TRIM(order_delivered_customer_date) = ''
    ) AS delivered_customer_date_nulo

FROM raw.orders;

SELECT
    COUNT(*) AS total,

    COUNT(*) FILTER (
        WHERE order_id IS NULL OR TRIM(order_id) = ''
    ) AS order_id_nulo,

    COUNT(*) FILTER (
        WHERE product_id IS NULL OR TRIM(product_id) = ''
    ) AS product_id_nulo,

    COUNT(*) FILTER (
        WHERE seller_id IS NULL OR TRIM(seller_id) = ''
    ) AS seller_id_nulo,

    COUNT(*) FILTER (
        WHERE price IS NULL OR TRIM(price) = ''
    ) AS price_nulo,

    COUNT(*) FILTER (
        WHERE freight_value IS NULL OR TRIM(freight_value) = ''
    ) AS freight_nulo

FROM raw.order_items;

SELECT
    COUNT(*) AS total,

    COUNT(*) FILTER (
        WHERE product_id IS NULL OR TRIM(product_id) = ''
    ) AS product_id_nulo,

    COUNT(*) FILTER (
        WHERE product_category_name IS NULL
           OR TRIM(product_category_name) = ''
    ) AS categoria_nula

FROM raw.products;

SELECT
    COUNT(*) AS total,

    COUNT(*) FILTER (
        WHERE seller_id IS NULL OR TRIM(seller_id) = ''
    ) AS seller_id_nulo,

    COUNT(*) FILTER (
        WHERE seller_city IS NULL OR TRIM(seller_city) = ''
    ) AS cidade_nula,

    COUNT(*) FILTER (
        WHERE seller_state IS NULL OR TRIM(seller_state) = ''
    ) AS estado_nulo

FROM raw.sellers;

SELECT
    COUNT(*) AS total,

    COUNT(*) FILTER (
        WHERE order_id IS NULL OR TRIM(order_id) = ''
    ) AS order_id_nulo,

    COUNT(*) FILTER (
        WHERE review_score IS NULL OR TRIM(review_score) = ''
    ) AS review_score_nulo,

    COUNT(*) FILTER (
        WHERE review_comment_title IS NULL
           OR TRIM(review_comment_title) = ''
    ) AS titulo_nulo,

    COUNT(*) FILTER (
        WHERE review_comment_message IS NULL
           OR TRIM(review_comment_message) = ''
    ) AS comentario_nulo

FROM raw.order_reviews;