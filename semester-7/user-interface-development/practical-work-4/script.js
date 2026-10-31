// ============================================
// Отображение консоли на HTML-странице
// ============================================

const outputElement = document.getElementById("console-output");

const originalConsoleLog = console.log.bind(console);

function formatConsoleValue(value) {
    if (typeof value === "string") {
        return value;
    }

    if (value === undefined) {
        return "undefined";
    }

    if (value instanceof Error) {
        return `${value.name}: ${value.message}`;
    }

    if (typeof value === "object" && value !== null) {
        return JSON.stringify(value, null, 2);
    }

    return String(value);
}

console.log = function (...args) {
    originalConsoleLog(...args);

    const message = args.map(formatConsoleValue).join(" ");

    outputElement.textContent += message + "\n";
};

// Кнопка очистки вывода
document.getElementById("clear-output").addEventListener("click", function () {
    outputElement.textContent = "";
});


// ============================================
// Задание 1. Создание массива объектов
// ============================================

const products = [
    {
        id: 1,
        name: "Ноутбук",
        price: 85000,
        category: "Техника",
        available: true,
        rating: 4.8
    },
    {
        id: 2,
        name: "Монитор",
        price: 32000,
        category: "Техника",
        available: false,
        rating: 4.5
    },
    {
        id: 3,
        name: "Клавиатура",
        price: 6500,
        category: "Аксессуары",
        available: true,
        rating: 4.7
    },
    {
        id: 4,
        name: "Мышь",
        price: 2500,
        category: "Аксессуары",
        available: true,
        rating: 4.3
    },
    {
        id: 5,
        name: "Кресло",
        price: 18000,
        category: "Мебель",
        available: false,
        rating: 4.6
    },
    {
        id: 6,
        name: "Стол",
        price: 12000,
        category: "Мебель",
        available: true,
        rating: 4.2
    },
    {
        id: 7,
        name: "Наушники",
        price: 7500,
        category: "Аксессуары",
        available: true,
        rating: 4.9
    }
];


// ============================================
// Задание 2. Вывод каталога
// ============================================

function showProducts(products) {
    products.forEach(product => {
        const availability = product.available
            ? "доступен"
            : "нет в наличии";

        console.log(
            `${product.id}. ${product.name} — ${product.price} руб. — ${product.category} — ${availability}`
        );
    });
}

console.log("Задание 2. Каталог товаров:");
showProducts(products);


// ============================================
// Задание 3. Поиск товара по идентификатору
// ============================================

function findProductById(products, id) {
    const product = products.find(product => product.id === id);

    return product ?? null;
}

console.log("\nЗадание 3. Поиск товара:");

const foundProduct = findProductById(products, 3);
const missingProduct = findProductById(products, 100);

console.log("Поиск существующего товара:", foundProduct);
console.log("Поиск отсутствующего товара:", missingProduct);


// ============================================
// Задание 4. Фильтрация по категории
// ============================================

function getProductsByCategory(products, category) {
    return products.filter(product => product.category === category);
}

console.log("\nЗадание 4. Товары категории «Техника»:");

const techProducts = getProductsByCategory(products, "Техника");
showProducts(techProducts);


// ============================================
// Задание 5. Получение доступных товаров
// ============================================

const availableProducts = products.filter(
    product => product.available === true
);

console.log("\nЗадание 5. Доступные товары:");
console.log("Количество доступных товаров:", availableProducts.length);

showProducts(availableProducts);


// ============================================
// Задание 6. Получение данных для интерфейса
// ============================================

const productCards = products.map(
    product => `${product.name} — ${product.price} руб.`
);

console.log("\nЗадание 6. Подписи карточек товаров:");
console.log(productCards);


// ============================================
// Задание 7. Вычисление средней цены
// ============================================

function getAveragePrice(products) {
    if (products.length === 0) {
        return 0;
    }

    const totalPrice = products.reduce(
        (sum, product) => sum + product.price,
        0
    );

    return totalPrice / products.length;
}

console.log("\nЗадание 7. Средняя цена:");

const averagePrice = getAveragePrice(products);

console.log("Средняя цена товаров:", averagePrice.toFixed(2), "руб.");
console.log("Средняя цена пустого массива:", getAveragePrice([]));


// ============================================
// Задание 8. Изменение доступности товара
// ============================================

function toggleAvailability(products, id) {
    const product = products.find(product => product.id === id);

    if (!product) {
        return null;
    }

    product.available = !product.available;

    return product;
}

console.log("\nЗадание 8. Изменение доступности товара:");

const changedProduct = toggleAvailability(products, 2);

if (changedProduct) {
    console.log("Изменённый товар:");
    showProducts([changedProduct]);
} else {
    console.log("Товар не найден.");
}

console.log("\nИтоговый каталог:");
showProducts(products);