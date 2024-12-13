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

def generate_random_time(hour_start, hour_end):
    """
    Генерирует случайное время в заданном диапазоне часов с минутами из 00, 15, 30, 45.
    """
    hour = random.randint(hour_start, hour_end)
    minute = random.choice([0, 15, 30, 45])
    return datetime.strptime(f"{hour}:{minute:02}", "%H:%M").time()

class GeneticAlgorithm:
    def __init__(self, population_size, generations, mutation_rate):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def initialize_population(self):
        """Создаёт начальную популяцию расписаний."""
        population = []
        for _ in range(self.population_size):
            schedule = self.generate_random_schedule()
            population.append(schedule)
        return population

    def generate_random_schedule(self):
        """Создаёт случайное расписание для водителей."""
        drivers = []
        num_drivers_type1 = random.randint(0, 7)
        num_drivers_type2 = 8 - num_drivers_type1

        # Генерация расписаний для водителей 1 типа
        for i in range(num_drivers_type1):
            start_time = generate_random_time(7, 12)
            end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=9)).time()
            schedule = [(start_time, end_time)] * 5 + [None, None]
            drivers.append(Driver(f"Кентик {i + 1}", 1, schedule))

        # Генерация расписаний для водителей 2 типа
        for i in range(num_drivers_type2):
            start_time = generate_random_time(0, 11)
            end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=12)).time()
            schedule = [(start_time, end_time)] * 7
            start_day = datetime(2024, 12, random.randint(16, 23)).date()
            drivers.append(Driver(f"Кентик {num_drivers_type1 + i + 1}", 2, schedule, start_day))

        return drivers

    def fitness(self, schedule):
        """Вычисляет общее количество перевезённых пассажиров для данного расписания."""
        total_passengers_transported = 0

        def simulate_with_schedule(schedule):
            nonlocal total_passengers_transported
            bus_stops = [BusStop(f"Stop {chr(65 + i)}") for i in range(8)]  # Создаём остановки
            buses = [Bus(f"{100 + i}", 26) for i in range(len(schedule))]   # Создаём автобусы
            current_time = datetime(2024, 12, 16, 7, 0)                     # Начало симуляции
            simulation_end_time = datetime(2024, 12, 23, 23, 59)            # Конец симуляции
            bus_positions = [0] * len(buses)                                # Позиции автобусов
            bus_schedule = [current_time] * len(buses)                      # Время прибытия

            while current_time < simulation_end_time:
                for i, bus in enumerate(buses):
                    driver = schedule[i]
                    if not driver.can_drive(current_time):
                        if driver.is_on_break:
                            driver.end_break(current_time)
                        continue

                    if current_time >= bus_schedule[i]:
                        current_stop_index = bus_positions[i]
                        is_final_stop = (current_stop_index == len(bus_stops) - 1)
                        stop = bus_stops[current_stop_index]

                        # Обновляем пассажиров на остановке
                        stop.update_waiting_passengers(current_time)

                        # Высадка и посадка пассажиров
                        dropped_off = bus.drop_off_passengers(is_final_stop)
                        picked_up = bus.pickup_passengers(stop.waiting_passengers)
                        stop.waiting_passengers -= picked_up

                        # Обновляем общее число перевезённых пассажиров
                        total_passengers_transported += dropped_off

                        # Проверяем начало перерыва
                        if is_final_stop and driver.driver_type == 1 and not driver.has_taken_break and not driver.is_on_break:
                          if datetime.strptime("13:00", "%H:%M").time() <= current_time.time() < datetime.strptime("15:00", "%H:%M").time():
                            driver.start_break(current_time)  # Начинаем обеденный перерыв
                            driver.has_taken_break = True  # Устанавливаем флаг об обеде
                            bus_schedule[i] += timedelta(minutes=60)  # Учитываем часовой перерыв

                        if is_final_stop and driver.driver_type == 2 and not driver.is_on_break:
                          driver.start_break(current_time)  # Начинаем 15-ти минутный перерыв
                          bus_schedule[i] += timedelta(minutes=15)  # Учитываем 15-минутный перерыв

                        # Переходим к следующей остановке
                        bus_positions[i] = (bus_positions[i] + 1) % len(bus_stops)

                        # Рассчитываем время прибытия на следующую остановку
                        bus_schedule[i] += timedelta(minutes=travel_time(current_time))

                # Переход на минуту вперёд
                current_time += timedelta(minutes=1)

        simulate_with_schedule(schedule)
        return total_passengers_transported


    def crossover(self, parent1, parent2):
        """Кроссовер двух расписаний."""
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def mutate(self, schedule):
        """Мутация расписания."""
        if random.random() < self.mutation_rate:
            driver_to_mutate = random.choice(schedule)
            if driver_to_mutate.driver_type == 1:
                start_time = generate_random_time(7, 12)
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=9)).time()
                driver_to_mutate.schedule = [(start_time, end_time)] * 5 + [None, None]
            else:
                start_time = generate_random_time(0, 11)
                end_time = (datetime.combine(datetime.today(), start_time) + timedelta(hours=12)).time()
                driver_to_mutate.schedule = [(start_time, end_time)] * 7
        return schedule

    def evolve(self):
        """Основной цикл ГА."""
        population = self.initialize_population()
        for generation in range(self.generations):
            population = sorted(population, key=self.fitness, reverse=True)
            best_fitness = self.fitness(population[0])
            print(f"Поколение {generation + 1}: перевезено пассажиров - {best_fitness}")
            new_population = population[:self.population_size // 2]
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(population[:self.population_size // 2], 2)
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([self.mutate(child1), self.mutate(child2)])
            population = new_population
        return max(population, key=self.fitness)

if __name__ == "__main__":
    ga = GeneticAlgorithm(population_size=100, generations=100, mutation_rate=0.1)
    best_schedule = ga.evolve()
    print("Лучшее расписание найдено:")
    unique_schedules = set()

for driver in best_schedule:
  driver_type = "типа 1" if driver.driver_type == 1 else "типа 2"
  for day_schedule in driver.schedule:
    if day_schedule is not None:
      start_time, end_time = day_schedule
      if driver.driver_type == 2 and driver.start_day is not None:
        start_weekday = get_weekday_name(driver.start_day)
        schedule_entry = (
            f"{driver.name} {driver_type} (начало смены {start_time}, конец смены {end_time}, "
            f"начальный день {start_weekday} ({driver.start_day}))")
      else:
        schedule_entry = f"{driver.name} {driver_type} (начало смены {start_time}, конец смены {end_time})"

      if schedule_entry not in unique_schedules:
        unique_schedules.add(schedule_entry)
        print(schedule_entry)
