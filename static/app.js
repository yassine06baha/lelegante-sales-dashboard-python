async function loadSummary() {
    const response = await fetch("/api/summary");
    const summary = await response.json();

    document.getElementById("revenueValue").textContent = `${summary.revenue.toFixed(2)} EUR`;
    document.getElementById("unitsValue").textContent = summary.unitsSold;
    document.getElementById("stockAlertValue").textContent = summary.lowStockCount;
    document.getElementById("bestProductValue").textContent = summary.bestProduct;
}

async function loadProducts() {
    const response = await fetch("/api/products");
    const products = await response.json();
    const body = document.getElementById("productsBody");

    body.innerHTML = products
        .map(
            (product) => `
                <tr>
                    <td>${product.name}</td>
                    <td>${product.category}</td>
                    <td>${product.price.toFixed(2)} EUR</td>
                    <td>${product.stock_quantity}</td>
                    <td>
                        <span class="badge ${product.low_stock ? "low" : "ok"}">
                            ${product.low_stock ? "À réassortir" : "Stable"}
                        </span>
                    </td>
                </tr>
            `
        )
        .join("");
}

async function loadSalesChart() {
    const response = await fetch("/api/sales");
    const sales = await response.json();
    const chart = document.getElementById("salesChart");
    const maxUnits = Math.max(...sales.map((item) => item.total_units), 1);

    chart.innerHTML = sales
        .map((item) => {
            const height = Math.round((item.total_units / maxUnits) * 290) + 20;
            const label = item.sale_date.slice(5).replace("-", "/");

            return `
                <div class="bar-item">
                    <div class="bar" style="height: ${height}px" title="${item.total_units} ventes"></div>
                    <span class="bar-label">${label}</span>
                </div>
            `;
        })
        .join("");
}

Promise.all([loadSummary(), loadProducts(), loadSalesChart()]);
