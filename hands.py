import random
from datetime import datetime, timedelta

class Bus:
    def __init__(self, bus_number, capacity):
        self.bus_number = bus_number
        self.capacity = capacity
        self.current_load = 0

    def pickup_passengers(self, waiting_passengers):
        passengers_to_pickup = min(waiting_passengers, self.capacity - self.current_load)
        self.current_load += passengers_to_pickup
        return passengers_to_pickup

    def drop_off_passengers(self, is_final_stop):
        if is_final_stop:
            passengers_to_drop = self.current_load  # Высаживаем всех
            self.current_load = 0  # Все пассажиры выходят
        else:
            if random.random() < 0.6:  # 60% вероятность высадки
                passengers_to_drop = random.randint(0, self.current_load)
                self.current_load -= passengers_to_drop
            else:
                passengers_to_drop = 0
        return passengers_to_drop


class BusStop:
    def __init__(self, name):
        self.name = name
        self.waiting_passengers = random.randint(0, 66)

    def update_waiting_passengers(self, current_time):
        # Добавляем пассажиров в зависимости от времени суток
        if 7 <= current_time.hour < 9 or 17 <= current_time.hour < 19:
            new_passengers = random.randint(5, 22)
        elif 9 <= current_time.hour < 17:
            new_passengers = random.randint(2, 12)
        else:
            new_passengers = random.randint(0, 7)
        self.waiting_passengers += new_passengers
        self.waiting_passengers = max(0, self.waiting_passengers)


class Driver:
    def __init__(self, name, driver_type, schedule, start_day=None):
        self.name = name
        self.driver_type = driver_type
        self.schedule = schedule
        self.has_taken_break = False
        self.is_on_break = False
        self.break_start_time = None
        self.day_counter = 0
        self.start_day = start_day  # День начала работы для водителей второго типа
        self.shift_ended = False  # Новый флаг для отслеживания завершения смены

    def is_working(self, current_time):
        weekday = current_time.weekday()
        if weekday >= len(self.schedule) or self.schedule[weekday] is None:
            return False
        start_time, end_time = self.schedule[weekday]
        return start_time <= current_time.time() <= end_time

    def can_drive(self, current_time):
        # Для водителей второго типа проверяем цикл через 3 дня
        if self.driver_type == 2:
            if self.start_day is not None:
                days_since_start = (current_time.date() - self.start_day).days
                if days_since_start < 0 or (days_since_start % 3) != 0:
                    return False
        return self.is_working(current_time) and not self.is_on_break

    def start_break(self, current_time):
        self.is_on_break = True
        self.break_start_time = current_time

    def end_break(self, current_time):
        if self.is_on_break:
            break_duration = 60 if self.driver_type == 1 else 15
            if current_time >= self.break_start_time + timedelta(minutes=break_duration):
                self.is_on_break = False
                print(f"Водитель {self.name} завершил {'обеденный' if self.driver_type == 1 else '15-ти минутный'} перерыв.\n")
                self.break_start_time = None

    def check_end_of_shift(self, current_time):
        weekday = current_time.weekday()
        if weekday >= len(self.schedule) or self.schedule[weekday] is None:
            return

        _, end_time = self.schedule[weekday]
        if current_time.time() >= end_time and self.is_working(current_time) and not self.shift_ended:
            self.shift_ended = True  # Устанавливаем флаг завершения смены
            print(f"Водитель {self.name} завершил смену в {current_time.strftime('%H:%M')}.\n")
        elif current_time.time() < end_time:
            self.shift_ended = False  # Смена еще не завершена, сбрасываем флаг


class BusSchedule:
    def __init__(self):
        self.schedule = {}

    def add_entry(self, stop_name, bus_number, driver_name, arrival_time, waiting_passengers, picked_up, dropped_off):
        date_key = arrival_time.date()  # Получаем дату прибытия
        if date_key not in self.schedule:
            self.schedule[date_key] = {}  # Создаем новый словарь для даты
        if stop_name not in self.schedule[date_key]:
            self.schedule[date_key][stop_name] = []
        self.schedule[date_key][stop_name].append({
            "bus_number": bus_number,
            "driver_name": driver_name,
            "arrival_time": arrival_time.strftime('%H:%M'),
            "waiting_passengers": waiting_passengers,
            "picked_up": picked_up,
            "dropped_off": dropped_off
        })

    def print_schedule(self):
        print("\n--- Расписание автобусов по остановкам ---")
        for date_key, stops in self.schedule.items():
            weekday_name = get_weekday_name(date_key)
            print(f"\nДата: {date_key}, {weekday_name}")
            for stop_name, entries in stops.items():
                print(f"Остановка: {stop_name}:")
                for entry in entries:
                    print(f"  Время: {entry['arrival_time']} - Автобус: {entry['bus_number']}.")



def travel_time(current_time):
    if 7 <= current_time.hour < 9 or 17 <= current_time.hour < 19:  # Пиковые часы
        return random.randint(10, 11)  # Утро
    elif 9 <= current_time.hour < 17:  # Дневные часы
        return random.randint(11, 12)  # Днем
    else:
        return random.randint(12, 13)  # Ночью


def get_weekday_name(date):
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    return weekdays[date.weekday()]


def simulate_buses(print_schedule=True):
    # Создание остановок
    bus_stops = [BusStop(f"Stop {chr(65 + i)}") for i in range(8)]
    buses = [Bus(f"{100 + i}", 26) for i in range(8)]

    # Расписание водителей
    driver_schedules = [
        # Первый тип
        [(datetime.strptime("07:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time())] * 5 + [None, None],
        [(datetime.strptime("07:15", "%H:%M").time(), datetime.strptime("16:15", "%H:%M").time())] * 5 + [None, None],
        [(datetime.strptime("07:30", "%H:%M").time(), datetime.strptime("16:30", "%H:%M").time())] * 5 + [None, None],
        [(datetime.strptime("10:00", "%H:%M").time(), datetime.strptime("19:00", "%H:%M").time())] * 5 + [None, None],
        [(datetime.strptime("10:15", "%H:%M").time(), datetime.strptime("19:15", "%H:%M").time())] * 5 + [None, None],
        [(datetime.strptime("10:30", "%H:%M").time(), datetime.strptime("19:30", "%H:%M").time())] * 5 + [None, None],
        # Второй тип
        [
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
            (datetime.strptime("12:00", "%H:%M").time(), datetime.strptime("23:59", "%H:%M").time()),
        ],
        [
            (datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
            (datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
            (datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
            (datetime.strptime("02:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
            (datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
            (datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
            (datetime.strptime("06:00", "%H:%M").time(), datetime.strptime("18:00", "%H:%M").time()),
        ],
    ]

    # Задаем стартовые дни для водителей второго типа
    start_days = [
        datetime(2024, 12, 16).date(),  # Водитель 7
        datetime(2024, 12, 18).date(),  # Водитель 8
    ]

    drivers = []
    for i in range(8):
        if i < 6:
            drivers.append(Driver(f"Кентик {i + 1}", 1, driver_schedules[i]))
        else:
            drivers.append(Driver(f"Кентик {i + 1}", 2, driver_schedules[i], start_days[i - 6]))

    # Время отправления первого автобуса
    current_time = datetime(2024, 12, 16, 7, 0)
    simulation_end_time = datetime(2024, 12, 23, 23, 59)  # Симуляция на два дня

    # Время отправления автобусов с интервалом 15 минут
    bus_schedule = [current_time + timedelta(minutes=15 * i) for i in range(len(buses))]
    bus_positions = [0] * len(buses)  # Индексы текущих остановок для каждого автобуса

    # Статистика
    total_passengers_transported = 0
    total_bus_load = 0
    total_bus_trips = 0
    schedule_tracker = BusSchedule()
    while current_time < simulation_end_time:
        # Сброс обеденного флага в начале нового дня
        if current_time.time() == datetime.strptime("00:00", "%H:%M").time():
            for driver in drivers:
                if driver.driver_type == 1:
                    driver.has_taken_break = False

        for i, bus in enumerate(buses):
            driver = drivers[i]

            driver.check_end_of_shift(current_time)

            # Проверяем, работает ли водитель и может ли он управлять автобусом
            if not driver.can_drive(current_time):
                # Если водитель на перерыве, проверяем, не пришло ли время возвращаться
              if driver.is_on_break:
                  driver.end_break(current_time)  # Проверяем, закончил ли водителю обед
              continue

            # Проверяем, наступило ли время отправления автобуса
            if current_time >= bus_schedule[i]:
                current_stop_index = bus_positions[i]
                stop = bus_stops[current_stop_index]


                # Обновляем ожидающих пассажиров
                stop.update_waiting_passengers(current_time)

                # Высадка и посадка пассажиров
                is_final_stop = (current_stop_index == len(bus_stops) - 1)
                dropped_off = bus.drop_off_passengers(is_final_stop)
                picked_up = bus.pickup_passengers(stop.waiting_passengers)
                stop.waiting_passengers -= picked_up

                # Обновление статистики
                total_passengers_transported += dropped_off
                total_bus_load += bus.current_load
                total_bus_trips += 1
                # Добавьте это перед печатью информации о прибытии автобуса
                schedule_tracker.add_entry(stop.name, bus.bus_number, driver.name, current_time, stop.waiting_passengers, picked_up, dropped_off)

                # Форматируем вывод
                weekday_name = get_weekday_name(current_time)
                print(f"{current_time.strftime('%Y-%m-%d')}, {weekday_name}, "
                      f"[{current_time.strftime('%H:%M')}] Автобус {bus.bus_number} под управлением {driver.name} "
                      f"прибывает на '{stop.name}' (Ожидающих: {stop.waiting_passengers + picked_up})")
                print(f"Высажено {dropped_off} пассажиров. Подобрано {picked_up} пассажиров. "
                      f"Текущая загрузка: {bus.current_load}/{bus.capacity}\n")

                # Проверяем обеденный перерыв (только для первого типа водителей)
                if is_final_stop and driver.driver_type == 1 and not driver.has_taken_break and not driver.is_on_break:
                    if datetime.strptime("13:00", "%H:%M").time() <= current_time.time() < datetime.strptime("15:00", "%H:%M").time():
                        driver.start_break(current_time)  # Начинаем обеденный перерыв
                        driver.has_taken_break = True  # Устанавливаем флаг об обеде
                        print(f"Водитель {driver.name} отправился на обеденный перерыв на конечной станции.\n")
                        bus_schedule[i] += timedelta(minutes=60)  # Учитываем часовой перерыв

                if is_final_stop and driver.driver_type == 2 and not driver.is_on_break:
                    driver.start_break(current_time)  # Начинаем 15-ти минутный перерыв
                    print(f"Водитель {driver.name} отправился на 15-ти минутный перерыв на конечной станции.\n")
                    bus_schedule[i] += timedelta(minutes=15)  # Учитываем 15-минутный перерыв

                # Переход к следующей остановке
                bus_positions[i] = (bus_positions[i] + 1) % len(bus_stops)
                bus_schedule[i] += timedelta(minutes=travel_time(current_time))


        current_time += timedelta(minutes=1)  # Увеличиваем время симуляции

    # Вывод общей статистики
    print("\n--- Итоги симуляции ---")
    print(f"Общее количество перевезенных пассажиров: {total_passengers_transported}")
    print(f"Средняя загрузка автобусов: {total_bus_load / total_bus_trips:.2f} пассажиров за поездку")
     # Подсчёт недовольных пассажиров
    total_remaining_passengers = sum(stop.waiting_passengers for stop in bus_stops)
    print(f"Общее количество недовольных пассажиров на всех остановках: {total_remaining_passengers}")
    print("Количество недовольных пассажиров на каждой остановке:")
    for stop in bus_stops:
        print(f"  {stop.name}: {stop.waiting_passengers} пассажиров")
    #Выводим расписание автобусов
    #schedule_tracker.print_schedule(current_time)
    if print_schedule:
        schedule_tracker.print_schedule()
# Запуск симуляции
simulate_buses(print_schedule=False)