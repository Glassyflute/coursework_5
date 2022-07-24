from flask import Flask, render_template, request, url_for, redirect

from base import Arena
from classes import unit_classes
from equipment import Equipment
from unit import BaseUnit, PlayerUnit, EnemyUnit

app = Flask(__name__)

heroes = {}

arena = Arena()
# TODO инициализируем класс арены
equipment = Equipment()

@app.route("/")
def menu_page():
    # TODO рендерим главное меню (шаблон index.html)
    return render_template("index.html")


@app.route("/fight/")
def start_fight():
    # TODO выполняем функцию start_game экземпляра класса арена и передаем ему необходимые аргументы
    # TODO рендерим экран боя (шаблон fight.html)

    arena.start_game(player=heroes["player"], enemy=heroes["enemy"])
    return render_template("fight.html", heroes=heroes)


@app.route("/fight/hit")
def hit():
    # TODO кнопка нанесения удара
    # TODO обновляем экран боя (нанесение удара) (шаблон fight.html)
    # TODO если игра идет - вызываем метод player.hit() экземпляра класса арены
    # TODO если игра не идет - пропускаем срабатывание метода (просто рендерим шаблон с текущими данными)

    if arena.game_is_running:
        result = arena.player_hit()
    else:
        result = arena.battle_result

    return render_template("fight.html", heroes=heroes, result=result)


@app.route("/fight/use-skill")
def use_skill():
    # TODO кнопка использования скилла
    # # TODO логика практически идентична предыдущему эндпоинту
    if arena.game_is_running:
        result = arena.player_use_skill()
    else:
        result = arena.battle_result

    return render_template("fight.html", heroes=heroes, result=result)


@app.route("/fight/pass-turn")
def pass_turn():
    # # TODO кнопка пропуск хода
    # # TODO логика практически идентична предыдущему эндпоинту
    # TODO однако вызываем здесь функцию следующий ход (arena.next_turn())
    if arena.game_is_running:
        result = arena.next_turn()
    else:
        result = arena.battle_result

    return render_template("fight.html", heroes=heroes, result=result)


@app.route("/fight/end-fight")
def end_fight():
    # TODO кнопка завершить игру - переход в главное меню
    return render_template("index.html", heroes=heroes)


@app.route("/choose-hero/", methods=['post', 'get'])
def choose_hero():
    # TODO кнопка выбор героя. 2 метода GET и POST
    # TODO на GET отрисовываем форму.
    # TODO на POST отправляем форму и делаем редирект на эндпоинт choose enemy
    if request.method == "GET":
        result = {
            "classes": unit_classes,
            "weapons": equipment.get_weapons_names(),
            "armors": equipment.get_armors_names(),
            "header": "Выберите героя",
        }
        return render_template("hero_choosing.html", result=result)

    elif request.method == "POST":
        name = request.form["name"]
        weapon_name = request.form["weapon"]
        armor_name = request.form["armor"]
        unit_class = request.form["unit_class"]

        player = PlayerUnit(name=name, unit_class=unit_classes.get(unit_class))

        # здесь можно проверить, есть ли название оружия или брони среди доступных из выбора
        player.equip_weapon(equipment.get_weapon(weapon_name))
        player.equip_armor(equipment.get_armor(armor_name))

        # if weapon_name not in equipment.get_weapons_names():
        #     print("Оружия такого нет.")
        # if armor_name not in equipment.get_armors_names():
        #     print("Брони такой нет.")

        heroes["player"] = player
        return redirect(url_for("choose_enemy"))

# class based views with 2 methods - get, post
# choose_enemy это по имени функции снизу
# 01.18.x

@app.route("/choose-enemy/", methods=['post', 'get'])
def choose_enemy():
    # TODO кнопка выбор соперников. 2 метода GET и POST
    # TODO также на GET отрисовываем форму.
    # TODO а на POST отправляем форму и делаем редирект на начало битвы
    if request.method == "GET":
        result = {
            "classes": unit_classes,
            "weapons": equipment.get_weapons_names(),
            "armors": equipment.get_armors_names(),
            "header": "Выберите противника",
        }
        return render_template("hero_choosing.html", result=result)

    elif request.method == "POST":
        name = request.form["name"]
        weapon_name = request.form["weapon"]
        armor_name = request.form["armor"]
        unit_class = request.form["unit_class"]

        enemy = EnemyUnit(name=name, unit_class=unit_classes.get(unit_class))

        # здесь можно проверить, есть ли название оружия или брони среди доступных из выбора
        enemy.equip_weapon(equipment.get_weapon(weapon_name))
        enemy.equip_armor(equipment.get_armor(armor_name))

        # if weapon_name not in equipment.get_weapons_names():
        #     print("Оружия такого нет.")
        # if armor_name not in equipment.get_armors_names():
        #     print("Брони такой нет.")

        heroes["enemy"] = enemy
        return redirect(url_for("start_fight"))


if __name__ == "__main__":
    app.run()
