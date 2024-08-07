from django.db import models


class ClassName(models.Model):
    class ClassNames(models.TextChoices):
        person = "person"
        face = "face"
        hands = "hands"
        legs = "legs"
        body = "body"
        gun = "gun"
        knife = "knife"
        bag = "bag"
        balaclava = "balaclava"
        concealing_glasses = "concealing glasses"
        hand = "hand"
        medicine_mask = "medicine mask"
        non_concealing_glasses = "non-concealing glasses"
        nothing = "nothing"
        scarf = "scarf"
        fall_down = "fall down"
        helmet = "helmet"
        vest = "vest"
        head = "head"
        hands_up = "hands_up"
        big_bag = "big bag"

    name = models.CharField(max_length=50, choices=ClassNames.choices, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "Class Names (superuser)"
        verbose_name_plural = "Class Names (superuser)"


class ModelsName(models.Model):
    class ModelName(models.TextChoices):
        skeleton = "skeleton"
        guns = "guns"
        bags = "bags"
        face_hiding = "face_hiding"
        human_fault = "human_fault"
        siz = "siz"

    name = models.CharField(max_length=30, choices=ModelName.choices)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Models Names (superuser)"
        verbose_name_plural = "Models Names (superuser)"


class ClassesNumber(models.Model):
    number = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.number}"

    class Meta:
        verbose_name = "Class Number (superuser)"
        verbose_name_plural = "Class Number (superuser)"


class Profile(models.Model):
    # class QualityType(models.TextChoices):
    #     H264_1 = "H264-1"
    #     H264_2 = "H264-2"
    #     H264_3 = "H264-3"

    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Profiles (superuser)"
        verbose_name_plural = "Profiles (superuser)"


class Points(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Key points (superuser)"
        verbose_name_plural = "Key points (superuser)"
