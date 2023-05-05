import sys
import pathlib
from pathlib import Path
import re
import os
import shutil
''' Словарь для транслитерации имен файлов'''

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}
for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = t
    TRANS[ord(c.upper())] = t.upper()

""" Игнор лист папок, списки расширений"""
folder_ignor_list = ['archives', 'audio', 'documents', 'images', 'video']
img_list = ['JPEG', 'PNG', 'JPG', 'SVG']
audio_list = ['MP3', 'OGG', 'WAV', 'AMR']
arh_list = ['ZIP', 'GZ', 'TAR']
doc_list = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX']
video_list = ['AVI', 'MP4', 'MOV', 'MKV']

unknown_file_type_list = set()
known_type_list = set()
music_list = []
images_list = []
archives_list = []
documents_list = []
moov_list = []


""" Функция, нормализующая имена файлов """
def normalize(name):
    file_name = re.findall(r"[^\\]+(?=\.\w+$)", name)   #регулярка для имени файла
    file_type = re.findall(r'\.\w+$', name)             #регулярка для расширения файла
    if file_name == [] and file_type == []:             #если списки имени и раширения пусты - значит это папка из одного имени. нормализуем и возвращаем
        folder_name = name.translate(TRANS)
        copy_folder_name = folder_name
        change_list = re.findall(r'\W', folder_name)
        for i in copy_folder_name:
            for j in change_list:
                if i==j:
                    folder_name = folder_name.replace (i, '_')
        normal_name = folder_name
        return normal_name
    if file_name ==[]:                                  #если файл состоит только из расшерения - оставляем пустым
        file_name = ''
    else:
        file_name = file_name[0]                        #если файл без расширения - оставляем его пустым
    if file_type == []:
        file_type = ""
    else:
        file_type = file_type[0]
    file_name = file_name.translate(TRANS)
    copy_file_name = file_name
    change_list = re.findall(r'\W', file_name)
    for i in copy_file_name:
        for j in change_list:
            if i==j:
                file_name = file_name.replace (i, '_')

    normal_file_name = file_name + file_type
    return normal_file_name

def rec_find(path, dict_destination, depth = 0, marg_sumb = '-' ):
    
    if path.is_dir():
        
        try: #определяем находится ли папка в спике игнорируемых, если да то рекурсивно в нее не входим
            folder_ignor_list.index(path.name)
            ignor = True
        except ValueError:
            ignor = False
            
        
        if path.name != normalize(path.name): #если папки отличается от нормализованного - переименовываем ее
            old_name = str(path)
            new_name = old_name.replace(path.name, normalize (path.name) )
            os.rename(old_name, new_name)
            path = pathlib.Path(new_name)
        
        if ignor == False:
            for item in path.iterdir():
                rec_find (item, dict_destination, depth= depth +1)
            
    else: #находим файл, работаем с ним
        #Находим расширение
        file_type = path.suffix
        file_type = file_type[1:].upper()
        if file_type:
            #пытаемся найти расширение в списках известных. если находим - нормализуем название и переносим в соотв папку
            try:    #Картинки
                img_list.index(file_type)
                normilized_file_name = normalize(path.name)
                new_path = dict_destination.get('images') + '\\' + normilized_file_name
                shutil.move(path, new_path)
                images_list.append(normilized_file_name)
                known_type_list.add(file_type)

            except ValueError:
                unknown_file_type_list.add(file_type)
            try:    #Аудио
                audio_list.index(file_type)
                normilized_file_name = normalize(path.name)
                new_path = dict_destination.get('audio') + '\\' + normilized_file_name
                shutil.move(path, new_path)
                music_list.append(normilized_file_name)
                known_type_list.add(file_type)
            except ValueError:
                unknown_file_type_list.add(file_type)

            try:    #Документы
                doc_list.index(file_type)
                normilized_file_name = normalize(path.name)
                new_path = dict_destination.get('documents') + '\\' + normilized_file_name
                shutil.move(path, new_path)
                documents_list.append(normilized_file_name)
                known_type_list.add(file_type)
            except ValueError:
                unknown_file_type_list.add(file_type)

            try:    #Видео
                video_list.index(file_type)
                normilized_file_name = normalize(path.name)
                new_path = dict_destination.get('video') + '\\' + normilized_file_name
                shutil.move(path, new_path)
                moov_list.append(normilized_file_name)
                known_type_list.add(file_type)
            except ValueError:
                unknown_file_type_list.add(file_type)

            try:    #Архивы
                arh_list.index(file_type)
                normilized_file_name = normalize(path.name)
                folder_name = re.findall(r"[^\\]+(?=\.\w+$)", normilized_file_name)
                new_path = dict_destination.get('archives') + '\\' + normilized_file_name
                shutil.move(path, new_path)
                archives_list.append(path.name)
                known_type_list.add(file_type)
                try:
                    shutil.unpack_archive(new_path, dict_destination.get('archives') + '\\' + folder_name[0]) #Распаковка
                    os.remove(new_path) # Удаление архива
                except:
                    archives_list.append(normilized_file_name)
            except ValueError:
                unknown_file_type_list.add(file_type)
                
    return unknown_file_type_list, known_type_list, images_list, audio_list, documents_list, moov_list, archives_list
"""
Функция удаляет все пустые папки
"""
def del_empty_folders (path):
    empt_fold = 0
    for paths, dirs, files in os.walk(path):
        if (not dirs) and (not files):
            empt_fold +=1
            print (f'Delet empty folder: {paths}')
            os.rmdir(paths)
    if empt_fold > 0:
        del_empty_folders (path)


def main():
    if len (sys.argv) == 1:
        return
    path = pathlib.Path(sys.argv[1])
    
    #print (path)

    #path = Path('d:/goit/sort')
    #создаем нужные папаки
    dict_destination = {}
    for i in folder_ignor_list:
        try:
            path_new_folder = pathlib.Path(path)  / i
            path_new_folder.mkdir()
            print (f'Папка {path_new_folder} создана успешно')
            dict_destination.update({i:str(path_new_folder)})
            
        except FileExistsError:
            print (f'Папка {i} существует')
            dict_destination.update({i:str(path_new_folder)})

    unknown_file_type_list, known_type_list, images_list, audio_list, documents_list, moov_list, archives_list = rec_find(path, dict_destination)
    print('Неизвестные типы файлов:     ', unknown_file_type_list^known_type_list)
    print('Известные типы файлов:       ', known_type_list )
    print('Изображения:                 ', images_list)
    print('Аудиофайлы:                  ', audio_list)
    print('Видео:                       ', moov_list)
    print('Документы:                   ', documents_list)
    print('Архивы:                      ', archives_list)

    #удаляем пусте файлы
    del_empty_folders(path)

if __name__ == "__main__":
    main()