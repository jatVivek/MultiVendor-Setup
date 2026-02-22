const API_BASE = '/api';

export const api = {
    // Auth
    async login(mobile, password, role = 'customer') {
        const res = await fetch(`${API_BASE}/${role}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mobile, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('role', role);
        }
        return { ok: res.ok, data };
    },

    async register(data, role = 'customer') {
        const res = await fetch(`${API_BASE}/${role}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return { ok: res.ok, data: await res.json() };
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('role');
        window.location.reload();
    },

    // Products
    async getProducts(params = {}) {
        // Auto-inject location if available
        const lat = localStorage.getItem('lat');
        const long = localStorage.getItem('long');
        if (lat && long && !params.lat) {
            params.lat = lat;
            params.long = long;
        }

        const query = new URLSearchParams(params).toString();
        const url = params.lat ? `${API_BASE}/products/nearby?${query}` : `${API_BASE}/products?${query}`;
        const res = await fetch(url);
        return await res.json();
    },

    async getProduct(id) {
        // Since API doesn't expose public single product endpoint yet (only admin), 
        // we'll fetch all and find (inefficient but works for MVP without changing backend now)
        // Or assume products array contains details.
        // Actually routes.py: get_products returns full details.
        const products = await this.getProducts();
        return products.find(p => p.id === parseInt(id));
    },

    async getCategories() {
        const res = await fetch(`${API_BASE}/categories`);
        return await res.json();
    },

    async getBanners(type = 'Home') {
        const res = await fetch(`${API_BASE}/banners?type=${type}`);
        return await res.json();
    },

    // Orders
    async placeOrder(orderData) {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/orders`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify(orderData)
        });
        return { ok: res.ok, data: await res.json() };
    },

    async getMyOrders() {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/customer/orders`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return await res.json();
    },

    async addMoney(amount) {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/customer/wallet`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify({ amount })
        });
        return { ok: res.ok, data: await res.json() };
    },

    // Cart (Local Storage)
    getCart() {
        return JSON.parse(localStorage.getItem('cart') || '[]');
    },

    addToCart(product, qty = 1) {
        const cart = this.getCart();
        const existing = cart.find(item => item.product_id === product.id);
        if (existing) {
            existing.quantity += qty;
        } else {
            cart.push({ product_id: product.id, name: product.name, price: product.price, image: product.image_url, quantity: qty });
        }
        localStorage.setItem('cart', JSON.stringify(cart));
    },

    removeFromCart(id) {
        let cart = this.getCart();
        cart = cart.filter(item => item.product_id !== id);
        localStorage.setItem('cart', JSON.stringify(cart));
    },
    
    clearCart() {
        localStorage.removeItem('cart');
    }
};
    async getVendors() {
        // Mock or simple fetch if endpoint exists. 
        // We implemented /admin/vendors but no public vendor list.
        // Let's rely on product data extraction or add a simple endpoint.
        // For MVP frontend, we extract from products for now.
        const products = await this.getProducts();
        const vendors = [...new Set(products.map(p => p.vendor_id))]; // IDs
        return vendors; 
        // Ideally: GET /api/vendors (public)
    },

    async getPage(slug) {
        const res = await fetch(`${API_BASE}/pages/${slug}`);
        return await res.json();
    },
    async getReviews(productId) {
        const res = await fetch(`${API_BASE}/products/${productId}/reviews`);
        return await res.json();
    },

    async downloadInvoice(orderId) {
        const token = localStorage.getItem('token');
        const res = await fetch(`${API_BASE}/orders/${orderId}/invoice`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `invoice_${orderId}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Failed to download invoice");
        }
    },
