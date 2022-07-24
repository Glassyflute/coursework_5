from __future__ import annotations
from abc import ABC, abstractmethod
from equipment import Equipment, Weapon, Armor
from classes import UnitClass
from random import randint
from typing import Optional


# 32.55
class BaseUnit(ABC):
    """
    Базовый класс юнита
    """
    def __init__(self, name: str, unit_class: UnitClass):
        """
        При инициализации класса Unit используем свойства класса UnitClass
        """
        self.name = name
        self.unit_class = unit_class
        self.hp = unit_class.max_health
        self.stamina = unit_class.max_stamina
        self.weapon = ...
        self.armor = ...
        self._is_skill_used = False

    @property
    def health_points(self):
        return round(self.hp, 1)
        # TODO возвращаем аттрибут hp в красивом виде

    @property
    def stamina_points(self):
        return round(self.stamina, 1)
        # TODO возвращаем аттрибут stamina в красивом виде

    def equip_weapon(self, weapon: Weapon):
        # TODO присваиваем нашему герою новое оружие
        self.weapon = weapon
        return f"{self.name} экипирован оружием {self.weapon.name}"

    def equip_armor(self, armor: Armor):
        # TODO одеваем новую броню
        self.armor = armor
        return f"{self.name} экипирован броней {self.armor.name}"

    def _count_damage(self, target: BaseUnit) -> int:
        # TODO Эта функция должна содержать:
        #  логику расчета урона игрока
        #  логику расчета брони цели
        #  здесь же происходит уменьшение выносливости атакующего при ударе
        #  и уменьшение выносливости защищающегося при использовании брони
        #  если у защищающегося нехватает выносливости - его броня игнорируется
        #  после всех расчетов цель получает урон - target.get_damage(damage)
        #  и возвращаем предполагаемый урон для последующего вывода пользователю в текстовом виде

        # урон игрока рассчитываем по схеме ниже.
        # урон_от_оружия = случайное число в диапазоне (min_damage - max_damage)
        # УРОН_АТАКУЮЩЕГО = урон_от_оружия * модификатор_атаки_класса
        damage = self.weapon.damage * self.unit_class.attack_mltplr

        # Уменьшается выносливость атакующего при ударе
        # (с учетом класса атакующего игрока и затрат на выносливость при ударе в раунде)
        self.stamina -= self.weapon.stamina_per_hit * self.unit_class.stamina_mltplr

        # проверяем, достаточно ли выносливости у противника, чтобы заблокировать удар броней
        # (с учетом класса противника и затрат на выносливость при использовании брони в раунде)
        stamina_to_block_by_armor = target.armor.stamina_per_turn * target.unit_class.stamina_mltplr
        if target.stamina > stamina_to_block_by_armor:
            # если выносливости хватает, снижаем выносливость противника по результату раунда игры
            # УТОЧНИТЬ если ровненько хватает стамины на блок в раунде????
            target.stamina -= stamina_to_block_by_armor

            # БРОНЯ_ЦЕЛИ = надетая_броня * модификатор_брони_класса
            target_armor = target.armor.defence * target.unit_class.armor_mltplr

            # при успешном блокировании броней урон атакующего игрока снижается за счет брони
            # УРОН = УРОН_АТАКУЮЩЕГО - БРОНЯ_ЦЕЛИ
            damage -= target_armor

        # если выносливости у противника недостаточно, чтобы заблокировать удар броней, противник получает
        # полный урон от атакующего игрока
        return target.get_damage(damage)

    def get_damage(self, damage: int) -> Optional[int]:
        # TODO получение урона целью
        #   присваиваем новое значение для аттрибута self.hp
        if damage > 0:
            self.hp -= damage
            return damage
        return 0

    @abstractmethod
    def hit(self, target: BaseUnit) -> str:
        """
        этот метод будет переопределен ниже
        """
        pass

    def use_skill(self, target: BaseUnit) -> str:
        """
        метод использования умения.
        если умение уже использовано возвращаем строку
        Навык использован
        Если же умение не использовано тогда выполняем функцию
        self.unit_class.skill.use(user=self, target=target)
        и уже эта функция вернем нам строку которая характеризует выполнение умения
        """
        if self._is_skill_used:
            return "Навык использован."

        self._is_skill_used = True
        return self.unit_class.skill.use(user=self, target=target)


class PlayerUnit(BaseUnit):

    def hit(self, target: BaseUnit) -> str:
        """
        функция удар игрока:
        здесь происходит проверка достаточно ли выносливости для нанесения удара.
        вызывается функция self._count_damage(target)
        а также возвращается результат в виде строки
        """
        # проверяем, достаточно ли выносливости для нанесения удара
        stamina_to_hit = self.weapon.stamina_per_hit * self.unit_class.stamina_mltplr
        if self.stamina < stamina_to_hit:
            return f"{self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости."

        damage = self._count_damage(target)
        if damage > 0:
            return f"{self.name} используя {self.weapon.name} пробивает {target.armor.name} соперника" \
                   f" и наносит {damage} урона."

        if damage == 0:
            f"{self.name} используя {self.weapon.name} наносит удар, но {target.armor.name} cоперника " \
            f"его останавливает."

        # stamina_to_block_by_armor = target.armor.stamina_per_turn * target.unit_class.stamina_mltplr
        # self.stamina -= self.weapon.stamina_per_hit * self.unit_class.stamina_mltplr


class EnemyUnit(BaseUnit):

    def hit(self, target: BaseUnit) -> str:
        """
        функция удар соперника
        должна содержать логику применения соперником умения
        (он должен делать это автоматически и только 1 раз за бой).
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
        stamina_to_hit = self.weapon.stamina_per_hit * self.unit_class.stamina_mltplr
        if self.stamina < stamina_to_hit:
            return f"{self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости."

        damage = self._count_damage(target)
        if damage > 0:
            return f"{self.name} используя {self.weapon.name} пробивает {target.armor.name}" \
                   f" и наносит Вам {damage} урона."

        if damage == 0:
            f"{self.name} используя {self.weapon.name} наносит удар, но Ваш(а) {target.armor.name} его останавливает."
