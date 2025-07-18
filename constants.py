default_lang = "ru"
# link_to_channel = "https://t.me/B6Laundrytest/"
link_to_channel = "https://t.me/B6Laundry/"

T_record_has_been_created = {"ru": "Запись создана. Приятного пользования!",
                             "en": "The record has been created. Enjoy!"}

T_record_already_created = {"ru": "Запись уже создана",
                            "en": "The record has already been created"}

T_select_language = {"ru": "Выберите язык:",
                     "en": "Please select your language:"}

T_languages = {"ru": "Русский",
               "en": "English"}

T_selected_language = {"ru": "Выбран язык: ",
                       "en": "Selected language: "}

T_too_many_boxes = {"ru": "У Вас слишком много боксов (больше 100). Очистите очередь отслеживания.",
                    "en": "You have too many boxes (more than 100). Clear the tracking queue."}

T_added_to_tracking = {"ru": "Добавлены для отслеживания: {}\nСейчас отслеживаются: {}",
                       "en": "Added for tracking: {}\nTracking now: {}"}

T_error_added_to_tracking = {"ru": "Набор контейнеров не распознан.\nСейчас отслеживаются: {}",
                             "en": "Boxes are not recognized\nNow Tracking: {}"}

T_now_tracking = {"ru": "Сейчас отслеживаются: {}",
                  "en": "Tracking now: {}"}

T_queue_is_empty = {"ru": "Очередь пуста",
                    "en": "Queue is empty"}

T_box_ready = {"ru": 'Бокс {} готов и удалён из отслеживания. <a href="{}">Оригинальное сообщение</a>',
               "en": 'Box {} is ready and is no longer being tracked. <a href="{}">Original message</a>'}

T_box_maybe_ready = {
    "ru": 'Бокс {}, вероятно, готов, проверьте <a href="{}">оригинальное сообщение</a> и удалите его вручную:',
    "en": 'Box {} is probably ready, check the <a href="{}">оriginal message</a> and delete it manually:'}

T_manually_delete_box = {"ru": "Удалить бокс {}",
                         "en": "Delete the box {}"}

T_box_are_not_exist = {"ru": "Бокса {} уже нет в списке отслеживания",
                       "en": "Box {} is no longer on the tracking list"}

T_success = {"ru": "Успешно",
             "en": "Success"}

T_delete_all = {"ru": "Удалить все",
                "en": "Delete all"}

T_delete_last = {"ru": "Удалить последний",
                 "en": "Delete the last box"}

T_incorrect_data = {"ru": "Отправленный тип файла не поддерживается. Отправьте чек в формате фото или файлом",
                    "en": "The sent file type is not supported. Send a check as a photo or as a file"}

T_exceeding_file_size = {"ru": "Размер файла не может превышать 100 МБ",
                         "en": "File size cannot exceed 100 MB",}

T_cant_add_more_files = {"ru": "Нельзя добавить больше 10 файлов к письму",
                         "en": "You can't add more than 10 files to the letter"}

T_hi_messages = {"ru": {"mess": "Добро пожаловать в B6PrachkaBot!\nЕсли что, он нужен для удобного отслеживания "
                                "Ваших стирок. Для добавления к отслеживанию одного или нескольких контейнеров, "
                                "отправьте сообщение с их номерами, разделёнными любыми символами (не числа). \nКогда "
                                "про ваш контейнер напишут в <a href=\"https://t.me/B6Laundry\">чате прачечной</a>, "
                                "бот пришлёт уведомление. \n\nПример:\n"
                                "1, 4, 42 -> контейнеры 1, 4 и 42\n"
                                "6 8 10 7 -> контейнеры 6, 8, 10 и 7\n"
                                "28 -> контейнер 28\n"
                                "12,'+OR+1=1-- -> контейнеры 12 и 1\n\n"
                                "Для вывода инструкции на иных языках, нажмите кнопку:",
                        "to_lang": "Вывести инструкцию на русском"},
                 "en": {"mess": "Welcome to the B6PrachkaBot!\nIt is needed for convenient tracking of your laundry. "
                                "In order to add your boxes on the tracking list, send a message with their numbers "
                                "separated with any symbols.\nIf your container is mentioned in "
                                "<a href=\"https://t.me/B6Laundry\">laundry chat</a>, you will get notified."
                                "\n\nExample:\n"
                                "1, 4, 42 -> containers 1, 4, and 42\n"
                                "6 8 10 7 -> containers 6, 8, 10, and 7.\n"
                                "28 -> container 28\n\n"
                                "To see the manual in other languages, please press the button:",
                        "to_lang": "Show the manual in English"}}