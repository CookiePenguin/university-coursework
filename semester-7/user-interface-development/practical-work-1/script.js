// ==========================================
// ПЗ № 1. Основы JavaScript
// ==========================================


// ==========================================
// ЗАДАНИЕ 1. Типы данных и арифметика
// ==========================================

console.log("========== ЗАДАНИЕ 1 ==========");

let a = 10;
let b = 30;

console.log("Начальное a:", a);
console.log("Начальное b:", b);

a = 8;
const c = a ** b;

console.log("Изменённое a:", a);
console.log("c = a ** b:", c);

console.log("Тип a:", typeof a);
console.log("Тип b:", typeof b);
console.log("Тип c:", typeof c);

a = String(a);
console.log("a как строка:", a, "| Тип:", typeof a);

a = Number(a);
console.log("a как число:", a, "| Тип:", typeof a);

console.log("Сложение:", a + b);
console.log("Вычитание:", a - b);
console.log("Умножение:", a * b);
console.log("Деление:", b / a);

b -= 6.8;

console.log("b после вычитания 6.8:", b);
console.log("Модуль b:", Math.abs(b));
console.log("Целая часть b / a:", Math.trunc(b / a));
console.log("Остаток b % a:", b % a);
console.log("Остаток после округления:", Math.round(b % a));

console.log("Максимум:", Math.max(a, b, c));
console.log("Минимум:", Math.min(a, b, c));

const sum = 0.1 + 0.2;

console.log("0.1 + 0.2 =", sum);
console.log("Сумма строго равна 0.3:", sum === 0.3);

const bigNumber = 9007199254740993n;
const bigResult = bigNumber + 10n;

console.log("Большое число:", bigNumber);
console.log("Большое число + 10n:", bigResult);
console.log("Тип большого числа:", typeof bigNumber);

try {
    console.log(bigNumber + 10);
} catch (error) {
    console.log("Ошибка сложения BigInt и number:", error.message);
}


// ==========================================
// ЗАДАНИЕ 2. Работа со строками
// ==========================================

console.log("\n========== ЗАДАНИЕ 2 ==========");

const d = " My name is ";

console.log("Исходная строка:", d);
console.log("После trim():", d.trim());

const trimmed = d.trim();

// Замени пример ФИО на свои данные
const surname = "Иванов";
const fullName = `${trimmed} Иванов Иван Иванович`;

console.log("Строка с ФИО:", fullName);
console.log("Длина строки:", fullName.length);

console.log("Текст в две строки:\nMy name\nis Иванов Иван Иванович");

console.log(
    "Слова через табуляцию:",
    fullName.trim().split(" ").join("\t")
);

console.log("Повторение строки:\n" + (fullName + "\n").repeat(3));

console.log("В верхнем регистре:", fullName.toUpperCase());
console.log("Слово NAME:", fullName.toUpperCase().substring(3, 7));

console.log('Содержит "name":', fullName.includes("name"));
console.log('Содержит "JavaScript":', fullName.includes("JavaScript"));

console.log("Первая буква фамилии:", surname[0]);
console.log("Замена name:", fullName.replace("name", "****"));
console.log("Позиция буквы y:", fullName.indexOf("y"));


// ==========================================
// ЗАДАНИЕ 3. Условные операторы
// ==========================================

console.log("\n========== ЗАДАНИЕ 3 ==========");

// Оценка по количеству баллов

const score = 87;

if (score < 0 || score > 100) {
    console.log("Некорректное значение");
} else if (score >= 85) {
    console.log("Оценка: отлично");
} else if (score >= 70) {
    console.log("Оценка: хорошо");
} else if (score >= 60) {
    console.log("Оценка: удовлетворительно");
} else {
    console.log("Оценка: неудовлетворительно");
}


// Проверка роли пользователя

const role = "student";

switch (role) {
    case "admin":
        console.log("Полный доступ");
        break;

    case "teacher":
        console.log("Редактирование учебных материалов");
        break;

    case "student":
        console.log("Просмотр и выполнение заданий");
        break;

    default:
        console.log("Доступ не определён");
}

// Сравнение == и ===

console.log("0 == false:", 0 == false);
console.log("0 === false:", 0 === false);

console.log('"5" == 5:', "5" == 5);
console.log('"5" === 5:', "5" === 5);


// ==========================================
// ЗАДАНИЕ 4. Циклы
// ==========================================

console.log("\n========== ЗАДАНИЕ 4 ==========");

// Цикл for: числа от 1 до 10

console.log("Числа от 1 до 10:");

for (let i = 1; i <= 10; i++) {
    console.log(i);
}


// Цикл while: сумма чисел от 1 до 100

let number = 1;
let total = 0;

while (number <= 100) {
    total += number;
    number++;
}

console.log("Сумма чисел от 1 до 100:", total);


// Цикл do...while: обратный отсчёт

console.log("Обратный отсчёт:");

let countdown = 5;

do {
    console.log(countdown);
    countdown--;
} while (countdown >= 1);


// Чётные числа от 2 до 20

console.log("Чётные числа от 2 до 20:");

for (let i = 2; i <= 20; i += 2) {
    console.log(i);
}


// continue: пропуск чисел, кратных трём

console.log("Числа от 1 до 20, кроме кратных трём:");

for (let i = 1; i <= 20; i++) {
    if (i % 3 === 0) {
        continue;
    }

    console.log(i);
}


// break: первое число больше 50, кратное семи

console.log("Первое число больше 50, кратное семи:");

for (let i = 51; i <= 100; i++) {
    if (i % 7 === 0) {
        console.log(i);
        break;
    }
}


// for...of: перебор символов строки

console.log("Символы слова JavaScript:");

for (const char of "JavaScript") {
    console.log(char);
}


// Дополнительное задание: таблица умножения

console.log("Таблицы умножения от 1 до 10:");

for (let i = 1; i <= 10; i++) {
    console.log(`Таблица умножения на ${i}:`);

    for (let j = 1; j <= 10; j++) {
        console.log(`${i} * ${j} = ${i * j}`);
    }
}

console.log("\n========== КОНЕЦ ПЗ № 1 ==========");