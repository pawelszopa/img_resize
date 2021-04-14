import threading


# aby uzyc multithreading

# def do_some_work(val):
#     print("do some work on thread")
#     print(f"echo: {val}")
#     return
#
#
# # to w jaki sposob uruchomimy funkcje w mulithreading hjest ta esencja
#
# value = 'text'
#
# # tworzymy nowego threada
# # thread ma 6 parametrow, name, args, kwargs, demon, target.
# t = threading.Thread(target=do_some_work, args=(value, ))
# # start uruchamia threada
# t.start()
# # join blokuje glownego threada aby ten mogl sie odpalic
# t.join()


# class FibonacciThread(threading.Thread):
#     def __init__(self, num):
#         # wywolujemy inita z klasy thread
#         super().__init__()
#         self.num = num
#
#     def run(self):
#         fib = [0] * (self.num + 1)
#         fib[0] = 0
#         fib[1] = 1
#         for i in range(2, self.num + 1):
#             fib[i] = fib[i - 1] + fib[i - 2]
#             print(fib[self.num])
#
#
# myFibTask1 = FibonacciThread(9)
# myFibTask2 = FibonacciThread(12)
#
# myFibTask1.start()
# myFibTask2.start()
#
# myFibTask1.join()
# myFibTask2.join()
#
# print('lol')


# thread interference
class BankAccount:
    def __init__(self):
        self.balance = 0

    def deposit(self, amount):
        balance = self.balance
        self.balance = balance + amount

    def withdraw(self, amount):
        balance = self.balance
        self.balance = balance - amount


b = BankAccount()
t1 = threading.Thread(target=b.deposit, args=(100,))
t2 = threading.Thread(target=b.withdraw, args=(50,))

t1.start()
t2.start()
t1.join()
t2.join()
print(b.balance)
