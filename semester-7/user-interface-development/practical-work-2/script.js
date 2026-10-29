console.log("=== Практическая работа № 2: Функции ===");

// Задание 1. Обычная функция
function calculateRectangleArea(width, height) {
    return width * height;
}

console.log("\nЗадание 1. Площадь прямоугольника:");
console.log("Ширина: 5, высота: 10");
console.log("Площадь:", calculateRectangleArea(5, 10));


// Задание 2. Function Expression
const average = function(a, b, c) {
    return (a + b + c) / 3;
};

console.log("\nЗадание 2. Среднее значение (Function Expression):");
console.log("Числа: 10, 20, 30");
console.log("Среднее значение:", average(10, 20, 30));


// Задание 3. Стрелочная функция
const averageArrow = (a, b, c) => {
    return (a + b + c) / 3;
};

console.log("\nЗадание 3. Среднее значение (стрелочная функция):");
console.log("Числа: 15, 25, 35");
console.log("Среднее значение:", averageArrow(15, 25, 35));


// Задание 4. Параметр по умолчанию
function greet(name = "Пользователь") {
    return `Привет, ${name}!`;
}

console.log("\nЗадание 4. Приветствие:");
console.log(greet("Иван"));
console.log(greet());


// Задание 5. Произвольное количество аргументов
function sum(...numbers) {
    return numbers.reduce((total, number) => total + number, 0);
}

console.log("\nЗадание 5. Сумма произвольного количества чисел:");
console.log("Сумма чисел 1, 2, 3:", sum(1, 2, 3));
console.log("Сумма чисел 10, 20, 30, 40:", sum(10, 20, 30, 40));
console.log("Сумма без аргументов:", sum());

console.log("\n=== Конец практической работы № 2 ===");