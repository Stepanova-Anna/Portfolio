# Ряд Фибоначчи с помощью итераторов

>Лабораторная работа состоит из двух подзаданий: 
>1. Создание сопрограммы на основе кода, позволяющей по данному n сгенерировать список элементов из ряда Фибоначчи.
>2. Создание программы, возвращающей список чисел Фибоначчи с помощью итератора.

## Решение

- `fib_elem_gen()` - бесконечный генератор, последовательно выдающий числа Фибоначчи
- Декоратор `fib_coroutine` инициализирует сопрограмму
- `my_genn()` - основная сопрограмма, которая принимает число n и возвращает список из n первых чисел Фибоначчи

Реализация с помощью итератора:
```
class FibonacchiLst:
    def __init__(self, lst):
        self.lst = lst
        self.index = 0
        self.max_val = max(lst) if lst else 0
        self.fib_set = self._generate_fib_set(self.max_val)

    def _generate_fib_set(self, max_val):
        """Генерирует множество чисел Фибоначчи до max_val"""
        a, b = 0, 1
        fib_numbers = {a}
        while b <= max_val:
            fib_numbers.add(b)
            a, b = b, a + b
        return fib_numbers

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.lst):
            elem = self.lst[self.index]
            self.index += 1
            if elem in self.fib_set:
                return elem
        raise StopIteration
```

- Итератор фильтрует элементы входного списка, оставляя только числа Фибоначчи
- При инициализации вычисляется множество чисел Фибоначчи до максимального значения в списке
- Метод `__next__()` последовательно возвращает элементы исходного списка, которые являются числами Фибоначчи

<img width="1753" height="102" alt="image" src="https://github.com/user-attachments/assets/618059d9-e5a8-4e48-961b-7c675fc16325" />


<img width="1769" height="129" alt="image" src="https://github.com/user-attachments/assets/116e1b6c-4b58-4d7f-998c-e1ba0cfb4177" />


<img width="1523" height="504" alt="image" src="https://github.com/user-attachments/assets/7d0754e2-b4b0-455e-a600-4e0485aa9de3" />
