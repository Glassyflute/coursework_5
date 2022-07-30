from __future__ import annotations
from abc import ABC, abstractmethod
from equipment import Weapon, Armor
from classes import UnitClass
from random import randint
from typing import Optional


class BaseUnit(ABC):
    """
    Базовый класс юнита, характеристики включают имя, класс персонажа, здоровье и выносливость юнита,
    оружие и броню, флаг _is_skill_used
    """
    def __init__(self, name: str, unit_class: UnitClass):
        """
        При инициализации класса Unit используем свойства класса UnitClass
        """
        self.name = name
        self.unit_class = unit_class
        self.hp = unit_class.max_health
        self.stamina = unit_class.max_stamina
        self.weapon = None
        self.armor = None
        self._is_skill_used = False

    @property
    def health_points(self):
        """
        возвращает значение атрибута hp (здоровье)
        """
        return round(self.hp, 1)

    @property
    def stamina_points(self):
        """
        возвращает значение атрибута stamina (выносливость)
        """
        return round(self.stamina, 1)

    def equip_weapon(self, weapon: Weapon):
        """
        метод принимает оружие и присваивает это оружие свойству экз-ра класса
        """
        self.weapon = weapon
        return f"{self.name} экипирован оружием {self.weapon.name}"

    def equip_armor(self, armor: Armor):
        """
        метод принимает броню и присваивает эту броню свойству экз-ра класса
        """
        self.armor = armor
        return f"{self.name} экипирован броней {self.armor.name}"

    def _count_damage(self, target: BaseUnit) -> float:
        """
        расчет урона, нанесенного игроком
        """
        # урон игрока рассчитываем по схеме ниже.
        # урон_от_оружия = случайное число в диапазоне (min_damage - max_damage)
        # УРОН_АТАКУЮЩЕГО = урон_от_оружия * модификатор_атаки_класса
        damage = self.weapon.damage * self.unit_class.attack_mltplr

        # Уменьшается выносливость атакующего при ударе
        self.stamina -= self.weapon.stamina_per_hit
        # восстановление выносливости идет через _stamina_regeneration в файле base.py в каждом раунде

        # проверяем, достаточно ли выносливости у противника, чтобы снизить урон атакующего
        if target.stamina >= target.armor.stamina_per_turn:
            # БРОНЯ_ЦЕЛИ = надетая_броня * модификатор_брони_класса
            target_armor = target.armor.defence * target.unit_class.armor_mltplr

            # Уменьшается выносливость противника (цели) при использовании брони для защиты
            target.stamina -= target.armor.stamina_per_turn
            # восстановление выносливости идет через _stamina_regeneration в файле base.py в каждом раунде

            # при успешном блокировании броней урон атакующего игрока снижается за счет брони
            # УРОН = УРОН_АТАКУЮЩЕГО - БРОНЯ_ЦЕЛИ
            damage -= target_armor

        return target.get_damage(damage)

    def get_damage(self, damage: float) -> Optional[float]:
        """
        получение урона целью и снижение уровня здоровья цели
        """
        damage = round(damage, 1)
        if damage > 0:
            self.hp -= damage
            return damage
        return 0

    @abstractmethod
    def hit(self, target: BaseUnit) -> str:
        """
        метод переопределен ниже
        """
        pass

    def use_skill(self, target: BaseUnit) -> str:
        """
        Метод использования умения.
        Если умение уже использовано, возвращается строка 'Навык использован'.
        Если умение не было использовано, тогда возвращается строка,
        которая характеризует выполнение умения, и флаг _is_skill_used меняет значение на True.
        """
        if self._is_skill_used:
            return "Навык использован."

        self._is_skill_used = True
        return self.unit_class.skill.use(user=self, target=target)


class PlayerUnit(BaseUnit):

    def hit(self, target: BaseUnit) -> str:
        """
        Функция удар игрока:
        здесь происходит проверка, достаточно ли выносливости для нанесения удара.
        Вызывается функция self._count_damage(target), успех атаки отображается строкой.
        """
        # проверяем, достаточно ли выносливости для нанесения удара
        if self.stamina < self.weapon.stamina_per_hit:
            return f"{self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости. "

        # показываем результат атаки в части нанесенного игроком урона сопернику
        damage = self._count_damage(target)
        if damage > 0:
            return f"{self.name} используя {self.weapon.name} пробивает {target.armor.name} соперника" \
                   f" и наносит {damage} урона. "

        if damage == 0:
            return f"{self.name} используя {self.weapon.name} наносит удар, но {target.armor.name} " \
                   f"cоперника его останавливает. "


class EnemyUnit(BaseUnit):

    def hit(self, target: BaseUnit) -> str:
        """
        Функция удар соперника:
        здесь происходит проверка, применялось ли умение ранее и дается шанс применить умение.
        Происходит проверка, достаточно ли выносливости для нанесения удара.
        Вызывается функция self._count_damage(target), успех атаки отображается строкой.


        Например, для этих целей можно использовать функцию randint из библиотеки random.
        Если умение не применено, противник наносит простой удар, где также используется
        функция _count_damage(target)
        """
        # проверяем поочередно (слева направо) выполнение условий для использования навыка класса
        # умение можно использовать только 1 раз за бой при достаточном уровне выносливости
        # вероятность успешного использования умения противником составляет 10%
        if not self._is_skill_used and self.stamina >= self.unit_class.skill.stamina and randint(0, 100) < 10:
            self.use_skill(target)

        # если умение не было применено, то противник наносит простой удар
        # проверка, достаточно ли выносливости для нанесения удара
        stamina_to_hit = self.weapon.stamina_per_hit * self.unit_class.stamina_mltplr
        if self.stamina < stamina_to_hit:
            return f"{self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости. "

        # показывается результат атаки в части нанесенного урона игроку
        damage = self._count_damage(target)
        if damage > 0:
            return f"{self.name} используя {self.weapon.name} пробивает {target.armor.name}" \
                   f" и наносит Вам {damage} урона. "

        if damage == 0:
            return f"{self.name} используя {self.weapon.name} наносит удар, но Ваш(а) " \
                   f"{target.armor.name} его останавливает. "
