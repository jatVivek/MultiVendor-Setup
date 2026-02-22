import { api } from './api.js';

var app = {
    state: {
        categories: [],
        banners: [],
        featuredProducts: [],
        products: [],
        user: JSON.parse(localStorage.getItem('user')),
        cart: api.getCart()
    },

    init() {
        this.updateHeader();
        this.handleHashChange();
        this.initLocation();
        window.addEventListener('hashchange', () => this.handleHashChange());
    },

    initLocation() {
        const lat = localStorage.getItem('lat');
        const long = localStorage.getItem('long');
        if (lat && long) {
            document.getElementById('location-text').textContent = "Location Active";
            document.getElementById('location-btn').classList.add('text-green-600', 'border-green-600');
        }
    },

    enableLocation() {
        if (navigator.geolocation) {
            document.getElementById('location-text').textContent = "Locating...";
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    localStorage.setItem('lat', pos.coords.latitude);
                    localStorage.setItem('long', pos.coords.longitude);
                    document.getElementById('location-text').textContent = "Location Active";
                    document.getElementById('location-btn').classList.add('text-green-600', 'border-green-600');
                    alert("Location enabled! Showing nearby products.");
                    // Reload products with location
                    this.renderHome(); 
                },
                (err) => {
                    alert("Location access denied. Showing all products.");
                    document.getElementById('location-text').textContent = "Enable Location";
                }
            );
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    },

    router(route) {
        window.location.hash = route;
    },

    handleHashChange() {
        const hash = window.location.hash.slice(1) || 'home';
        const [page, id] = hash.split('/');

        if (page === 'home') this.renderHome();
        else if (page === 'products') this.renderPLP();
        else if (page === 'product') this.renderPDP(id);
        else if (page === 'cart') this.renderCart();
        else if (page === 'orders') this.renderOrders();
        else if (page === 'page') this.renderStaticPage(id);
        else this.renderHome();
    },

    async renderStaticPage(slug) {
        const container = document.getElementById('app-container');
        const page = await api.getPage(slug);
        
        container.innerHTML = `
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-3xl font-bold mb-6">${page.title}</h1>
                <div class="prose max-w-none text-gray-700">
                    ${page.content}
                </div>
            </div>
        `;
    },

    updateHeader() {
        // Cart Count
        document.getElementById('cart-count').textContent = this.state.cart.reduce((acc, item) => acc + item.quantity, 0);
        
        // Auth Menu
        const authLinks = document.getElementById('auth-links');
        const userLinks = document.getElementById('user-links');
        
        if (this.state.user) {
            authLinks.innerHTML = `
                <h4 class="font-bold text-sm mb-1">Hello, ${this.state.user.name || 'User'}</h4>
                <p class="text-xs text-gray-500 mb-3">${this.state.user.mobile}</p>
            `;
            userLinks.classList.remove('hidden');
        } else {
            userLinks.classList.add('hidden');
        }
    },

    logout() {
        api.logout();
    },

    async renderHome() {
        const container = document.getElementById('app-container');
        container.innerHTML = '<div class="flex justify-center pt-20"><div class="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600"></div></div>';

        // Fetch data
        const [cats, banners, prods] = await Promise.all([
            api.getCategories(),
            api.getBanners('Home'),
            api.getProducts() // Get all for "Featured" simulation
        ]);

        this.state.categories = cats;
        this.state.banners = banners;
        this.state.featuredProducts = prods.slice(0, 8); // Top 8

        // Nav Bar (Categories)
        const navHTML = `
            <div class="bg-white shadow-sm mb-4">
                <div class="container mx-auto px-4 overflow-x-auto hide-scrollbar flex space-x-8 py-3 justify-center">
                    ${cats.map(c => `
                        <div class="flex flex-col items-center cursor-pointer min-w-[64px]" onclick="app.router('products?cat=${c.id}')">
                            <img src="${c.image_url || 'https://via.placeholder.com/64'}" class="h-12 w-12 rounded-full object-cover mb-1 border hover:border-yellow-500">
                            <span class="text-xs font-bold text-gray-700 hover:text-yellow-600">${c.name}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Hero Banner
        const heroHTML = banners.length > 0 ? `
            <div class="relative w-full h-64 md:h-96 overflow-hidden bg-gray-200">
                <img src="${banners[0].image_url}" class="w-full h-full object-cover" alt="Banner">
                <div class="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center">
                    <h2 class="text-4xl text-white font-bold shadow-sm">Huge Savings on Coffee</h2>
                </div>
            </div>
        ` : '';

        // Featured Grid
        const gridHTML = `
            <div class="container mx-auto px-4 py-8">
                <h3 class="text-2xl font-bold mb-6">Featured Products</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                    ${this.state.featuredProducts.map(p => this.ProductCard(p)).join('')}
                </div>
            </div>
        `;

        container.innerHTML = navHTML + heroHTML + gridHTML;
    },

    ProductCard(p) {
        return `
            <div class="bg-white hover:shadow-lg transition duration-300 border border-gray-100 p-3 group cursor-pointer" onclick="app.router('product/${p.id}')">
                <div class="h-48 overflow-hidden relative">
                    <img src="${p.image_url || 'https://via.placeholder.com/200'}" class="w-full h-full object-contain group-hover:scale-105 transition duration-300">
                </div>
                <div class="mt-3">
                    <h4 class="font-bold text-gray-700 truncate">${p.name}</h4>
                    <p class="text-xs text-gray-500 truncate">${p.description || 'Premium Quality'}</p>
                    <div class="flex items-center mt-1 space-x-2">
                        <span class="font-bold text-sm">₹${p.price}</span>
                        ${p.old_price ? `<span class="text-xs text-gray-400 line-through">₹${p.old_price}</span>` : ''}
                        ${p.old_price ? `<span class="text-xs text-orange-500">(${Math.round(((p.old_price-p.price)/p.old_price)*100)}% OFF)</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    async renderPLP() {
        const container = document.getElementById('app-container');
        const prods = await api.getProducts(); // In real app, parse URL query params for filter
        
        container.innerHTML = `
            <div class="container mx-auto px-4 py-6 flex">
                <!-- Filters -->
                <aside class="w-1/5 hidden md:block pr-6 border-r">
                    <h3 class="font-bold mb-4">FILTERS</h3>
                    <div class="mb-4">
                        <h4 class="text-sm font-semibold mb-2">CATEGORIES</h4>
                        ${this.state.categories.map(c => `
                            <label class="flex items-center space-x-2 text-sm text-gray-600 mb-1 cursor-pointer">
                                <input type="checkbox" class="form-checkbox text-yellow-600">
                                <span>${c.name}</span>
                            </label>
                        `).join('')}
                    </div>
                    <div class="mb-4">
                        <h4 class="text-sm font-semibold mb-2">PRICE</h4>
                        <label class="flex items-center space-x-2 text-sm text-gray-600 mb-1"><input type="checkbox"> <span>Under ₹500</span></label>
                        <label class="flex items-center space-x-2 text-sm text-gray-600 mb-1"><input type="checkbox"> <span>₹500 - ₹1000</span></label>
                    </div>
                </aside>
                
                <!-- Grid -->
                <div class="w-full md:w-4/5 pl-4">
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-sm text-gray-500">Showing ${prods.length} items</span>
                        <select class="border p-1 text-sm rounded">
                            <option>Recommended</option>
                            <option>Price: Low to High</option>
                            <option>Price: High to Low</option>
                        </select>
                    </div>
                    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        ${prods.map(p => this.ProductCard(p)).join('')}
                    </div>
                </div>
            </div>
        `;
    },

    async renderPDP(id) {
        const container = document.getElementById('app-container');
        const p = await api.getProduct(id);
        
        if (!p) { container.innerHTML = 'Product Not Found'; return; }
        
        container.innerHTML = `
            <div class="container mx-auto px-4 py-8">
                <div class="flex flex-col md:flex-row bg-white shadow-sm p-4">
                    <!-- Gallery -->
                    <div class="w-full md:w-2/5 flex">
                        <div class="w-full h-96 border flex items-center justify-center overflow-hidden">
                            <img src="${p.image_url}" class="max-h-full max-w-full object-contain hover:scale-110 transition duration-500">
                        </div>
                    </div>
                    
                    <!-- Details -->
                    <div class="w-full md:w-3/5 md:pl-10 mt-6 md:mt-0">
                        <h1 class="text-2xl font-bold text-gray-800 mb-2">${p.name}</h1>
                        <p class="text-gray-500 text-lg mb-4">${p.description}</p>
                        
                        <div class="border-t border-b py-4 mb-6">
                            <div class="flex items-baseline space-x-4">
                                <span class="text-3xl font-bold text-gray-900">₹${p.price}</span>
                                ${p.old_price ? `<span class="text-xl text-gray-400 line-through">₹${p.old_price}</span>` : ''}
                                ${p.old_price ? `<span class="text-xl text-orange-500 font-bold">(${Math.round(((p.old_price-p.price)/p.old_price)*100)}% OFF)</span>` : ''}
                            </div>
                            <p class="text-green-600 text-sm mt-1 font-bold">inclusive of all taxes</p>
                        </div>
                        
                        <div class="flex space-x-4 mb-8">
                            <button onclick="app.addToCart(${p.id}, '${p.name}', ${p.price}, '${p.image_url}')" class="flex-1 bg-yellow-600 text-white font-bold py-4 rounded shadow hover:bg-yellow-700 flex justify-center items-center gap-2">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
                                ADD TO BAG
                            </button>
                            <button class="flex-1 border border-gray-300 text-gray-800 font-bold py-4 rounded hover:border-gray-800">WISHLIST</button>
                        </div>
                        
                        <div>
                            <h3 class="font-bold text-sm mb-2 flex items-center gap-2">
                                DELIVERY OPTIONS <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            </h3>
                            <div class="flex border rounded w-64">
                                <input type="text" placeholder="Enter Pincode" class="p-2 flex-1 focus:outline-none">
                                <button class="text-yellow-600 font-bold px-4 hover:text-yellow-800">Check</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Reviews -->
                <div class="mt-12 bg-white shadow-sm p-6">
                    <h3 class="font-bold text-xl mb-4">Ratings & Reviews</h3>
                    <div id="reviews-container">Loading reviews...</div>
                </div>
            </div>
        `;
        this.loadReviews(id);
    },

    async loadReviews(id) {
        const reviews = await api.getReviews(id);
        const container = document.getElementById('reviews-container');
        
        if (reviews.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No reviews yet.</p>';
            return;
        }
        
        container.innerHTML = reviews.map(r => `
            <div class="border-b py-4">
                <div class="flex items-center gap-2 mb-1">
                    <span class="bg-green-600 text-white text-xs font-bold px-2 py-0.5 rounded">${r.rating} ★</span>
                    <span class="font-bold text-sm">${r.customer_name || 'Customer'}</span>
                </div>
                <p class="text-gray-600 text-sm">${r.comment}</p>
                <p class="text-xs text-gray-400 mt-1">${new Date(r.created_at).toLocaleDateString()}</p>
            </div>
        `).join('');
    },

    addToCart(id, name, price, img) {
        api.addToCart({ id, name, price, image_url: img });
        this.state.cart = api.getCart();
        this.updateHeader();
        alert('Added to Bag');
    },

    renderCart() {
        const container = document.getElementById('app-container');
        const cart = this.state.cart;
        
        if (cart.length === 0) {
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center h-96">
                    <img src="https://constant.myntassets.com/checkout/assets/img/empty-bag.png" class="h-32 mb-4">
                    <h3 class="text-xl font-bold">Hey, it feels so light!</h3>
                    <p class="text-gray-500 mb-6">There is nothing in your bag. Let's add some items.</p>
                    <button onclick="app.router('home')" class="bg-yellow-600 text-white px-6 py-2 rounded font-bold">ADD ITEMS FROM WISHLIST</button>
                </div>
            `;
            return;
        }
        
        const total = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        
        container.innerHTML = `
            <div class="container mx-auto px-4 py-8 flex flex-col md:flex-row gap-8">
                <!-- Items -->
                <div class="w-full md:w-2/3">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="font-bold">My Bag <span class="text-gray-500 text-sm">(${cart.length} items)</span></h3>
                    </div>
                    
                    ${cart.map(item => `
                        <div class="flex border p-4 mb-4 bg-white relative">
                            <img src="${item.image || 'https://via.placeholder.com/100'}" class="h-24 w-24 object-cover">
                            <div class="ml-4 flex-1">
                                <h4 class="font-bold text-sm">${item.name}</h4>
                                <p class="text-xs text-gray-500 mb-2">Sold by: Zenbrew Vendor</p>
                                <div class="flex items-center space-x-2">
                                    <span class="font-bold">₹${item.price}</span>
                                </div>
                                <div class="mt-2 text-sm">Qty: ${item.quantity}</div>
                            </div>
                            <button onclick="app.removeFromCart(${item.product_id})" class="absolute top-4 right-4 text-gray-400 hover:text-red-500">
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                            </button>
                        </div>
                    `).join('')}
                </div>
                
                <!-- Price Details -->
                <div class="w-full md:w-1/3">
                    <div class="bg-white p-4 border sticky top-24">
                        <h4 class="font-bold text-xs text-gray-500 mb-4">PRICE DETAILS</h4>
                        <div class="flex justify-between mb-2 text-sm">
                            <span>Total MRP</span>
                            <span>₹${total}</span>
                        </div>
                        <div class="flex justify-between mb-2 text-sm text-green-600">
                            <span>Discount on MRP</span>
                            <span>-₹0</span>
                        </div>
                        <div class="flex justify-between mb-4 text-sm">
                            <span>Convenience Fee</span>
                            <span>₹20</span>
                        </div>
                        <div class="border-t pt-4 flex justify-between font-bold text-lg mb-4">
                            <span>Total Amount</span>
                            <span>₹${total + 20}</span>
                        </div>
                        
                        <button onclick="app.placeOrder()" class="w-full bg-yellow-600 text-white font-bold py-3 rounded hover:bg-yellow-700">PLACE ORDER</button>
                    </div>
                </div>
            </div>
        `;
    },

    removeFromCart(id) {
        api.removeFromCart(id);
        this.state.cart = api.getCart();
        this.updateHeader();
        this.renderCart();
    },

    async placeOrder() {
        if (!this.state.user) {
            this.showModal('login');
            return;
        }
        
        // Transform cart to API format
        const items = this.state.cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        }));
        
        const res = await api.placeOrder({ items, payment_method: 'COD' });
        
        if (res.ok) {
            alert(`Order Placed Successfully! IDs: ${res.data.order_ids.join(', ')}`);
            api.clearCart();
            this.state.cart = [];
            this.updateHeader();
            this.router('home');
        } else {
            alert(`Order Failed: ${res.data.message}`);
        }
    },

    async renderOrders() {
        if (!this.state.user) { this.router('home'); return; }
        const container = document.getElementById('app-container');
        const orders = await api.getMyOrders();
        
        container.innerHTML = `
            <div class="container mx-auto px-4 py-8">
                <h2 class="text-2xl font-bold mb-6">My Orders</h2>
                <div class="space-y-4">
                    ${orders.map(o => `
                        <div class="bg-white p-4 rounded shadow border flex flex-col md:flex-row justify-between items-center">
                            <div>
                                <h4 class="font-bold">Order #${o.id}</h4>
                                <p class="text-sm text-gray-500">Placed on ${new Date(o.created_at).toLocaleDateString()}</p>
                                <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded mt-2 inline-block">${o.status}</span>
                            </div>
                            <div class="text-right mt-4 md:mt-0">
                                <p class="font-bold text-lg">₹${o.total_amount}</p>
                                <p class="text-xs text-gray-500">${o.payment_method}</p>
                                <button onclick="api.downloadInvoice(${o.id})" class="text-blue-600 text-xs hover:underline mt-2 block">Download Invoice</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    // Modals
    showModal(type) {
        const container = document.getElementById('modal-container');
        const content = document.getElementById('modal-content');
        container.classList.remove('hidden');
        
        if (type === 'login') {
            content.innerHTML = `
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">Login / Signup</h3>
                    <div class="mt-4">
                        <input type="tel" id="mobile" class="w-full border p-2 rounded mb-3" placeholder="Mobile Number">
                        <input type="password" id="password" class="w-full border p-2 rounded mb-3" placeholder="Password">
                        <button onclick="app.handleLogin()" class="w-full bg-yellow-600 text-white font-bold py-2 rounded">CONTINUE</button>
                    </div>
                    <p class="text-xs text-center mt-3 text-gray-500">By continuing, you agree to Terms of Use</p>
                </div>
            `;
        }
    },

    hideModal() {
        document.getElementById('modal-container').classList.add('hidden');
    },

    async handleLogin() {
        const mobile = document.getElementById('mobile').value;
        const password = document.getElementById('password').value;
        const res = await api.login(mobile, password);
        if (res.ok) {
            this.state.user = res.data.user;
            this.hideModal();
            this.updateHeader();
            alert('Logged in successfully');
        } else {
            alert('Login failed');
        }
    }
};

window.app = app; // Expose to window
// No wait for DOMContentLoaded, init immediately if loaded as module at end of body
app.init();
