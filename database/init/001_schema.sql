CREATE TABLE stores (
    store_id TEXT PRIMARY KEY,
    store_name TEXT NOT NULL,
    region TEXT NOT NULL,
    store_type TEXT NOT NULL,
    opened_date DATE NOT NULL
);

CREATE TABLE products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_cost NUMERIC(12, 2) NOT NULL CHECK (unit_cost >= 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= unit_cost)
);

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    segment TEXT NOT NULL,
    region TEXT NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE sales (
    sale_id BIGINT PRIMARY KEY,
    sale_date DATE NOT NULL,
    store_id TEXT NOT NULL REFERENCES stores (store_id),
    product_id TEXT NOT NULL REFERENCES products (product_id),
    customer_id TEXT NOT NULL REFERENCES customers (customer_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount NUMERIC(5, 4) NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 1),
    sales_amount NUMERIC(14, 2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount)) STORED
);

CREATE TABLE inventory (
    inventory_date DATE NOT NULL,
    store_id TEXT NOT NULL REFERENCES stores (store_id),
    product_id TEXT NOT NULL REFERENCES products (product_id),
    stock_on_hand INTEGER NOT NULL CHECK (stock_on_hand >= 0),
    reorder_point INTEGER NOT NULL CHECK (reorder_point >= 0),
    stock_in INTEGER NOT NULL DEFAULT 0 CHECK (stock_in >= 0),
    stock_out INTEGER NOT NULL DEFAULT 0 CHECK (stock_out >= 0),
    PRIMARY KEY (inventory_date, store_id, product_id)
);

CREATE TABLE sales_daily (
    sales_date DATE NOT NULL,
    store_id TEXT NOT NULL REFERENCES stores (store_id),
    product_id TEXT NOT NULL REFERENCES products (product_id),
    sales_amount NUMERIC(14, 2) NOT NULL CHECK (sales_amount >= 0),
    gross_profit NUMERIC(14, 2) NOT NULL,
    customer_count INTEGER NOT NULL CHECK (customer_count >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (sales_date, store_id, product_id)
);

CREATE TABLE anomaly_results (
    anomaly_id BIGSERIAL PRIMARY KEY,
    detected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('store', 'product')),
    entity_id TEXT NOT NULL,
    anomaly_type TEXT NOT NULL,
    anomaly_score NUMERIC(12, 6),
    evidence JSONB NOT NULL,
    detection_method TEXT NOT NULL
);

CREATE TABLE forecast_results (
    forecast_id BIGSERIAL PRIMARY KEY,
    forecast_date DATE NOT NULL,
    store_id TEXT NOT NULL REFERENCES stores (store_id),
    model_name TEXT NOT NULL,
    predicted_sales NUMERIC(14, 2) NOT NULL CHECK (predicted_sales >= 0),
    actual_sales NUMERIC(14, 2),
    evaluation_mae NUMERIC(14, 6),
    evaluation_rmse NUMERIC(14, 6),
    evaluation_period_start DATE,
    evaluation_period_end DATE,
    CHECK (evaluation_period_end IS NULL OR evaluation_period_start IS NOT NULL)
);

CREATE TABLE copilot_insights (
    insight_id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    scope TEXT NOT NULL,
    entity_type TEXT,
    entity_id TEXT,
    current_situation TEXT NOT NULL,
    evidence JSONB NOT NULL,
    possible_factors JSONB NOT NULL,
    risk TEXT NOT NULL CHECK (risk IN ('low', 'medium', 'high')),
    recommended_action TEXT NOT NULL,
    generation_method TEXT NOT NULL
);

CREATE INDEX idx_sales_date_store ON sales (sale_date, store_id);
CREATE INDEX idx_sales_product_date ON sales (product_id, sale_date);
CREATE INDEX idx_inventory_store_product ON inventory (store_id, product_id);
CREATE INDEX idx_anomaly_entity ON anomaly_results (entity_type, entity_id, detected_at);
CREATE INDEX idx_forecast_store_date ON forecast_results (store_id, forecast_date);
