# threading interference (race condition)
threading.Lock() - jezeli thread uzywa zmiennej to on ja blokuje i inny thread nie moze jej uzyc - GIL to robi automatycznie - mozna uzywac jako context managera i ma kilka metod
threading.RLock() - 
threading.Semaphore() - mowimy ile pociagow moze wjechac na tor - np 3 to 3 thready moga uzywac zmiennej
threading.Event() - await - czekac 
threading.;Condition() - w zaleznosci od codition mamy 5 stanow


# recommended:
Queue - trzymamy dane w kolejce i thread moze wziac z konca kolejki
    - put() - dodaje na koniec kolejki
    - get() - pobiera z poczatku 
    - task_done() - oznacza ze dany task zostal zakonczony lub przetworzony
    - join() - blokuje kolejke 

poison pill zatrowamy 