import asyncio
import datetime
import gc
import os
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import art
from loggerfile import *
import re
import json

faq_text = "[!!!] Данное уведомление появится лишь однократно!\n" \
           "Для того, чтобы не вводить данные вручную, вы можете задать конкретные флаги и переменные в файле config.txt.\n" \
           "После установки work_mode_only_from_config = 1, вам больше никогда не придётся выбирать режим работы.\n" \
           "Все переменные имеют комментарии и интуитивно понятны.\n" \
           "При следующем запуске вы не увидите данное уведомление.\n\n\n"
os.environ["PATH"] += os.pathsep + r"msedgedriver.exe"
urls = []


config_dict = {}
with open('config.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        key, value = line.split('=')
        config_dict[key.strip()] = value.strip()

with open('dev_config.json', 'w') as f:
    json.dump(config_dict, f)

with open('dev_config.json', 'r') as f:
    config_dict = json.load(f)

pause_time = float(config_dict['pause_time'])
NUM_THREADS = int(config_dict['NUM_THREADS'])
counter_web_sites = int(config_dict['counter_web_sites'])
work_mode_only_from_config = int(int(config_dict['work_mode_only_from_config']))
art_on_start = bool(int(config_dict['art_on_start']))
new_user = bool(int(config_dict['new_user']))
views_to_write_logfile = int(config_dict['views_to_write_logfile'])
debug_mode = bool(int(config_dict['debug_mode']))


with open('config.txt', 'r') as f:
    content = f.read()

match = re.search(r'debug_mode\s*=\s*(\d+)', content)
#   Поиск значения для режима отладки

if debug_mode == 1:
    print(
        "\n\n\nВКЛЮЧЁН РЕЖИМ ОТЛАДКИ! БРАУЗЕРЫ БУДУТ ВИДНЫ. ЧТОБЫ ОТКЛЮЧИТЬ ИЗМЕНИТЕ ЗНАЧЕНИЕ С 1 НА 0 (debug_mode=0)")
    time.sleep(5)

text_about_log = f"Логирование в файл произойдёт при {views_to_write_logfile}+ просмотров. (Меняется в конфиге)"

#   Добавление всех ссылок из файла в список urls.
with open('links.txt', 'r') as f:
    lines = f.readlines()
for line in lines:
    urls.append(line.replace('\n', ''))

#   Добавление всех слов для поиска из файла в список random_university_words.
random_university_words = []
with open('search.txt', encoding="UTF-8") as f:
    lines = f.readlines()
for line in lines:
    random_university_words.append(line.replace('\n', ''))

ART = art.text2art('KUBGU Viewer')
#   Поиск значения для вывода логотипа при старте
if art_on_start == 1:
    print(ART)
    time.sleep(1.5)
#   Поиск значения, уведомляющее о том, что пользователь новый,
#   если это так, то выводит приветственное сообщение и меняет
#   переменную на 0, чтобы пользователь не считался новым.
with open('config.txt', 'r') as f:
    lines = f.readlines()

with open('config.txt', 'w') as f:
    for line in lines:
        if line.startswith('new_user'):
            if 'new_user=1' in line:
                print(faq_text)
                time.sleep(5)
                line = 'new_user=0\n'
        f.write(line)

if work_mode_only_from_config == 1:
    print("Данные берутся из файла конфигураций. (Установлен флаг work_mode_only_from_config)")


if work_mode_only_from_config == 0:
    print("--- Нужно выбрать режим работы!\n"
          "1. Ввод данных вручную\n"
          "2. Брать данные из файла конфигурации\n")
    work_mode = int(input("Выберите режим работы: "))
    if work_mode == 1:
        num_sites = int(input("Введите количество выводимых сайтов: "))
        print(urls[:num_sites])
        counter_web_sites = int(input("Введите количество обрабатываемых сайтов: "))
        if counter_web_sites == -1:
            counter_web_sites = len(urls)

        urls = urls[:counter_web_sites]

        NUM_THREADS = int(input("Введите количество потоков: "))

        pause_time = float(input("Введите задержку перед махинациями на сайте: "))
    else:
        print(
            '\n----------------------------------------------------------------------------------------------------------------\n'
            'Вы выбрали режим работы "Брать данные из файла конфигурации". \nЕсли вы хотите, чтобы данные всегда '
            'брались из файла конфигурации, то замените work_mode_only_from_config = 0\nна work_mode_only_from_config = 1 в '
            'файле конфигурации config.txt\n----------------------------------------------------------------------------------------------------------------')
        with open('config.txt', 'r') as f:
            for line in f:
                if line.startswith("#"):
                    continue
                key, value = line.strip().split('=')
                if key == 'pause_time':
                    pause_time = float(value)
                elif key == 'NUM_THREADS':
                    NUM_THREADS = int(value)
                elif key == 'counter_web_sites':
                    counter_web_sites = int(value)

else:
    #   Поиск значений, которые установлены в конфиге.
    print(f"""
    +--------[УСТАНОВЛЕННЫЕ ЗНАЧЕНИЯ]---------+
    ++----------------------------+----------++
    ||        Наименование        | Значение ||
    |+----------------------------+----------+|
    ||     Время ожидания         |   {pause_time}    ||
    ||     Количество потоков     |    {NUM_THREADS}     ||
    ||     Количество веб-сайтов  |    {counter_web_sites}     ||
    ||     Режим работы из конфига|    {work_mode_only_from_config}     ||
    ++----------------------------+----------++------------------------------+|
    ||Возможное время на сайте исходя из установленного время ожидания:      ||
    ||Минимум: {int(float(pause_time) * 6 + float(19.6) + 2)} секунд.                                                    ||
    ||Максимум: {int(float(pause_time) * 6 + float(64.4) + 2)} секунд.                                                   ||
    ||{text_about_log}||
    ++-----------------------------------------------------------------------++""")


def go_to_url(index, url):
    options = Options()
    if debug_mode == 0:
        options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if index >= counter_web_sites:
        url = random.choice(urls)

    with webdriver.Edge(service=Service("msedgedriver.exe"), options=options) as driver:
        start_time = time.monotonic()
        driver.get(url)
        time.sleep(pause_time)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time + random.uniform(2.5, 10.5))
        driver.execute_script("window.scrollTo(0, 0);")
        driver.find_element(by=By.CSS_SELECTOR, value='#edit-custom-search-blocks-form-1--2').click()
        time.sleep(pause_time + random.uniform(3.5, 21.5))
        text_form = driver.find_element(by=By.CSS_SELECTOR, value='#edit-custom-search-blocks-form-1--2')
        text_form.send_keys(random.choice(random_university_words))
        # print(text_form.text)
        driver.find_element(by=By.CSS_SELECTOR, value='#edit-actions').click()
        time.sleep(pause_time + random.uniform(2.5, 10.5))
        try:
            driver.find_element(by=By.CSS_SELECTOR,
                                value='div.views-row.views-row-1.views-row-odd.views-row-first > div > span > a').click()
            time.sleep(pause_time + 1.5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass
        # print("Не найдено")
        time.sleep(pause_time + random.uniform(1.5, 4.9))
        for i in range(4):
            driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(random.uniform(1.1, 3.5))
        time.sleep(2)

        end_time = time.monotonic()

        print(f"Thread {index} : {url} was processed in {end_time - start_time:.2f} seconds")
    driver.quit()


async def main():
    try:
        with ThreadPoolExecutor(max_workers=int(NUM_THREADS)) as executor:
            loop = asyncio.get_event_loop()
            tasks = []
            for i in range(NUM_THREADS):
                current_time = datetime.datetime.now().time()
                if current_time >= datetime.time(20, 0) or current_time < datetime.time(7, 0):
                    sleep_between_threads = random.uniform(600, 1200)
                    next_thread_time = datetime.datetime.now() + datetime.timedelta(seconds=sleep_between_threads)
                    print(
                        f"Сейчас ночь, поэтому следующий поток запустится через {datetime.timedelta(seconds=int(sleep_between_threads))} секунд = {round(int(sleep_between_threads) / 60)} минут")
                    print(f"Следующий поток запустится в {next_thread_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    sleep_between_threads = random.uniform(1, 2.5)
                tasks.append(loop.run_in_executor(executor, go_to_url, i, urls[i % counter_web_sites]))
                time.sleep(sleep_between_threads)  # Задержка между потоками.

            await asyncio.gather(*tasks)
            #   Очистка памяти.
            print("Очищаю память.")
            del executor
            del loop
            gc.collect()
            subprocess.call(['ipconfig', '/flushdns'])
            print("Память очищена.")
    except Exception:
        print("Очищаю память with error.")
        del executor
        del loop
        gc.collect()
        subprocess.call(['ipconfig', '/flushdns'])
        print("Память очищена with error.")


if __name__ == '__main__':
    time.sleep(10)
    counter = 0
    print(f'Начал выполнение в {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    while True:
        asyncio.run(main())
        gc.collect()
        counter += 1
        print(f"Количество итераций: {counter}")
        print(f"Количество посещенний сайтов: {counter * NUM_THREADS}")
        if counter * NUM_THREADS >= views_to_write_logfile:
            print(
                f'Количество просмотров достигла отметки в {views_to_write_logfile} посещений в {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(
                f'Количество просмотров достигла отметки в {views_to_write_logfile} Всего посещений за текущий сеанс: {counter * NUM_THREADS}')
            counter = 0

#   TODO: Использовать чтение из json, вместо чтения из файлов по несколько раз.