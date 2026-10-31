// ============================================
// Задание 1. Класс User
// ============================================

{
    class User {
        constructor(name, age) {
            this.name = name;
            this.age = age;
        }

        showInfo() {
            return `Имя: ${this.name}, возраст: ${this.age}`;
        }
    }

    const user1 = new User("Александр", 21);
    const user2 = new User("Мария", 22);

    console.log("Задание 1. Пользователи:");
    console.log(user1.showInfo());
    console.log(user2.showInfo());
}


// ============================================
// Задание 2. Класс Counter
// ============================================

{
    class Counter {
        constructor() {
            this.value = 0;
        }

        increment() {
            this.value++;
        }

        decrement() {
            this.value--;
        }

        reset() {
            this.value = 0;
        }
    }

    const counter = new Counter();

    console.log("\nЗадание 2. Счётчик:");

    counter.increment();
    counter.increment();
    console.log("После двух увеличений:", counter.value);

    counter.decrement();
    console.log("После уменьшения:", counter.value);

    counter.reset();
    console.log("После сброса:", counter.value);
}


// ============================================
// Задания 3, 4 и 5. Класс Product
// ============================================

{
    class Product {
        constructor(name, price) {
            this.name = name;
            this.price = price;
        }

        get price() {
            return this._price;
        }

        set price(value) {
            if (value < 0) {
                console.log("Ошибка: цена не может быть отрицательной");
                return;
            }

            this._price = value;
        }

        get info() {
            return `${this.name} — ${this.price} руб.`;
        }

        static compare(product1, product2) {
            if (product1.price === product2.price) {
                return "Товары имеют одинаковую цену";
            }

            return product1.price > product2.price
                ? product1.name
                : product2.name;
        }
    }

    const monitor = new Product("Монитор", 32000);
    const mouse = new Product("Мышь", 1500);
    const keyboard = new Product("Клавиатура", 4000);

    console.log("\nЗадание 3. Информация о товарах:");
    console.log(monitor.info);
    console.log(mouse.info);
    console.log(keyboard.info);

    console.log("\nЗадание 4. Проверка цены:");

    monitor.price = 35000;
    console.log("Новая цена:", monitor.price);

    monitor.price = -500;
    console.log("Цена после попытки установить отрицательное значение:", monitor.price);

    console.log("\nЗадание 5. Сравнение товаров:");
    console.log("Более дорогой товар:", Product.compare(mouse, keyboard));
}


// ============================================
// Задания 6 и 7. Наследование и instanceof
// ============================================

{
    class User {
        constructor(name) {
            this.name = name;
        }

        showRole() {
            return "Пользователь";
        }
    }

    class Admin extends User {
        deleteUser() {
            return "Пользователь удалён";
        }

        showRole() {
            return "Администратор";
        }
    }

    const user = new User("Александр");
    const admin = new Admin("Мария");

    console.log("\nЗадание 6. Наследование:");

    console.log(`${user.name}: ${user.showRole()}`);
    console.log(`${admin.name}: ${admin.showRole()}`);
    console.log(admin.deleteUser());

    console.log("\nЗадание 7. Проверка instanceof:");

    console.log("admin instanceof Admin:", admin instanceof Admin);
    console.log("admin instanceof User:", admin instanceof User);
    console.log("user instanceof Admin:", user instanceof Admin);
    console.log("user instanceof User:", user instanceof User);
}


// ============================================
// Задание 8. Класс Button
// ============================================

{
    class Button {
        constructor(text) {
            this.text = text;
            this.isActive = true;
            this.clickCount = 0;
        }

        click() {
            if (this.isActive) {
                this.clickCount++;
            }
        }

        disable() {
            this.isActive = false;
        }

        enable() {
            this.isActive = true;
        }

        showInfo() {
            const state = this.isActive ? "активна" : "неактивна";

            return `Кнопка: ${this.text}
Состояние: ${state}
Количество нажатий: ${this.clickCount}`;
        }
    }

    const button = new Button("Сохранить");

    console.log("\nЗадание 8. Работа кнопки:");

    button.click();
    button.click();
    button.click();

    button.disable();
    button.click();

    button.enable();
    button.click();

    console.log(button.showInfo());
}