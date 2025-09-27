#!/usr/bin/env python3
"""
Add the real Tres Dias retreat schedule to the Schedule table.
"""

import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appRp7Vby2JMzN0mC")
TABLE_ID = os.getenv("AIRTABLE_SCHEDULE_TABLE_ID", "tblsxihPaZebzyBS2")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_event_type(title, description=""):
    """Determine event type based on title and description."""
    title_lower = title.lower()
    desc_lower = description.lower()

    if any(word in title_lower for word in ['рое', 'roe', '#']):
        return "ROE"
    elif any(word in title_lower for word in ['завтрак', 'обед', 'ужин']):
        return "Meal"
    elif any(word in title_lower for word in ['молитва', 'чэпел', 'chapel', 'благословение']):
        return "Chapel"
    elif any(word in title_lower for word in ['рефрешмент', 'перерыв']):
        return "Break"
    elif any(word in title_lower for word in ['восхваление', 'хвала', 'de colores', 'мананита']):
        return "Prayer"
    elif any(word in title_lower for word in ['обряд', 'крест', 'агапе', 'драма', 'хлебопреломление']):
        return "Celebration"
    elif any(word in title_lower for word in ['собрание', 'заезд', 'отъезд', 'регистрация', 'фото']):
        return "Activity"
    else:
        return "Talk"

def get_audience(title, description=""):
    """Determine audience based on title and description."""
    content = (title + " " + description).lower()

    if any(word in content for word in ['тм', 'тим', 'team']):
        return "Team"
    elif any(word in content for word in ['кандидат']):
        return "Candidates"
    else:
        return "All"

def create_real_schedule():
    """Create the real Tres Dias schedule events."""

    # Day 0 - November 13, 2025 (Thursday) - Подготовительный день
    day0_events = [
        ("09:00", "10:30", "Заезд тим-мемберов", "Приезд и размещение команды", 1),
        ("09:00", "10:30", "Собрание (чэпел)", "Утреннее собрание команды в часовне", 2),
        ("11:00", "12:30", "Проверка всех материалов", "Проверка готовности всех материалов и оборудования", 3),
        ("13:00", "13:30", "Молитва", "Общая молитва перед началом", 4),
        ("13:30", "14:00", "Обед", "Обеденный перерыв", 5),
        ("14:00", "16:00", "Работа в департаментах", "Подготовительная работа по департаментам", 6),
        ("16:00", "17:00", "Фото всех тим-мемберов и готовность к встрече кандидатов", "Групповое фото команды и финальная подготовка", 7),
        ("17:00", "18:00", "Заезд кандидатов, регистрация, фото, размещение", "Регистрация кандидатов, фотографирование, размещение (восхваление в фойе)", 8),
        ("18:00", "18:30", "Ужин", "Приветственный ужин", 9),
        ("18:30", "18:40", "Перерыв", "Короткий перерыв", 10),
        ("18:40", "19:00", "Лекционный зал, восхваление", "Переход в лекционный зал, восхваление", 11),
        ("19:00", "20:30", "Знакомство", "1) представление департаментов, 2) представление кандидатов", 12),
        ("20:30", "20:45", "Ректор: словарь, объяснение", "Выступление ректора, объяснение словаря", 13),
        ("20:45", "21:30", "Духовный лидер", "Выступление духовного лидера", 14),
        ("21:30", "22:00", "Переход в Чэпл (гайд). ОБЕТ МОЛЧАНИЯ", "Переход в часовню под руководством гида. Обет молчания (чтецы, Сын Мой)", 15),
        ("22:00", "22:10", "Рефрешмент (молча) (1)", "Первый рефрешмент в молчании", 16),
        ("22:10", "22:20", "Переход в спальный корпус (гайд). Отбой", "Переход в спальный корпус под руководством гида. Отбой", 17),
        ("22:20", "23:00", "Собрание ТМ", "Собрание тим-мемберов", 18),
    ]

    # Day 1 - November 14, 2025 (Friday) - 1 ДЕНЬ
    day1_events = [
        ("05:30", "06:00", "Подъем ТМ", "Подъем тим-мемберов", 1),
        ("06:00", "06:50", "Молитва ТМ в чэпел", "Утренняя молитва тим-мемберов в часовне", 2),
        ("06:50", "07:10", "Первый звонок", "Первый звонок для кандидатов", 3),
        ("07:10", "08:30", "Второй звонок. Визит в Чэпл", "Второй звонок. Визит в часовню (гайд), разбивается обет молчания. Хвала De Colores – объяснение", 4),
        ("08:30", "09:15", "Завтрак (W-Welcome)", "Завтрак с темой 'Welcome', разминка", 5),
        ("09:15", "09:30", "Перерыв, рефрешмент (2)", "Перерыв и второй рефрешмент", 6),
        ("09:30", "09:45", "Восхваление в лекционном зале", "Восхваление в лекционном зале", 7),
        ("09:45", "10:10", "Формирование семей, знакомство", "Формирование семей, знакомство, выбор названия, рисование плаката", 8),
        ("10:10", "10:40", "Представление плаката", "Представление плакатов семей", 9),
        ("10:40", "10:50", "Восхваление", "Восхваление", 10),
        ("10:50", "11:10", "#1 Рое «Идеал»", "Первое ROE выступление на тему 'Идеал'", 11),
        ("11:10", "11:35", "Обсуждение, рисование", "Обсуждение ROE, рисование плаката", 12),
        ("11:35", "11:50", "Представление плаката", "Представление плаката по ROE", 13),
        ("11:50", "12:00", "Восхваление", "Восхваление", 14),
        ("12:00", "13:00", "#2 Рое «Благодать на благодать»", "Второе ROE выступление на тему 'Благодать на благодать'", 15),
        ("13:00", "13:30", "Молитва покаяния и благословения", "Молитва покаяния и благословения (роерум). De Colores, гайд", 16),
        ("13:30", "14:20", "Обед (G-Благодать, зонт)", "Обед с темой 'Благодать', символ зонта, разминка", 17),
        ("14:20", "14:30", "Рефрешмент (3)", "Третий рефрешмент", 18),
        ("14:30", "14:40", "Восхваление", "Восхваление", 19),
        ("14:40", "15:00", "#3 Рое «Церковь»", "Третье ROE выступление на тему 'Церковь'", 20),
        ("15:00", "15:10", "Восхваление", "Восхваление", 21),
        ("15:10", "15:20", "Паланка (1)", "Первая паланка", 22),
        ("15:20", "15:50", "#4 «Благочестие»", "Четвертое выступление на тему 'Благочестие'", 23),
        ("15:50", "16:00", "Восхваление", "Восхваление", 24),
        ("16:00", "16:10", "Паланка (2)", "Вторая паланка", 25),
        ("16:10", "16:50", "#5 Рое «Святой Дух» (Помощь Бога)", "Пятое ROE выступление на тему 'Святой Дух' (Помощь Бога)", 26),
        ("16:50", "18:00", "Молитва за Святой Дух", "Молитва за Святой Дух. De Colores, гайд", 27),
        ("18:00", "18:40", "Ужин (S-голубь)", "Ужин с символом голубя, разминка", 28),
        ("18:40", "18:50", "Рефрешмент (4)", "Четвертый рефрешмент", 29),
        ("18:50", "19:00", "Восхваление", "Восхваление", 30),
        ("19:00", "19:10", "Паланка (3)", "Третья паланка", 31),
        ("19:10", "20:00", "Восхваление. Хвала по группам", "Восхваление. Хвала по группам", 32),
        ("20:00", "21:00", "Объяснение обряда «Крест»", "Объяснение обряда 'Крест'", 33),
        ("21:00", "21:40", "ОБРЯД КРЕСТ", "Проведение обряда 'Крест'", 34),
        ("21:40", "22:00", "Рефрешмент (5) в корпусе", "Пятый рефрешмент в корпусе", 35),
        ("22:00", "22:30", "Отбой. Собрание ТМ", "Отбой. Собрание тим-мемберов", 36),
    ]

    # Day 2 - November 15, 2025 (Saturday) - 2 ДЕНЬ
    day2_events = [
        ("05:30", "06:00", "Подъем ТМ", "Подъем тим-мемберов", 1),
        ("06:00", "06:30", "Молитва ТМ в чэпел", "Утренняя молитва тим-мемберов в часовне", 2),
        ("06:30", "07:00", "В этот день (первый звонок)", "Первый звонок 'В этот день'", 3),
        ("07:00", "08:30", "Второй звонок, визит в Чэпл", "Второй звонок, визит в часовню. Гайд веселый, в костюмах. De Colores, гайд", 4),
        ("08:30", "09:15", "Завтрак (якорь)", "Завтрак с символом якоря, разминка", 5),
        ("09:15", "09:25", "Рефрешмент (6)", "Шестой рефрешмент", 6),
        ("09:25", "09:35", "Восхваление", "Восхваление", 7),
        ("09:35", "09:40", "Паланка (4)", "Четвертая паланка", 8),
        ("09:40", "10:00", "#6 «Исследование»", "Шестое выступление на тему 'Исследование'", 9),
        ("10:00", "10:10", "Восхваление", "Восхваление", 10),
        ("10:10", "11:10", "#7 «Святые обряды»", "Седьмое выступление на тему 'Святые обряды'", 11),
        ("11:10", "12:10", "ХЛЕБОПРЕЛОМЛЕНИЕ", "Обряд хлебопреломления", 12),
        ("12:10", "13:00", "ОМОВЕНИЕ НОГ", "Обряд омовения ног", 13),
        ("13:00", "13:30", "АБРАЗА", "Обряд Абраза. De Colores, гайд", 14),
        ("13:30", "14:10", "Обед (крест)", "Обед с символом креста. Шуток нет! 'Иисус – это Твоя кровь'. Рыбка", 15),
        ("14:10", "14:30", "Объяснение молитвы по группам", "Объяснение молитвы по группам", 16),
        ("14:30", "15:20", "Молитва по группам (дары Св.Д)", "Молитва по группам (дары Святого Духа)", 17),
        ("15:20", "15:30", "Первый звонок", "Первый звонок", 18),
        ("15:30", "16:10", "Рефрешмент большой (7). Фото", "Большой седьмой рефрешмент. Фото по столам, общее", 19),
        ("16:10", "16:20", "Восхваление", "Восхваление", 20),
        ("16:20", "16:40", "#8 «Жизнь христианина»", "Восьмое выступление на тему 'Жизнь христианина'", 21),
        ("16:40", "16:50", "Паланка (5)", "Пятая паланка", 22),
        ("16:50", "16:55", "Восхваление", "Восхваление", 23),
        ("16:55", "17:30", "#9 «Преграды, мешающие получать благодать»", "Девятое выступление на тему 'Преграды, мешающие получать благодать'", 24),
        ("17:30", "17:35", "Восхваление", "Восхваление", 25),
        ("17:35", "18:00", "#10 «Христианский лидер»", "Десятое выступление на тему 'Христианский лидер'. De Colores, гайд", 26),
        ("18:00", "19:10", "Ужин (сердце)", "Ужин с символом сердца, разминка", 27),
        ("19:10", "19:20", "Рефрешмент (8)", "Восьмой рефрешмент", 28),
        ("19:20", "19:35", "Восхваление в Чэпл", "Восхваление в часовне", 29),
        ("19:35", "20:00", "Подготовка к драме", "Подготовка к драме", 30),
        ("20:00", "21:00", "Драма", "Представление драмы", 31),
        ("21:00", "21:30", "Объяснение обряда Агапе", "Объяснение обряда Агапе", 32),
        ("21:30", "23:00", "АГАПЕ. Карта", "Проведение обряда Агапе. Карта", 33),
        ("23:00", "23:10", "Рефрешмент (9)", "Девятый рефрешмент", 34),
        ("23:10", "", "Отбой", "Отбой, собрания ТМ нет", 35),
    ]

    # Day 3 - November 16, 2025 (Sunday) - 3 ДЕНЬ
    day3_events = [
        ("05:30", "06:00", "Подъем ТМ", "Подъем тим-мемберов", 1),
        ("06:00", "06:30", "Молитва тимов в чэпл", "Утренняя молитва тимов в часовне", 2),
        ("06:30", "07:00", "Первый звонок", "Первый звонок", 3),
        ("07:00", "09:00", "Второй звонок. Визит в Чэпл, МАНАНИТА", "Второй звонок. Визит в часовню, рассаживание по столам (гайд). МАНАНИТА. Все студенты и выпускники Академии", 4),
        ("09:00", "09:40", "Завтрак (круг/бабочка)", "Завтрак с символом круга/бабочки. Сброс шаров. Когда мы вместе", 5),
        ("09:40", "09:50", "Объяснения молитвы по группам", "Объяснения молитвы по группам", 6),
        ("09:50", "10:30", "Молитва по группам (видение)", "Молитва по группам (видение)", 7),
        ("10:40", "11:00", "Первый звонок (Сбор вещей)", "Первый звонок (сбор вещей)", 8),
        ("11:00", "11:10", "Второй звонок (вещи в чэпл)", "Второй звонок (вещи в часовню)", 9),
        ("11:10", "11:30", "Восхваление", "Восхваление", 10),
        ("11:30", "11:50", "#11 «Христианская атмосфера»", "Одиннадцатое выступление на тему 'Христианская атмосфера'", 11),
        ("11:50", "12:00", "Паланка (6,7)", "Шестая и седьмая паланки", 12),
        ("12:00", "12:10", "Восхваление", "Восхваление", 13),
        ("12:10", "12:30", "#12 Рое «Христианская община»", "Двенадцатое ROE выступление на тему 'Христианская община'", 14),
        ("12:30", "12:40", "Восхваление", "Восхваление", 15),
        ("12:40", "13:00", "#13 Рое «Четвертый день»", "Тринадцатое ROE выступление на тему 'Четвертый день'", 16),
        ("13:00", "14:00", "Обед", "Обед. Выбор председателя, объявления", 17),
        ("14:00", "14:30", "ВЫПУСКНОЙ. Гимн ТД", "Выпускной. Гимн Tres Dias", 18),
        ("14:30", "15:00", "#14 «Жизнь в благодати»", "Четырнадцатое выступление на тему 'Жизнь в благодати'", 19),
        ("15:00", "16:30", "Свидетельства", "Время для свидетельств", 20),
        ("16:30", "17:00", "Объявления. Пасторское благословение", "Объявления. Пасторское благословение", 21),
        ("17:00", "", "Отъезд", "Отъезд участников", 22),
    ]

    # Build the complete events list
    all_events = []

    # Process Day 0 (Thursday)
    for start_time, end_time, title, description, order in day0_events:
        event = {
            "fields": {
                "EventTitle": title,
                "EventDate": "2025-11-13",
                "StartTime": start_time,
                "EndTime": end_time if end_time else "",
                "Description": description,
                "Location": "",  # Location not specified in most cases
                "Audience": get_audience(title, description),
                "EventType": get_event_type(title, description),
                "DayTag": "Day 0",
                "Order": order,
                "IsActive": True,
                "IsMandatory": True
            }
        }
        all_events.append(event)

    # Process Day 1 (Friday)
    for start_time, end_time, title, description, order in day1_events:
        event = {
            "fields": {
                "EventTitle": title,
                "EventDate": "2025-11-14",
                "StartTime": start_time,
                "EndTime": end_time if end_time else "",
                "Description": description,
                "Location": "",
                "Audience": get_audience(title, description),
                "EventType": get_event_type(title, description),
                "DayTag": "Day 1",
                "Order": order,
                "IsActive": True,
                "IsMandatory": True
            }
        }
        all_events.append(event)

    # Process Day 2 (Saturday)
    for start_time, end_time, title, description, order in day2_events:
        event = {
            "fields": {
                "EventTitle": title,
                "EventDate": "2025-11-15",
                "StartTime": start_time,
                "EndTime": end_time if end_time else "",
                "Description": description,
                "Location": "",
                "Audience": get_audience(title, description),
                "EventType": get_event_type(title, description),
                "DayTag": "Day 2",
                "Order": order,
                "IsActive": True,
                "IsMandatory": True
            }
        }
        all_events.append(event)

    # Process Day 3 (Sunday)
    for start_time, end_time, title, description, order in day3_events:
        event = {
            "fields": {
                "EventTitle": title,
                "EventDate": "2025-11-16",
                "StartTime": start_time,
                "EndTime": end_time if end_time else "",
                "Description": description,
                "Location": "",
                "Audience": get_audience(title, description),
                "EventType": get_event_type(title, description),
                "DayTag": "Day 3",
                "Order": order,
                "IsActive": True,
                "IsMandatory": True
            }
        }
        all_events.append(event)

    return all_events

def add_schedule_batch(events, batch_size=10):
    """Add events to Airtable in batches."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

    total_events = len(events)
    print(f"📝 Adding {total_events} real schedule events to Airtable...")

    success_count = 0

    # Process in batches
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]

        # Create batch request
        batch_data = {"records": batch}

        response = requests.post(url, headers=HEADERS, json=batch_data)

        if response.status_code == 200:
            created_records = response.json().get('records', [])
            for j, record in enumerate(created_records):
                event_title = batch[j]['fields']['EventTitle']
                event_date = batch[j]['fields']['EventDate']
                print(f"   ✅ Added: {event_title} ({event_date})")
                success_count += 1
        else:
            print(f"   ❌ Batch {i//batch_size + 1} failed: {response.status_code}")
            print(f"      Error: {response.text}")
            # Try individual records if batch fails
            for event in batch:
                response = requests.post(url, headers=HEADERS, json=event)
                if response.status_code == 200:
                    event_title = event['fields']['EventTitle']
                    event_date = event['fields']['EventDate']
                    print(f"   ✅ Added individually: {event_title} ({event_date})")
                    success_count += 1
                else:
                    event_title = event['fields']['EventTitle']
                    print(f"   ❌ Failed: {event_title}")
                time.sleep(0.2)  # Rate limiting for individual requests

        time.sleep(0.3)  # Rate limiting between batches

    print(f"\n📊 Summary: {success_count}/{total_events} events added successfully")
    return success_count

def main():
    print("🚀 Adding Real Tres Dias Schedule")
    print("=" * 50)
    print(f"Base ID: {BASE_ID}")
    print(f"Table ID: {TABLE_ID}")
    print()

    if not API_KEY:
        print("❌ Error: AIRTABLE_API_KEY not found in environment")
        return

    # Create the real schedule
    print("📅 Parsing real Tres Dias schedule...")
    events = create_real_schedule()

    print(f"✅ Parsed {len(events)} events:")

    # Count events by day
    day_counts = {}
    for event in events:
        day_tag = event['fields']['DayTag']
        day_counts[day_tag] = day_counts.get(day_tag, 0) + 1

    for day, count in sorted(day_counts.items()):
        print(f"   {day}: {count} events")

    print()

    # Add events to Airtable
    success_count = add_schedule_batch(events)

    if success_count > 0:
        print(f"\n✨ Successfully added {success_count} real schedule events!")
        print("\n📌 Schedule includes:")
        print("   • Day 0 (Thu 13/11): Preparation day with team arrival and candidate registration")
        print("   • Day 1 (Fri 14/11): First day with ROE talks, meals, and Cross ceremony")
        print("   • Day 2 (Sat 15/11): Second day with sacraments, drama, and Agape")
        print("   • Day 3 (Sun 16/11): Final day with graduation and departure")
        print("\n📋 Event types classified:")
        print("   • ROE talks, Meals, Chapel services, Breaks, Activities, Celebrations")
        print("   • Proper Russian terminology preserved")
        print("   • Audience targeting (All, Candidates, Team)")
    else:
        print("\n❌ No events were added. Check the error messages above.")

if __name__ == "__main__":
    main()