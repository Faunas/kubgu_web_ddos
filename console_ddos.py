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
import art

faq_text = "[!!!] Данное уведомление появится лишь однократно!\n" \
            "Для того, чтобы не вводить данные вручную, вы можете задать конкретные флаги и переменные в файле config.txt.\n" \
            "После установки work_mode_only_from_config = 1, вам больше никогда не придётся выбирать режим работы.\n"\
            "Все переменные имеют комментарии и интуитивно понятны.\n" \
            "При следующем запуске вы не увидите данное уведомление.\n\n\n"\

os.environ["PATH"] += os.pathsep + r"msedgedriver.exe"
urls = []

with open('links.txt', 'r') as f:
    lines = f.readlines()
for line in lines:
    urls.append(line.replace('\n', ''))

random_university_words = []
with open('search.txt', encoding="UTF-8") as f:
    lines = f.readlines()
for line in lines:
    random_university_words.append(line.replace('\n', ''))


ART = art.text2art('KUBGU Viewer')
with open("config.txt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        if "art_on_start" in line:
            if line.split("=")[1].strip() == "1":
                art_on_start = 1
                print(ART)
                time.sleep(1.5)
            break

with open('config.txt', 'r') as f:
    lines = f.readlines()

with open('config.txt', 'w') as f:
    for line in lines:
        if line.startswith('new_user'):
            if 'new_user = 1' in line:
                print(faq_text)
                time.sleep(5)
                line = 'new_user = 0\n'
        f.write(line)





work_mode_only_from_config = 0
with open("config.txt") as f:
    for line in f:
        if line.startswith("#"):
            continue
        if "work_mode_only_from_config" in line:
            if line.split("=")[1].strip() == "1":
                work_mode_only_from_config = 1
                print("Данные берутся из файла конфигураций. (Установлен флаг work_mode_only_from_config)")
            break



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
    print(f"""
    +--------[УСТАНОВЛЕННЫЕ ЗНАЧЕНИЯ]---------+
    |+----------------------------+----------+|
    ||        Наименование        | Значение ||
    |+----------------------------+----------+|
    ||     Время ожидания         |   {pause_time}    ||
    ||     Количество потоков     |    {NUM_THREADS}     ||
    ||     Количество веб-сайтов  |    {counter_web_sites}     ||
    ||     Режим работы из конфига|    {work_mode_only_from_config}     ||
    ++----------------------------+----------++------------------------------+|
    ||Возможное время на сайте исходя из установленного время ожидания:      ||
    ||Минимум: {int(float(pause_time) * 6  + float(19.6) + 2)} секунд.                                                    ||
    ||Максимум: {int(float(pause_time) * 6 + float(64.4) + 2)} секунд.                                                  ||
    ++-----------------------------------------------------------------------++""")


def go_to_url(index, url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if index >= counter_web_sites:
        url = random.choice(urls)

    with webdriver.Edge("msedgedriver.exe", options=options) as driver:
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
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            loop = asyncio.get_event_loop()
            tasks = []
            for i in range(NUM_THREADS):
                time.sleep(random.uniform(1, 2.5))  #   Задержка между потоками.
                tasks.append(loop.run_in_executor(executor, go_to_url, i, urls[i % counter_web_sites]))
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

# TODO: Использовать невидимый для браузера селениум
#  Сделать большую задержку создания потоков на временном промежутке от 20:00 До 6:00
#  Добавить логирование/Информирование на каждые 100 просмотров страницы
#  Закомпилить exe файл.