def get_polls():
    polls_list = [
        dict(
            poll_title="Природные ископаемые",
            poll_description="опрос про природные ископаемые",
            questions=[
                dict(
                    question_name="Как называют брилианты до обрабоки?",
                    choices=[
                        dict(choice_name="Изумруд", is_correct=False),
                        dict(choice_name="Неограненный бриллиант", is_correct=False),
                        dict(choice_name="Рубин", is_correct=False),
                        dict(choice_name="Алмаз", is_correct=True),
                    ],
                ),
                dict(
                    question_name="В честь чего назван минерал Танзанит?",
                    choices=[
                        dict(choice_name="В чеесть императора Танзании - Танзанития 4-го", is_correct=False),
                        dict(
                            choice_name="В честь начедшего минерал исследователя  - Мркуса Тансона",
                            is_correct=False,
                        ),
                        dict(choice_name="В честь старны - Таназнии ", is_correct=True),
                    ],
                ),
                dict(
                    question_name="Какой драгоценный металл не подвержен коррозии?",
                    choices=[dict(choice_name="Медь", is_correct=False), dict(choice_name="Золото", is_correct=True)],
                ),
            ],
        ),
        dict(
            poll_title="Космос",
            poll_description="опрос про космос",
            questions=[
                dict(
                    question_name="Как называют галактику в который мы находимся?",
                    choices=[
                        dict(choice_name="Андромеда", is_correct=False),
                        dict(choice_name="Пегас", is_correct=False),
                        dict(choice_name="Млечный Путь", is_correct=True),
                    ],
                ),
                dict(
                    question_name="Самая большая планета в солнечной системе?",
                    choices=[
                        dict(choice_name="Солнце", is_correct=False),
                        dict(
                            choice_name="Нептун",
                            is_correct=False,
                        ),
                        dict(choice_name="Юпитер", is_correct=True),
                    ],
                ),
                dict(
                    question_name="Сколько спутников у Сатурна?",
                    choices=[dict(choice_name="33", is_correct=False), dict(choice_name="83", is_correct=True)],
                ),
            ],
        ),
    ]
    return polls_list


def get_user_info():
    data_user_teacher = {
        "username": "TestUser123",
        "first_name": "TestUserFirstName",
        "last_name": "TestUserLastName",
        "email": "TestUser@email.com",
    }

    data_profile_teacher = {"ph_number": "89673876987", "user_type": "teacher"}

    data_user_student = {
        "username": "TestUser123Student_student",
        "first_name": "TestUserFirstName_student",
        "last_name": "TestUserLastName_student",
        "email": "TestUser@email.com_student",
    }
    data_profile_student = {"ph_number": "89673876980", "user_type": "student"}

    data_all = {"student": dict(profile=data_profile_student, user_d=data_user_student),
                "teacher": dict(profile=data_profile_teacher, user_d=data_user_teacher)}

    return data_all
