# matcha

Страницы:

  - регистрация / логин:
      - подтверждение почты
  - профиль:
      - гендер
      - пол
      - краткое описание
      - интересы в виде хэштегов
      - фотографии (до 5)
      - местоположение
  - главная
  - настройки:
      - возможность поменять пароль
  - коннекты (если два пользователя лайкнули друг друга)
  - сообщения
 
Функции:

  - просмотр тех, кто "оценил" пользователя
  - пользователь должен иметь публичный "рейтинг известности"
  - определение местоположения (даже если пользователь не захотел этого)
  - подбор партнера:
  учитывается при подборе:
    - пол
    - местоположение (приоритет)
    - общие теги (интересы)
    - наибольший "рейтинг известности"
    - возможность фильтровать и сортировать по возрасту, местоположению, рейтингу и общим тегам
  - поиск:
      - интервал возраста
      - интервал рейтинга
      - местоположение (я так думаю расстояние от пользователя: 5км, 10км и т.д. ну или по городам/странам)
      - по одному или нескольким тегам
  - история посещений (зашел к кому то на профиль - информация добавилась в этот раздел)
  - отображение онлайна, даты и времени последнего посещения
  - возможность репортить пользователей как фейки
  - блокировка пользователей (черный список)
  - уведомления (должны быть видны на всех страницах (всплывающие?)):
      - получение лайка
      - просмотр профиля
      - получение сообщения
      - создание коннекта (лайк в ответ)
      - разрывание коннекта

REQUIREMENTS:

В таблицу django_site нужно добавить объект с хостом, на котором
выложен этот сайт. В локалке это будет 127.0.0.1, а на проде что-то вроде `www.host.org`.
Нужно установить `domain = yandex.ru` (если почта, с которой посылаются письма, это `yandex`,
в противном случае это будет что-то другое), а `name = 127.0.0.1:8000`, если запускается на локалке.  

Чтобы заработал чат, нужно поднять локально (или на сервере)
redis (стандартный порт).

`brew install libmaxminddb` для более быстрой геолокации
(для других систем см. https://github.com/maxmind/libmaxminddb)

Нужно изменить под себя GEOIP_PATH, в котором будут лежать файлы
GeoLite2 City и GeoLite2 Country с
https://www.maxmind.com/en/accounts/394283/geoip/downloads. 
Из разархивированных папок нужно взять файлы с расширением `.mmdb`
и поместить их в отдельную папку,
на которую и должен указывать GEOIP_PATH.
