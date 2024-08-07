## Порядок запуска

- Поднять docker-compose:
```bash
docker-compose up --build
```

## Тестовые запуски для разработчика

- Возможно предварительно перед запуском контейнера надо выполнить команду для работы с выводом ximagesink
```bash
xhost + local:
```

- Запуск конвеера от rtsp с выводом на экран:
```bash
gst-launch-1.0 -e rtspsrc location=rtsp://127.0.0.1:8554/cam_001 ! rtph264depay !  avdec_h264  !  decodebin    ! videoconvert ! autovideosink sync=true
```

- Тестовый запуск с камеры:
```bash
gst-launch-1.0 -e rtspsrc location=rtsp://172.16.2.16:554/profile2/media.smp user-id=admin user-pw=Admin123! ! rtph264depay !  avdec_h264  !  decodebin    ! videoconvert ! autovideosink sync=true
```

- Просмотр параметров камеры
```bash
gst-discoverer-1.0 rtsp://admin:Admin12345@10.0.10.207:554/profile1/media.smp
```

## Получение графического отображения пайплайна для разработчиков

- Запустите с указанием пути на файл из папки `tmp/dot`:
```bash
dot -Tsvg 0.00.10.289175435-gst-launch.PAUSED_PLAYING.dot > /videoanalytics2.0/tmp/output.svg
```

- Теперь можете открыть графическую схему пайплайна с указанием параметров.

- Копировать файл с контейнера:
```bash
docker cp 133209294c72:/app/gstream/test.log /home/oem/Desktop/videoanalytics/gstream/tmp
```

## Дебаг режим gstream

- Для включения дебаг режима добавьте перед gst-launch-1.0 команду с указанием глубины дебага:
```bash
GST_DEBUG_FILE=test.log GST_DEBUG=4 gst-launch-1.0 ...
```
- Блэк лист
```bash
gst-inspect-1.0 --print-blacklist
```
- Для получения логов:
```bash
ENV GST_DEBUG_FILE=/app/tmp/test.log
```
