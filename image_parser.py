import requests
from bs4 import BeautifulSoup as bs
import cv2 as cv
from datetime import datetime
import pytesseract as tess
from PIL import Image
import os
from multiprocessing import Pool
import csv

tess.pytesseract.tesseract_cmd = r'D:\Users\Klork\AppData\Local\Tesseract-OCR\tesseract.exe'
base_url = 'https://manganelo.com/manga/read_onepunchman_one'
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': user_agent}
alphabet = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x',
            'c', 'v', 'b', 'n', 'm', "'"]


def get_count_page():
    session = requests.session()
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        soup = bs(request.content, 'lxml')
        try:
            print("good")
            divs = soup.find_all('div', class_='panel-story-chapter-list')
            for div in divs:
                print(div)
                count = div.find('a', class_="chapter-name text-nowrap").text
                count = count[8:]
                print(count)
        except:
            print("first except")
    else:
        print(request.status_code)
        print('ERROR')
    return count


def get_image_from_url(url):
    # for url in links:
    print('get image from ', url)
    begin = url.rfind('_')
    begin = url[:begin].rfind('/') + 1
    img = requests.get(url)
    name = url[begin:].replace('/', '_')
    with open(f'{name}', 'wb') as file:
        file.write(img.content)


def get_text_from_image():
    listdir = os.listdir()
    for image in listdir[:]:
        print('get text from ', image)
        img = cv.imread(f'{image}', 0)
        ret, th1 = cv.threshold(img, 111, 255, cv.THRESH_BINARY)
        cv.imwrite('th1.jpg', th1)
        img = Image.open('th1.jpg')
        text = tess.image_to_string(img, lang='eng')
        os.chdir('..')
        with open('text', 'a', encoding='UTF-8') as file:
            file.write(f'{text} ')
        os.chdir('images')


def count_image_from_url(count):
    links = []
    for chapter in range(count):
        chapter += 1
        url = base_url[:20] + base_url[20:].replace('manga', 'chapter') + f'/chapter_{chapter}'
        print('get links on image from ', url)
        session = requests.session()
        request = session.get(url, headers=headers)
        if request.status_code == 200:
            soup = bs(request.content, 'lxml')
            try:
                a = soup.find('div', class_="container-chapter-reader")
                a = a.find_all('img')
                for i in a:
                    links.append(i['src'])
            except:
                print('Second except')
        else:
            print(request.status_code)
            print('Status_code error 2')
        '''for num in range(count_img):
            num += num
            url = f'https://s7.mkklcdnv7.com/mangakakalot/r1/read_onepunchman_one/chapter_{chapter}/{num}.jpg'
            get_image_from_url(url, num)
            get_text_from_image(num)
        '''
    print(links)
    return links


def rewrite():
    if 'images' not in os.listdir():
        os.mkdir('images')
    os.chdir('images')
    list = os.listdir()
    for file in list:
        os.remove(file)
    os.chdir('..')
    with open('text', 'w+') as file:
        pass


def get_wordlist():
    os.chdir('..')
    with open('text', 'r+', encoding="UTF-8") as file:
        wordlist = []
        for line in file.readlines():
            line = line[:-1]
            line = line.split(' ')
            if line[0] != "":
                for element in line:
                    if len(element) > 1:
                        word = element.lower()
                        x = word
                        trash = ''
                        for i in x:
                            trash += i
                            if trash == i * 3:
                                word = ''
                                break
                            if i not in alphabet:
                                if i == '-':
                                    word = word.replace(i, ' ')
                                else:
                                    word = word.replace(i, '')
                        word = word.strip()
                        if len(word) > 2:
                            wordlist.append(word.title())
        print(wordlist)
    return wordlist


def get_word_dict(word_list, translate_list):
    word_dict = {}
    for i in range(len(word_list)):
        if word_list[i] != translate_list[i]:
            word_dict[word_list[i]] = translate_list[i]
    return word_dict


def write_word_dict(word_dict):
    with open('word_dict.csv', 'w+', encoding='UTF-8') as file:
        writer = csv.writer(file)
        for key, value in word_dict.items():
            writer.writerow((key, value))


def translate(word_list):
    session = requests.session()
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'
    api = 'trnsl.1.1.20200229T104608Z.60e8d78e7ab50c16.0d9b273f3f0a7b20f524efb46cc4338f151aa31c'
    params = {
        "key": api,
        "text": word_list,
        "lang": 'en-ru'
    }
    request = session.get(url, headers=headers, params=params)
    translate_list = request.json()['text']
    return translate_list


def main():
    count = 3  # int(get_count_page())
    links = count_image_from_url(count)
    os.chdir('images')
    with Pool(30) as p:
        p.map(get_image_from_url, links)
    # get_image_from_url(links)
    get_text_from_image()
    word_list = get_wordlist()
    translate_list = translate(word_list)
    print(translate_list)
    word_dict = get_word_dict(word_list, translate_list)
    print(word_dict)
    write_word_dict(word_dict)


if __name__ == '__main__':
    rewrite()
    main()

