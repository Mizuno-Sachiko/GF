"""终焉花海：60Hz逻辑更新，复用目录中的动画、背景与音效。

F1显示碰撞区域；F2输出状态变化与每秒运行状态。
"""

import random
from collections.abc import Iterable
from enum import Enum, auto
from functools import lru_cache
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parent
FPS = 60
STEP = 1 / FPS
ARENA = pygame.Rect(0, 0, 1280, 720)
# 加载动画：各动作的图片数量，文件名从0开始。
PLAYER_FRAMES = {
    "wait": 54,
    "move": 24,
    "back": 31,
    "attack": 34,
    "backattack": 34,
    "moveattack": 24,
    "die": 137,
    "win": 142,
}
BOSS_FRAMES = {
    "wait": 54,
    "move": 40,
    "attack1": 50,
    "attack2": 67,
    "skill3": 67,
    "skill4": 639,
    "die": 167,
}
BOSS_POSITIONS = ((1000, 360), (1000, 180), (1000, 540), (720, 180), (720, 540))
# Nyto判定点：右腿、左腿、身体、头部，相对角色中心设置。
BOSS_HITBOXES = (
    (10, 40, 20, 65),
    (-40, 40, 20, 65),
    (-20, -20, 30, 60),
    (-40, -90, 70, 70),
)
BULLET_RADII = {20: 10, 30: 20, 80: 60}
SHOT_FRAMES = {
    "attack": (1, 7, 12),
    "backattack": (1, 7, 12),
    "moveattack": (1, 5, 10),
}
GAP_FRAMES = (
    71,
    121,
    170,
    215,
    245,
    285,
    355,
    375,
    435,
    455,
    475,
    495,
    550,
    570,
    585,
    605,
)


class Scene(Enum):
    TITLE = auto()
    INTRO = auto()
    BATTLE = auto()
    WIN = auto()
    LOSE = auto()


@lru_cache(maxsize=128)
def load_image(path: str) -> pygame.Surface:
    # 动画按帧加载；限制缓存大小，避免同时解码所有序列。
    return pygame.image.load(ROOT / path).convert_alpha()


@lru_cache(maxsize=1)
def load_intro(frame: int) -> pygame.Surface:
    # 过场单向播放，只保留当前帧，使用不含透明通道的像素格式。
    return pygame.image.load(ROOT / f"art/Load/{frame}.jpg").convert()


def draw_image(
    screen: pygame.Surface,
    image: pygame.Surface,
    position: tuple[int, int] | pygame.Rect,
    alpha: int = 255,
) -> None:
    if alpha != 255:
        # 缓存中的Surface会被多个对象共享，透明度只修改绘制副本。
        image = image.copy()
        image.set_alpha(alpha)
    screen.blit(image, position)


def play_music(filename: str, volume: float, fade_ms: int = 0) -> None:
    pygame.mixer.music.load(ROOT / "Sound" / filename)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops=-1, fade_ms=fade_ms)


class Actor:
    def __init__(
        self,
        prefix: str,
        frames: dict[str, int],
        center: tuple[int, int],
        health: int,
        death_frame: int,
        death_offset: int,
    ) -> None:
        self.prefix = prefix
        self.frames = frames
        self.animation = "wait"
        self.frame: int = 0
        self.position: pygame.Vector2 = pygame.Vector2(center)
        self.rect = self.image.get_rect(center=center)
        self.max_health = health
        self.health = health
        self.death_frame = death_frame
        self.death_offset = death_offset
        self.alpha = 255

    @property
    def image(self) -> pygame.Surface:
        frame = self.frame % self.frames[self.animation]
        return load_image(f"{self.prefix}_{self.animation}/{frame}.png")

    def set_animation(self, animation: str) -> None:
        if animation != self.animation:
            self.animation = animation
            self.frame = 0

    def take_damage(self, damage: int) -> None:
        if self.health == 0:
            return
        self.health = max(0, self.health - damage)
        if self.health == 0:
            self.set_animation("die")
            # 死亡序列的人物位置与站立序列不同，需要对应的水平偏移。
            self.position.x += self.death_offset
            self.rect.center = (round(self.position.x), round(self.position.y))

    def advance(self) -> None:
        if self.animation == "die":
            if self.frame < self.death_frame:
                self.frame += 1
            else:
                self.alpha = max(0, self.alpha - 6)
        elif self.animation == "win":
            self.frame = min(self.frame + 1, self.frames["win"] - 1)
        else:
            self.frame = (self.frame + 1) % self.frames[self.animation]

    def draw(self, screen: pygame.Surface, alpha: int = 255) -> None:
        draw_image(screen, self.image, self.rect, min(alpha, self.alpha))


class Bullet:
    def __init__(
        self,
        image: pygame.Surface,
        position: pygame.Vector2,
        velocity: pygame.Vector2,
        damage: int = 0,
        radius: int = 0,
    ) -> None:
        self.image = image
        self.position = position.copy()
        self.velocity = velocity
        self.rect = image.get_rect(center=(round(position.x), round(position.y)))
        self.damage = damage
        self.radius = radius

    def update(self) -> bool:
        # 用浮点位置累计位移，Rect仅用于绘制与矩形碰撞。
        self.position += self.velocity
        self.rect.center = (round(self.position.x), round(self.position.y))
        return ARENA.colliderect(self.rect)


class Phantom:
    def __init__(self, position: tuple[int, int]) -> None:
        self.frame = 0
        self.image = load_image("phantom/phantom_dash/0.png")
        self.rect = self.image.get_rect(topleft=position)
        self.speed = 40
        self.has_collided = False

    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(self.rect.x + 85, self.rect.y + 80, 110, 160)

    def update(self) -> bool:
        if self.frame >= 83:
            self.rect.x -= self.speed
            self.speed += 12
        self.frame = min(self.frame + 1, 139)
        self.image = load_image(f"phantom/phantom_dash/{self.frame}.png")
        return ARENA.colliderect(self.rect)


class Player(Actor):
    def __init__(self) -> None:
        super().__init__("M4A1/M4A1", PLAYER_FRAMES, (320, 360), 1000, 136, 50)
        self.bullets: list[Bullet] = []
        self.focused = False
        self.dot_angle = 0
        self.attack = 5

    def set_animation(self, animation: str) -> None:
        if animation in ("die", "win"):
            super().set_animation(animation)
        else:
            # 普通动作共用连续帧计数，切换动作不重置射击时序。
            self.animation = animation

    def advance(self) -> None:
        if self.animation in ("die", "win"):
            super().advance()
        else:
            self.frame += 1

    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(self.rect.centerx - 7, self.rect.centery + 17, 10, 10)

    def move(self, direction: pygame.Vector2, focused: bool, firing: bool) -> None:
        if self.health == 0 or self.animation == "win":
            self.focused = False
            return
        # M4A1速度判断（Shift）。
        self.focused = focused
        if focused:
            self.dot_angle = (self.dot_angle + 1) % 360
        # M4A1位置更新及活动区域限制。
        self.position += direction * (5 if focused else 10)
        self.rect.center = (round(self.position.x), round(self.position.y))
        hitbox = self.hitbox
        self.position += pygame.Vector2(hitbox.clamp(ARENA).topleft) - hitbox.topleft
        self.rect.center = (round(self.position.x), round(self.position.y))

        # M4A1移动状态判断。
        if direction.x < 0:
            animation = "backattack" if firing else "back"
        elif direction.length_squared():
            animation = "moveattack" if firing else "move"
        else:
            animation = "attack" if firing else "wait"
        self.set_animation(animation)

    def fire(self) -> bool:
        frame = self.frame % self.frames[self.animation]
        if frame not in SHOT_FRAMES.get(self.animation, ()):
            return False
        bullet = Bullet(
            load_image("Bullet/M4A1/Bullet.png"),
            pygame.Vector2(self.rect.right - 69, self.rect.centery + 21),
            pygame.Vector2(40, 0),
        )
        self.bullets.append(bullet)
        return True


class Boss(Actor):
    def __init__(self) -> None:
        super().__init__("Nyto/nyto", BOSS_FRAMES, (1000, 360), 2500, 127, 120)
        self.bullets: list[Bullet] = []
        self.phantoms: list[Phantom] = []
        self.target = self.position.copy()
        self.next_move = random.randint(600, 720)
        self.next_attack = random.randint(60, 120)
        self.followup = False
        self.special_count = 0
        self.special_loop = 0
        self.gap = 15

    @property
    def hitboxes(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(self.rect.centerx + x, self.rect.centery + y, width, height)
            for x, y, width, height in BOSS_HITBOXES
        ]

    def update(self, tick: int) -> None:
        if self.health == 0:
            return
        # Nyto血量判定：50%发动第一次技能4，25%发动第二次。
        thresholds = (self.max_health * 0.5, self.max_health * 0.25)
        if (
            self.special_count < 2
            and self.health <= thresholds[self.special_count]
            and self.animation != "skill4"
        ):
            self.set_animation("skill4")
            self.special_loop = 0
            self.followup = False

        # Nyto移动及移动状态判定。
        if tick >= self.next_move:
            self.next_move = tick + random.randint(540, 600)
            if self.animation == "wait":
                self.target = pygame.Vector2(random.choice(BOSS_POSITIONS))
                self.set_animation("move")
        if self.animation == "move":
            self.position.move_towards_ip(self.target, 10)
            self.rect.center = (round(self.position.x), round(self.position.y))
            if self.position == self.target:
                self.set_animation("wait")

        # Nyto攻击状态判定。
        if tick >= self.next_attack:
            self.next_attack = tick + random.randint(30, 60)
            if self.animation == "wait":
                self.followup = False
                self.set_animation(random.choice(("attack1", "attack2", "skill3")))

    def advance(self) -> None:
        if self.animation == "skill4":
            # 第二次技能将67～600帧播放三遍，再播放收尾部分。
            if self.special_count == 1 and self.frame == 600 and self.special_loop < 2:
                self.special_loop += 1
                self.frame = 67
                return
            if self.frame == self.frames["skill4"] - 1:
                self.special_count += 1
                self.set_animation("wait")
                return
        elif self.animation in ("attack1", "attack2", "skill3"):
            if self.frame == self.frames[self.animation] - 1:
                if self.animation == "attack1" and self.followup:
                    self.frame = 0
                else:
                    self.set_animation("wait")
                return
        super().advance()

    def ring(self, angles: Iterable[int], speed: int, size: int) -> None:
        for angle in angles:
            # 屏幕坐标向下为正；0度向左，90度向上。
            self.bullets.append(
                Bullet(
                    load_image(f"Bullet/nyto/{size}.png"),
                    self.position,
                    pygame.Vector2(-speed, 0).rotate(angle),
                    size,
                    BULLET_RADII[size],
                )
            )

    def aim(
        self, start: pygame.Vector2, target: pygame.Vector2, speed: int, size: int
    ) -> Bullet | None:
        direction = target - start
        if direction.length_squared() == 0:
            # 起点与目标重合时没有发射方向，不生成这颗定向子弹。
            return None
        bullet = Bullet(
            load_image(f"Bullet/nyto/{size}.png"),
            start,
            direction.normalize() * speed,
            size,
            BULLET_RADII[size],
        )
        self.bullets.append(bullet)
        return bullet

    def aimed_volley(self, target: pygame.Vector2) -> None:
        if self.followup:
            self.ring(range(random.randint(0, 5), 360, 10), 12, 30)
            self.followup = False
            return
        for x in (-20, -80, -140, -200):
            for y in (-25, 27):
                bullet = self.aim(
                    self.position + (x + 15, y + 15), target + (x + 20, y), 8, 30
                )
                if bullet is not None:
                    # 各列沿射击方向错开起点，形成两排平行弹幕。
                    bullet.position.y -= (x + 20) * bullet.velocity.y / 8
                    bullet.rect.center = (
                        round(bullet.position.x),
                        round(bullet.position.y),
                    )
        self.followup = random.random() > 0.25

    def spawn_phantoms(self) -> None:
        # 技能3：随机起点生成幻影，10%几率向下追加两个。
        x = random.choice((1000, 900, 800))
        y = random.randrange(26) * 20
        count = 3 if random.random() <= 0.1 else 1
        for index in range(count):
            self.phantoms.append(Phantom((x, y + index * 100)))

    def special_attack(self, target: pygame.Vector2) -> None:
        frame = self.frame
        if self.special_count == 0:
            if frame in GAP_FRAMES:
                # 技能4阶段1：圆形弹幕留出30度缺口，缺口起点最多移动40度。
                self.gap = random.randint(max(4, self.gap - 8), min(26, self.gap + 8))
                self.ring(
                    (
                        -90 + index * 5
                        for index in range(72)
                        if not self.gap <= index < self.gap + 6
                    ),
                    3,
                    30,
                )
            elif frame in range(610, 639, 2):
                # 技能4阶段2：从随机高度发射自机狙。
                self.aim(
                    self.position + (10, random.randint(-40, 40) + 10), target, 6, 20
                )
        elif self.special_loop == 0 and frame in range(67, 498, 2):
            # 技能4阶段3：随机选四个角度发射。
            self.ring((random.randrange(360) for _ in range(4)), 3, 30)
            if frame in range(131, 516, 64):
                # 每12度一发子弹的圆形弹幕。
                self.ring(range(random.randint(0, 10), 360, 12), 6, 20)
        elif self.special_loop == 1 and frame in range(67, 540, 59):
            # 技能4阶段4：每3度一发，交替发射上下半圆弹幕。
            start = 180 if frame % 2 == 0 else 0
            self.ring(range(start, start + 181, 3), 9, 30)
        elif self.special_loop == 2 and frame in range(62, 595, 7):
            # 技能4阶段5：以当前帧数为起始角度，发射旋转弹幕。
            self.ring(range(frame % 360, frame % 360 + 360, 25), 4, 30)

    def fire(self, target: pygame.Vector2) -> None:
        if self.animation == "attack1" and self.frame == 31:
            self.aimed_volley(target)
        elif self.animation == "attack2":
            if self.frame == 32:
                # 攻击2阶段1：慢速圆形弹幕。
                self.ring(range(random.randint(0, 10), 370, 11), 2, 30)
            elif self.frame == 50:
                # 攻击2阶段2：快速圆形弹幕与大号自机狙。
                self.ring(range(random.randint(0, 10), 415, 25), 6, 20)
                self.aim(self.position + (40, 40), target, 14, 80)
        elif self.animation == "skill3" and self.frame in (19, 31, 46):
            self.spawn_phantoms()
        elif self.animation == "skill4":
            self.special_attack(target)


def resolve_collisions(player: Player, boss: Boss) -> None:
    # M4A1子弹与Nyto的碰撞判定。
    if boss.health > 0:
        hitboxes = boss.hitboxes
        remaining: list[Bullet] = [
            bullet
            for bullet in player.bullets
            if bullet.rect.collidelist(hitboxes) == -1
        ]
        # 同帧命中的玩家子弹全部消耗，伤害只按命中时的攻击力结算一次。
        if len(remaining) != len(player.bullets):
            boss.take_damage(player.attack)
        player.bullets = remaining

    if player.health == 0 or player.animation == "win":
        return
    # Nyto子弹伤害判定。
    hitbox = player.hitbox
    center = pygame.Vector2(hitbox.center)
    damage = 0
    remaining = []
    for bullet in boss.bullets:
        if bullet.position.distance_squared_to(center) <= bullet.radius**2:
            damage += bullet.damage
        else:
            remaining.append(bullet)
    boss.bullets = remaining
    for phantom in boss.phantoms:
        if not phantom.has_collided and phantom.hitbox.colliderect(hitbox):
            damage += 75
            phantom.has_collided = True
    player.take_damage(damage)


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.player = Player()
        self.boss = Boss()
        self.shot = pygame.mixer.Sound(ROOT / "Sound/gun.wav")
        self.running = True
        self.scene = Scene.TITLE
        self.frame = 0
        self.debug_hitboxes = False
        self.debug_logs = False
        self._debug_state: str | None = None
        self.enter(Scene.TITLE)

    def enter(self, scene: Scene) -> None:
        self.scene = scene
        self.frame = 0
        match scene:
            case Scene.TITLE:
                play_music("M_19summer_zombie_h.ogg", 0.4)
            case Scene.INTRO:
                # 过场沿用标题音乐。
                return
            case Scene.BATTLE:
                play_music("M_19summer_song.wav", 0.5)
            case Scene.WIN:
                play_music("Win.wav", 0.4, 2000)
            case Scene.LOSE:
                play_music("Lose.wav", 0.4, 2000)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.debug_hitboxes = not self.debug_hitboxes
            elif event.key == pygame.K_F2:
                self.debug_logs = not self.debug_logs
                self._debug_state = None
                self.log_debug_state()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scene == Scene.TITLE:
                self.enter(Scene.INTRO)
            elif self.scene in (Scene.WIN, Scene.LOSE):
                self.running = False

    def step(self, direction: pygame.Vector2, focused: bool, firing: bool) -> None:
        self.frame += 1
        if self.scene == Scene.INTRO and self.frame == 395:
            self.enter(Scene.BATTLE)
        elif self.scene == Scene.BATTLE:
            self.step_battle(direction, focused, firing)
        self.log_debug_state()

    def log_debug_state(self) -> None:
        if not self.debug_logs:
            return
        state = (
            f"scene={self.scene.name} "
            f"player={self.player.health}/{self.player.max_health}:"
            f"{self.player.animation} "
            f"boss={self.boss.health}/{self.boss.max_health}:{self.boss.animation} "
            f"special={self.boss.special_count}/{self.boss.special_loop} "
            f"gap_angle={self.boss.gap * 5 - 90} phantoms={len(self.boss.phantoms)}"
        )
        # 状态变化立即输出，连续动画和位移每秒记录一次，避免逐帧刷屏。
        if state == self._debug_state and self.frame % FPS != 0:
            return
        player_frame = self.player.frame % self.player.frames[self.player.animation]
        print(
            f"{state} tick={self.frame} "
            f"player_frame={player_frame} player_counter={self.player.frame} "
            f"player_position={self.player.position} "
            f"boss_frame={self.boss.frame} boss_position={self.boss.position} "
            f"bullets={len(self.player.bullets)}/{len(self.boss.bullets)} "
            f"phantom_frames={[(p.rect.topleft, p.frame) for p in self.boss.phantoms]} "
            f"intro_alpha={self.intro_alpha if self.scene == Scene.INTRO else '-'}"
        )
        self._debug_state = state

    def step_battle(
        self, direction: pygame.Vector2, focused: bool, firing: bool
    ) -> None:
        self.player.advance()
        self.boss.advance()
        self.player.move(direction, focused, firing)
        self.boss.update(self.frame)
        if self.boss.animation == "skill4":
            self.player.attack = 3
        if self.player.fire():
            self.shot.play()
        if self.player.health > 0 and self.player.animation != "win":
            self.boss.fire(pygame.Vector2(self.player.hitbox.center))
        self.player.bullets = [
            bullet for bullet in self.player.bullets if bullet.update()
        ]
        self.boss.bullets = [bullet for bullet in self.boss.bullets if bullet.update()]
        self.boss.phantoms = [
            phantom for phantom in self.boss.phantoms if phantom.update()
        ]
        resolve_collisions(self.player, self.boss)

        # 同时死亡按失败处理；死亡期间保留已有弹幕，胜利动画期间停止战斗。
        if self.player.health == 0:
            if self.player.alpha == 0:
                self.enter(Scene.LOSE)
        elif self.boss.alpha == 0:
            if self.player.animation != "win":
                self.player.set_animation("win")
                self.player.bullets.clear()
                self.boss.bullets.clear()
                self.boss.phantoms.clear()
            elif self.player.frame == PLAYER_FRAMES["win"] - 1:
                self.enter(Scene.WIN)

    def draw_world(self) -> None:
        self.screen.blit(load_image("BG/2019summer_5 720.png"), (0, 0))
        self.player.draw(self.screen, 220 if self.player.focused else 255)
        self.boss.draw(self.screen)

    def draw_battle(self) -> None:
        self.draw_world()
        # 判定点输出。
        if self.player.focused and self.player.health > 0:
            dot = pygame.transform.rotate(
                load_image("M4A1/dot.png"), self.player.dot_angle
            )
            draw_image(
                self.screen, dot, dot.get_rect(center=self.player.hitbox.center), 180
            )
        # 子弹与幻影输出。
        for bullets in (self.player.bullets, self.boss.bullets):
            for bullet in bullets:
                self.screen.blit(bullet.image, bullet.rect)
        for phantom in self.boss.phantoms:
            draw_image(self.screen, phantom.image, phantom.rect, 130)
        # 绘制血条。
        pygame.draw.rect(
            self.screen,
            (192, 192, 192),
            (140, 50, 1000 * self.boss.health / self.boss.max_health, 5),
        )
        pygame.draw.rect(
            self.screen,
            (0, 255, 255),
            (120, 710, 200 * self.player.health / self.player.max_health, 10),
        )
        draw_image(self.screen, load_image("M4A1/pic_m4a1mod_n.png"), (0, 600), 240)
        if self.debug_hitboxes:
            self.draw_hitboxes()

    def draw_hitboxes(self) -> None:
        # 绘制实际参与碰撞的区域；已命中的幻影不再造成伤害。
        if self.player.health > 0 and self.player.animation != "win":
            pygame.draw.rect(self.screen, (255, 255, 255), self.player.hitbox, 1)
            for bullet in self.boss.bullets:
                pygame.draw.circle(
                    self.screen, (255, 165, 0), bullet.position, bullet.radius, 1
                )
            for phantom in self.boss.phantoms:
                if not phantom.has_collided:
                    pygame.draw.rect(self.screen, (255, 0, 0), phantom.hitbox, 1)
        if self.boss.health > 0:
            for hitbox in self.boss.hitboxes:
                pygame.draw.rect(self.screen, (255, 255, 255), hitbox, 1)
            for bullet in self.player.bullets:
                pygame.draw.rect(self.screen, (0, 255, 255), bullet.rect, 1)

    @property
    def intro_alpha(self) -> int:
        if self.frame < 364:
            return 255
        return max(0, 255 - (self.frame - 363) * 8 - 7)

    def draw(self) -> None:
        match self.scene:
            case Scene.TITLE:
                self.screen.blit(load_image("BG/2019summer_10 720.png"), (0, 0))
                self.screen.blit(load_image("art/logo.png"), (30, 30))
                self.screen.blit(load_image("art/subtitle.png"), (80, 130))
                pulse = self.frame * 3 % 512
                draw_image(
                    self.screen,
                    load_image("art/description.png"),
                    (517, 550),
                    min(pulse, 511 - pulse),
                )
            case Scene.INTRO:
                self.draw_world()
                draw_image(
                    self.screen, load_intro(self.frame), (0, 0), self.intro_alpha
                )
            case Scene.BATTLE:
                self.draw_battle()
            case Scene.WIN:
                self.screen.blit(
                    load_image("BG/Shattered_Connexion_Login_Wallpaper2 720.png"),
                    (0, 0),
                )
                self.screen.blit(load_image("art/Win.png"), (290, 200))
            case Scene.LOSE:
                self.screen.blit(load_image("BG/2019summer_4_1 720.png"), (0, 0))
                self.screen.blit(load_image("art/Lose.png"), (190, 300))

    def run(self) -> None:
        clock = pygame.time.Clock()
        accumulator = 0.0
        while self.running:
            # 窗口拖动或系统暂停后，不一次性执行长时间积累的战斗更新。
            accumulator += min(clock.tick(FPS) / 1000, 0.1)
            for event in pygame.event.get():
                self.handle_event(event)
            if not self.running:
                break
            keys = pygame.key.get_pressed()
            active = pygame.key.get_focused()
            direction = (
                pygame.Vector2(
                    int(keys[pygame.K_RIGHT] or keys[pygame.K_d])
                    - int(keys[pygame.K_LEFT] or keys[pygame.K_a]),
                    int(keys[pygame.K_DOWN] or keys[pygame.K_s])
                    - int(keys[pygame.K_UP] or keys[pygame.K_w]),
                )
                if active
                else pygame.Vector2()
            )
            focused = active and keys[pygame.K_LSHIFT]
            firing = active and pygame.mouse.get_pressed()[0]
            while accumulator >= STEP:
                self.step(direction, focused, firing)
                accumulator -= STEP
            self.draw()
            pygame.display.flip()


if __name__ == "__main__":
    try:
        pygame.display.init()
        pygame.mixer.init()
        window = pygame.display.set_mode(ARENA.size)
        pygame.display.set_caption("终焉花海")
        pygame.display.set_icon(load_image("icon/icon.png"))
        Game(window).run()
    finally:
        pygame.quit()
