import requests, json, time, os, datetime
from pprint import pprint
from tqdm import tqdm



def write_json(data): # получение списка фотографий со страницы в VK в формате json
    with open('photos.json', 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_foto_data(offset = 0, count = 50): # получение списка фотографий со страницы в VK
    api = requests.get('https://api.vk.com/method/photos.getAll', params ={
        'owner_id': vk_user_id,
        'access_token': vk_token,
        'offset': offset,
        'count': count,
        'extended': 1,
        'photo_sizes': True,
        'v': 5.131

    })
    write_json(api.json())
    return json.loads(api.text)


def get_largest(size_dict):
    ''' определение ориентации фотографии  '''
    if size_dict['width'] >= size_dict['height']:
        return size_dict['width']
    else:
        return size_dict['height']

def time_conversion(unix_time):
    ''' конвертация unix-времени в обыкновенную дату '''
    value = datetime.datetime.fromtimestamp(unix_time)
    time_value = value.strftime('%Y-%m-%d time %H-%M-%S')
    return time_value

class YaUploader:

    def __init__(self, token: str):
        self.token = token

    def creating_folder(self, file_path):
        ''' Создание папки на Яндекс.Диске '''
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {"path": file_path}
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        response = requests.put(url=upload_url, headers=headers, params=params)


    def upload(self, file_path, url_vk):
        '''  загрузка файла на Яндекс.Диск '''
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": file_path, "url": url_vk}
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        response = requests.post(url=upload_url, headers=headers, params=params)
        json_resp = response.json()
        href = json_resp.get('href', '')
        resp = requests.get(url=href, headers=headers, params=params)
        resp.raise_for_status()


def main():
    get_foto_data() # получение списка фотографий со страницы в VK
    photos = json.load(open('photos.json'))['response']['items']
    json_list = []
    name_url_photos_dict = {}
    number = 0
    for photo in photos: # заполнение словаря ключ: кол-во лайков/дата загрузки фотографий, значение url фотографии в vk
        sizes = photo['sizes']
        lickes = photo['likes']
        max_size_url = max(sizes, key=get_largest)["url"] #определение фотографии максимального размера
        for numb_url in sizes:
            if numb_url["url"] == max_size_url:
                size = numb_url['type']

        if lickes['count'] == 0 or lickes['count'] == number:
            unix_time = photo['date']
            key_photo = time_conversion(unix_time)

        else:
            key_photo = lickes['count']
            number = lickes['count']

        file_name = f'{key_photo}.jpg'
        json_list.append({'file name': file_name, 'size': size})
        name_url_photos_dict[key_photo] = max_size_url

    creat_fold = YaUploader(token)
    res_folder = creat_fold.creating_folder(path_to_file)
    num = int(input('Введите количество фотографий для загрузки (от  1 до 5)\n'))
    json_list_result = []
    for name_photo, i in zip(name_url_photos_dict.keys(), tqdm(range(num))):
        uploader = YaUploader(token)
        result = uploader.upload(f'{path_to_file}/{name_photo}', name_url_photos_dict[name_photo])
        json_list_result.append(json_list[int(i-1)])
    with open('uploaded_VK_photos', 'w') as file:
        json.dump(json_list_result, file)

    print()
    print(f'Загружено на Яндекс.Диск фотографий: {num}')



if __name__ == "__main__":
    ''' получение от пользователя id VK, токенов в VK и на Яндекс.Диске,
    указываются в файле id_and_tokens.txt '''
    with open('id_and_tokenss.txt') as f:
        vk_user_id = f.readline().strip()
        vk_token = f.readline().strip()
        token = f.read().strip()
    path_to_file = input("Введите название папки на Яндекс.Диске\n")
    main()










