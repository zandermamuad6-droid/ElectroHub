
/*
 * ElectroHub frontend prototype.
 * Product data is currently sample data.
 * Later, Django REST Framework will provide real products and sellers.
 */

const products = [
    {
        id: 1,
        name: "Arduino Uno R3",
        price: 450,
        seller: "Tech Parts Shop",
        category: "Microcontrollers",
        image: "🔌"
    },
    {
        id: 2,
        name: "Ultrasonic Sensor HC-SR04",
        price: 85,
        seller: "Circuit Corner",
        category: "Sensors",
        image: "📡"
    },
    {
        id: 3,
        name: "Resistor Assortment Kit",
        price: 120,
        seller: "Tech Parts Shop",
        category: "Resistors",
        image: "🔧"
    },
    {
        id: 4,
        name: "Capacitor Assortment",
        price: 150,
        seller: "Circuit Corner",
        category: "Capacitors",
        image: "⚡"
    },
    {
        id: 5,
        name: "ESP32 Development Board",
        price: 280,
        seller: "Maker Supplies",
        category: "Development Boards",
        image: "💻"
    },
    {
        id: 6,
        name: "Breadboard and Jumper Wires",
        price: 95,
        seller: "Maker Supplies",
        category: "Accessories",
        image: "🔋"
    },
    {
        id: 7,
        name: "PIR Motion Sensor",
        price: 110,
        seller: "Circuit Corner",
        category: "Sensors",
        image: "📟"
    },
    {
        id: 8,
        name: "Jumper Wire Set",
        price: 75,
        seller: "Maker Supplies",
        category: "Accessories",
        image: "〰️"
    },
    {
        id: 9,
        name: "Digital Multimeter",
        price: 350,
        seller: "Tech Parts Shop",
        category: "Tools",
        image: "🔌"
    }
];

// Shopping cart holds product IDs for this browser session.
const cart = [];

let selectedCategory = "All";

const productGrid = document.getElementById("productGrid");
const searchInput = document.getElementById("searchInput");
const cartCount = document.getElementById("cartCount");
const productTotal = document.getElementById("productTotal");

const cartModal = document.getElementById("cartModal");
const cartItems = document.getElementById("cartItems");
const cartTotal = document.getElementById("cartTotal");

const cartButton = document.getElementById("cartButton");
const closeCartButton = document.getElementById("closeCartButton");
const sellerInfoButton = document.getElementById("sellerInfoButton");

function formatPrice(price) {
    return `₱${price.toLocaleString("en-PH", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}

function displayProducts() {
    const query = searchInput.value.toLowerCase().trim();

    const filteredProducts = products.filter((product) => {
        const matchesSearch =
            product.name.toLowerCase().includes(query) ||
            product.category.toLowerCase().includes(query) ||
            product.seller.toLowerCase().includes(query);

        const matchesCategory =
            selectedCategory === "All" ||
            product.category === selectedCategory;

        return matchesSearch && matchesCategory;
    });

    productGrid.replaceChildren();
    productTotal.textContent =
        `${filteredProducts.length} product${filteredProducts.length === 1 ? "" : "s"}`;

    if (filteredProducts.length === 0) {
        const message = document.createElement("p");
        message.className = "empty-message";
        message.textContent =
            "No components found. Try another search or category.";
        productGrid.appendChild(message);
        return;
    }

    filteredProducts.forEach((product) => {
        const card = document.createElement("article");
        card.className = "product-card";

        const image = document.createElement("div");
        image.className = "product-image";
        image.setAttribute("aria-hidden", "true");
        image.textContent = product.image;

        const category = document.createElement("span");
        category.className = "product-category";
        category.textContent = product.category;

        const name = document.createElement("h3");
        name.textContent = product.name;

        const seller = document.createElement("p");
        seller.className = "product-seller";
        seller.textContent = `Sold by ${product.seller}`;

        const price = document.createElement("p");
        price.className = "product-price";
        price.textContent = formatPrice(product.price);

        const button = document.createElement("button");
        button.className = "add-button";
        button.textContent = "Add to Cart";

        button.addEventListener("click", () => {
            cart.push(product.id);
            updateCartCount();
            button.textContent = "Added to Cart ✓";

            window.setTimeout(() => {
                button.textContent = "Add to Cart";
            }, 1000);
        });

        card.append(image, category, name, seller, price, button);
        productGrid.appendChild(card);
    });
}

function updateCartCount() {
    cartCount.textContent = cart.length;
}

function displayCart() {
    cartItems.replaceChildren();

    if (cart.length === 0) {
        const message = document.createElement("p");
        message.className = "empty-message";
        message.textContent = "Your cart is empty.";
        cartItems.appendChild(message);
        cartTotal.textContent = formatPrice(0);
        return;
    }

    let total = 0;

    cart.forEach((productId, index) => {
        const product = products.find((item) => item.id === productId);

        if (!product) return;

        total += product.price;

        const item = document.createElement("article");
        item.className = "cart-item";

        const details = document.createElement("div");

        const name = document.createElement("h3");
        name.textContent = product.name;

        const price = document.createElement("p");
        price.textContent = formatPrice(product.price);

        details.append(name, price);

        const removeButton = document.createElement("button");
        removeButton.className = "remove-button";
        removeButton.textContent = "Remove";

        removeButton.addEventListener("click", () => {
            cart.splice(index, 1);
            updateCartCount();
            displayCart();
        });

        item.append(details, removeButton);
        cartItems.appendChild(item);
    });

    cartTotal.textContent = formatPrice(total);
}

function openCart() {
    displayCart();
    cartModal.hidden = false;
    closeCartButton.focus();
}

function closeCart() {
    cartModal.hidden = true;
    cartButton.focus();
}

if (searchInput) {
    searchInput.addEventListener("input", displayProducts);
}

document.querySelectorAll(".category-link").forEach((button) => {
    button.addEventListener("click", () => {
        selectedCategory = button.dataset.category;

        document.querySelectorAll(".category-link").forEach((item) => {
            item.classList.toggle("active", item === button);
        });

        displayProducts();
        document.getElementById("products").scrollIntoView({
            behavior: "smooth"
        });
    });
});

cartButton.addEventListener("click", openCart);
closeCartButton.addEventListener("click", closeCart);

cartModal.addEventListener("click", (event) => {
    if (event.target === cartModal) {
        closeCart();
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !cartModal.hidden) {
        closeCart();
    }
});

sellerInfoButton.addEventListener("click", () => {
    window.alert(
        "Seller registration will be available when we build the Django backend."
    );
});

// Render the initial product catalog.
displayProducts();
updateCartCount();
