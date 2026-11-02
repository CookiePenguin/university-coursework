// ============================================
// Задание 2. Базовые типы
// ============================================

const shopName: string = "Digital Store";
const year: number = 2026;
const isOnline: boolean = true;

console.log("Название магазина:", shopName);
console.log("Год:", year);
console.log("Интернет-магазин:", isOnline);

// Переменная может содержать строку или null
let description: string | null = null;

console.log("Описание магазина:", description);

description = "Магазин цифровой техники и аксессуаров";

console.log("Новое описание:", description);

// ============================================
// Задания 3–4. Создание типа Product
// ============================================

type Product = {
    id: number;
    name: string;
    price: number;
    category: ProductCategory;
    inStock: boolean;
    description?: string;
};

// Создание товаров

const product1: Product = {
    id: 1,
    name: "Ноутбук",
    price: 85000,
    category: "computers",
    inStock: true,
    description: "Игровой ноутбук с мощным процессором"
};

const product2: Product = {
    id: 2,
    name: "Смартфон",
    price: 45000,
    category: "phones",
    inStock: true
};

const product3: Product = {
    id: 3,
    name: "Наушники",
    price: 5000,
    category: "accessories",
    inStock: false
};

// Объединение товаров в массив

const products: Product[] = [
    product1,
    product2,
    product3
];

// Вывод товаров

console.log("\nСписок товаров:");

products.forEach((product) => {
    console.log("Товар:", product.name);
    console.log("Цена:", product.price, "руб.");
    console.log("Описание:", product.description ?? "Описание отсутствует");
});

// ============================================
// Задание 5. Literal и Union-типы
// ============================================

type ProductCategory =
    | "computers"
    | "phones"
    | "accessories";

// ============================================
// Задание 6. Функция вывода товара
// ============================================

function printProduct(product: Product): void {
    console.log("\nИнформация о товаре:");
    console.log("Товар:", product.name);
    console.log("Цена:", product.price, "руб.");
    console.log("Категория:", product.category);
    console.log("В наличии:", product.inStock ? "да" : "нет");

    if (product.description) {
        console.log("Описание:", product.description);
    }
}

// Вывод информации обо всех товарах

console.log("\n========== ЗАДАНИЕ 6 ==========");

products.forEach(printProduct);


// ============================================
// Задание 7. Функция поиска товара
// ============================================

function findProductById(
    products: Product[],
    id: number
): Product | undefined {
    return products.find((product) => product.id === id);
}

console.log("\n========== ЗАДАНИЕ 7 ==========");

const result = findProductById(products, 2);

if (result) {
    console.log("Найден товар:", result.name);
} else {
    console.log("Товар не найден");
}


// ============================================
// Задание 8. Фильтрация доступных товаров
// ============================================

function getAvailableProducts(
    products: Product[]
): Product[] {
    return products.filter((product) => product.inStock === true);
}

console.log("\n========== ЗАДАНИЕ 8 ==========");

const availableProducts = getAvailableProducts(products);

console.log("Доступные товары:");

availableProducts.forEach((product) => {
    console.log(product.name);
});


// ============================================
// Задание 9. Фильтрация товаров по цене
// ============================================

function getProductsByMaxPrice(
    products: Product[],
    maxPrice: number
): Product[] {
    return products.filter((product) => product.price <= maxPrice);
}

console.log("\n========== ЗАДАНИЕ 9 ==========");

const affordableProducts = getProductsByMaxPrice(products, 50000);

console.log("Товары стоимостью не более 50000 руб.:");

affordableProducts.forEach((product) => {
    console.log(product.name, "-", product.price, "руб.");
});

// ============================================
// Задание 10. Interface
// ============================================

type UserRole =
    | "admin"
    | "manager"
    | "customer";

interface User {
    id: number;
    name: string;
    email: string;
    role: UserRole;
}

// Создание пользователей

const admin: User = {
    id: 1,
    name: "Анна",
    email: "anna@example.com",
    role: "admin"
};

const manager: User = {
    id: 2,
    name: "Иван",
    email: "ivan@example.com",
    role: "manager"
};

const customer: User = {
    id: 3,
    name: "Мария",
    email: "maria@example.com",
    role: "customer"
};

const users: User[] = [
    admin,
    manager,
    customer
];

console.log("\n========== ЗАДАНИЕ 10 ==========");
console.log("Пользователи магазина:");

users.forEach((user) => {
    console.log(
        `${user.name} | ${user.email} | Роль: ${user.role}`
    );
});


// ============================================
// Задание 11. Расширение интерфейса
// ============================================

interface Admin extends User {
    permissions: string[];
}

const administrator: Admin = {
    id: 4,
    name: "Алексей",
    email: "alex@example.com",
    role: "admin",
    permissions: [
        "create",
        "edit",
        "delete"
    ]
};

console.log("\n========== ЗАДАНИЕ 11 ==========");
console.log("Администратор:");
console.log("Имя:", administrator.name);
console.log("Email:", administrator.email);
console.log("Роль:", administrator.role);
console.log("Права доступа:", administrator.permissions);


// ============================================
// Задание 12. DTO
// ============================================

interface CreateProductDto {
    name: string;
    price: number;
    category: ProductCategory;
}

const newProduct: CreateProductDto = {
    name: "Монитор",
    price: 32000,
    category: "computers"
};

console.log("\n========== ЗАДАНИЕ 12 ==========");
console.log("Данные нового товара:");
console.log("Название:", newProduct.name);
console.log("Цена:", newProduct.price, "руб.");
console.log("Категория:", newProduct.category);