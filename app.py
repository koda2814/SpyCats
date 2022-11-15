import os
import sys
from PIL import Image


class Stega():
    """
    Класс для работы со стеганографией
    """

    eng = 'abcdefghijklmnopqrstuvwxyzÆÇÈÉÊÌÍABCDEFGHIJKLMNOPQRSTUVWXYZÎÏÐÑÒÓÔ'
    rus = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

    SYMBOLS_TABLE_RUS = {} # 'h': 'ж'
    SYMBOLS_TABLE_ENG = {} # 'ж': 'h'

    for sym in zip(eng, rus):
        SYMBOLS_TABLE_RUS[sym[0]]=sym[1]
        SYMBOLS_TABLE_ENG[sym[1]]=sym[0]


    def __create_mask(self, degree):
        """Возвращает битовые маски для текста и для картинки"""
        text_mask = 0b11111111
        img_mask = 0b11111111

        text_mask <<= 8 - degree
        text_mask %= 256
        img_mask >>= degree
        img_mask <<= degree

        return [text_mask, img_mask]


    def __convert_msg(self, msg):
        """Разделяет спец-символами кириллицу и латиницу в шифруемом сообщении."""
        msg = msg.split()

        flag1, flag2 = True, False
        res = []
        for word in msg:
            if not word.isascii() and flag1:
                word = f"@{word}"
                flag1, flag2 = False, True

            if word.isascii() and flag2:
                word= f"${word}"
                flag1, flag2 = True, False

            res.append(word)
        new = " ".join(res)
        return f'{new}×'



    def encrypt(self, msg, degree, pic):
        """
        Функция для шифрования данных в bmp картинку
        """

        if os.stat(pic).st_size * degree - 54 < len(msg.encode('utf-8'))*8: #проверка на вместимость сообщения в картинку
            print('MESSAGE TO ENCRYPT TOO BIG, CHOOSE ANOTHER PICTURE OR SMALLER VALUE OF DEGREE')
            return None

        startbmp = open(pic, 'rb')
        encodebmp = open('encode.bmp', 'wb')

        first54 = startbmp.read(54) #первые 54 бита несут только служебную информацию
        encodebmp.write(first54)

        text_mask = self.__create_mask(degree)[0]
        img_mask = self.__create_mask(degree)[1]

        cyrillic_flag = False

        msg = self.__convert_msg(msg) #добавляем спец символы к исходному сообщению
        for sym in msg:
            
            if sym == '@': cyrillic_flag=True #проверка на кириллицу
            if sym == '$': cyrillic_flag=False #проверка на кириллицу

            if cyrillic_flag:
                sym = Stega.SYMBOLS_TABLE_ENG.get(sym, sym)

            sym = ord(sym) #представление символа в бинарном виде
            for iter in range(0, int(8/degree)): #количество итераций (сдвигов)
                bmp_byte = int.from_bytes(startbmp.read(1), sys.byteorder) #получаем байт из bmp
                bmp_byte &= img_mask #стираем последние биты изображения с помощью маски
                
                bits = sym & text_mask #стираем конечные биты сообщения с помощью маски
                bits >>= (8 - degree) #сдвигаем начальные биты сообщения на конец

                bmp_byte |= bits #объединяем и получаем конечный зашифрованный бит
                encodebmp.write(bmp_byte.to_bytes(1, sys.byteorder)) #записываем его в зашифрованную картинку

                sym <<= degree


        print(startbmp.tell())
        encodebmp.write(startbmp.read())
    
        startbmp.close()
        encodebmp.close()
        

        
    def decrypt(self, degree, pic):
        """
        Расшифровывает содержимое из bmp картинки
        """
        
        encodebmp = open(pic, 'rb')
        msg = ''

        encodebmp.seek(54) #начинаем с 54 т.к. первые 54 байта несут системную информацию о картинке

        img_mask = self.__create_mask(degree)[1] 
        img_mask = ~ img_mask #операция двоичного отрицания, получаем обратную маску для bmp

        cyrillic_flag = False

        while True:
            sym = 0
            for iter in range(0, int(8/degree)): #количество итераций (сдвигов)
                bmp_byte = int.from_bytes(encodebmp.read(1), sys.byteorder) #получаем байт из зашифрованногов bmp
                bmp_byte &= img_mask #стираем RGB биты изображения с помощью обратной маски
                
                sym <<= degree #сдвигаем старые биты влево на степень сдвига (шаг)
                sym |= bmp_byte #на место старых битов ставим биты из шифрованного bmp

            sym = chr(sym)

            if sym == '×': break
        
            if sym == '@': #проверка на кириллицу
                cyrillic_flag=True 
                continue

            if sym == '$': #проверка на кириллицу
                cyrillic_flag=False
                continue

            if cyrillic_flag:
                sym = Stega.SYMBOLS_TABLE_RUS.get(sym, sym)

            msg += sym 

        encodebmp.close()
        return msg





def main():

    img = Image.open('pics/cat.png').convert('RGB')
    img.save('pics/cat_rgb.png')
    # print(img.mode)

    inst = Stega()
    inst.encrypt('hello I love OOP', 2, 'pics/cat_rgb.png')
    message = inst.decrypt(2, 'encode.bmp')
    print(message) #output: hello I love OOP


    # print('завершено')



if __name__ == "__main__":
    main()