import pygame
import random
import math  # 导入 math 模块

# 游戏设置
SCREEN_WIDTH = 1080  # 屏幕宽度
SCREEN_HEIGHT = 720  # 屏幕高度
FPS = 60  # 每秒帧数
BACKGROUND_IMAGE_PATH = "Image\\Backgrounds\\longgong.jpg"  # 新增背景路径

# 在游戏设置部分新增音效相关常量
SOUND_PATH = "Sound/"
BG_MUSIC = SOUND_PATH + "bg_music.ogg"
PLAYER_SHOOT_SOUND = SOUND_PATH + "laser1.ogg"
PLAYER_HURT_SOUND = SOUND_PATH + "hurt1.ogg"
LEVEL_UP_SOUND = SOUND_PATH + "powerup.ogg"
GAME_OVER_SOUND = SOUND_PATH + "game_over.ogg"
VICTORY_SOUND = SOUND_PATH + "victory.ogg"

# UI设置
UI_FONT = 'fusion-pixel-12px-monospaced-zh_hans.ttf'
UI_FONT_SIZE = 24
UI_COLOR = (255, 255, 255)
UI_ACCENT_COLOR = (255, 215, 0)  # 金色
HP_BAR_WIDTH = 200
HP_BAR_HEIGHT = 25
EXP_BAR_HEIGHT = 10


# 玩家设置
PLAYER_SPEED = 3  # 玩家移动速度
PLAYER_WIDTH = 80  # 玩家宽度
PLAYER_HEIGHT = 80  # 玩家高度
PLAYER_COLOR = (0, 255, 0)  # 玩家颜色

# Boss 设置
BOSS_WIDTH = 100  # Boss 宽度
BOSS_HEIGHT = 120  # Boss 高度
BOSS_COLOR = (255, 0, 0)  # Boss 颜色
BOSS_SPEED = 2.5  # Boss 移动速度
BOSS_SKILL_COOLDOWN = 180  # Boss技能冷却时间（帧数）
BOSS1_IMAGE_FOLDER = "Image\\Characters\\aobing\\"  # 第一个Boss的图片文件夹
BOSS2_IMAGE_FOLDER = "Image\\Characters\\aoguang\\"  # 第二个Boss的图片文件夹

# 子弹设置
BULLET_SPEED = 5  # 子弹速度
BULLET_WIDTH = 10  # 子弹宽度
BULLET_HEIGHT = 10  # 子弹高度
BULLET_COLOR = (255, 255, 0)  # 子弹颜色

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("二龙戏吒") 

# 初始化音效系统
pygame.mixer.init(frequency=22050, size=-16, channels=4)

try:
    # 背景音乐（使用音乐通道）
    pygame.mixer.music.load(BG_MUSIC)
    
    # 音效对象（使用Sound类）
    sound_player_shoot = pygame.mixer.Sound(PLAYER_SHOOT_SOUND)
    sound_player_hurt = pygame.mixer.Sound(PLAYER_HURT_SOUND)
    sound_level_up = pygame.mixer.Sound(LEVEL_UP_SOUND)
    sound_game_over = pygame.mixer.Sound(GAME_OVER_SOUND)
    sound_victory = pygame.mixer.Sound(VICTORY_SOUND)
    
    # 单独设置每个音效音量（0.0-1.0）
    pygame.mixer.music.set_volume(0.8)       # 背景音乐音量 30%
    sound_player_shoot.set_volume(0.1)      # 玩家射击音效 10%
    sound_player_hurt.set_volume(0.9)       # 玩家受伤音效 70%
    sound_level_up.set_volume(0.8)          # 升级音效 80%
    sound_game_over.set_volume(1.0)         # 游戏结束音效 100% 
    sound_victory.set_volume(0.6)           # 胜利音效 60%

except Exception as e:
    print(f"音效加载失败: {e}")

# 加载背景图片（新增代码）
try:
    background = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
    # 获取原始尺寸
    orig_width, orig_height = background.get_size()
    
    # 计算自适应缩放比例
    width_ratio = SCREEN_WIDTH / orig_width
    height_ratio = SCREEN_HEIGHT / orig_height
    scale_ratio = max(width_ratio, height_ratio)
    
    # 等比例缩放
    new_size = (
        int(orig_width * scale_ratio),
        int(orig_height * scale_ratio)
    )
    background = pygame.transform.smoothscale(background, new_size)
    
    # 居中裁剪
    x = (new_size[0] - SCREEN_WIDTH) // 2
    y = (new_size[1] - SCREEN_HEIGHT) // 2
    background = background.subsurface(pygame.Rect(x, y, SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception as e:
    print(f"背景加载失败: {e}")
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((0, 0, 75))  # 备用深蓝色背景
    # 添加错误提示文字
    font = pygame.font.Font(None, 30)
    text = font.render("背景加载失败", True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    background.blit(text, text_rect)

clock = pygame.time.Clock()

# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_or_angle, shooter=None, width=BULLET_WIDTH, height=BULLET_HEIGHT, speed=BULLET_SPEED):
        super().__init__()
        self.image = pygame.Surface((width, height))
        if shooter == boss1 or shooter == boss2:  # 根据发射者设置子弹颜色
            self.image.fill((255, 0, 0))  # Boss子弹颜色为红色
        else:
            self.image.fill(BULLET_COLOR)  # 玩家子弹颜色为黄色
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        if isinstance(target_or_angle, pygame.sprite.Sprite):
            self.target = target_or_angle  # 目标为Boss
            self.angle = None
        else:
            self.target = None
            self.angle = target_or_angle  # 角度
        self.speed = speed  # 子弹速度
        self.shooter = shooter  # 记录发射者

    def update(self):
        if self.target and (self.target.health <= 0 or not self.target.alive()):
            self.target = None
            
        if self.target:
            # 计算子弹移动方向
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            if distance != 0:
                dx /= distance
                dy /= distance
        else:
            # 根据角度计算子弹移动方向
            dx = math.cos(self.angle)
            dy = math.sin(self.angle)
        
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # 如果子弹飞出屏幕，则销毁子弹
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = []  # 存储动画帧
        for i in range(1, 11):  # 加载10帧动画图像
            frame = pygame.image.load(f"Image\\Characters\\nezha\\{i}.png").convert_alpha()
            frame = pygame.transform.scale(frame, (PLAYER_WIDTH, PLAYER_HEIGHT))  # 缩小图像
            self.frames.append(frame)
        self.current_frame = 0  # 当前显示的帧索引
        self.image = self.frames[self.current_frame]  # 初始图像
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
         # 新增：缩小15%的碰撞箱（保持中心）
        self.hitbox = self.rect.inflate(-int(PLAYER_WIDTH*0.3), -int(PLAYER_HEIGHT*0.3))
        self.hitbox.center = self.rect.center  # 初始对齐
        self.health = 100  # 玩家血量
        self.speed = PLAYER_SPEED  # 玩家移动速度
        self.prev_x = self.rect.x  # 记录上一次的x坐标
        self.prev_y = self.rect.y  # 记录上一次的y坐标
        self.shoot_cooldown = 10  # 射击冷却时间（帧数）
        self.current_cooldown = 0  # 当前冷却时间
        self.invulnerable_time = 0  # 无敌时间（帧数）
        self.flash_timer = 0  # 闪烁计时器
        self.animation_timer = 0  # 动画计时器
        self.experience = 0  # 经验值
        self.level = 1  # 玩家等级
        self.last_laser_damage = 0  # 新增：最后受激光伤害时间

    def update(self, keys):
        self.prev_x = self.rect.x  # 更新上一次的x坐标
        self.prev_y = self.rect.y  # 更新上一次的y坐标
        
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

        # 无敌时间内闪烁
        if self.invulnerable_time > 0:
            self.flash_timer += 1
            if self.flash_timer % 10 == 0:  # 每10帧切换一次可见性
                self.image.set_alpha(0 if self.image.get_alpha() == 255 else 255)
            self.invulnerable_time -= 1
        else:
            self.image.set_alpha(255)  # 无敌时间结束后恢复完全可见

        # 更新动画帧
        if self.rect.x != self.prev_x or self.rect.y != self.prev_y:  # 检查玩家是否移动
            self.animation_timer += 1
            if self.animation_timer >= 10:  # 每10帧切换一次动画帧
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                self.animation_timer = 0
        else:
            self.animation_timer = 0  # 如果玩家没有移动，重置动画计时器
        
        # 更新后同步碰撞箱位置
        self.hitbox.center = self.rect.center

    def shoot(self, target):

        if sound_player_shoot:
            sound_player_shoot.play()
        if self.level >= 3:
            angles = [math.pi / 2, -math.pi / 2, 0]  # 朝前后和正前方发射
        elif self.level == 2:
            angles = [math.pi / 2, -math.pi / 2]  # 朝前后发射
        else:
            angles = [0]  # 只朝正前方发射

        bullets = []
        for angle in angles:
            # 子弹先朝指定角度移动一段距离，然后再开始追踪敌人
            bullet = Bullet(self.rect.centerx, self.rect.top, angle, shooter=self)
            bullet.speed = 10  # 设置初始速度较高，以便快速朝指定角度移动
            bullet.rect.x += math.cos(angle) * 50  # 移动子弹一段距离
            bullet.rect.y += math.sin(angle) * 50  # 移动子弹一段距离
            bullet.target = target  # 设置目标为敌人
            bullet.speed = BULLET_SPEED  # 重置子弹速度为正常速度
            all_sprites.add(bullet)
            bullets.append(bullet)
        return bullets

    def take_damage(self, damage):
        if self.invulnerable_time <= 0:  # 只有在无敌时间结束后才能受到伤害
            if sound_player_hurt:
                sound_player_hurt.play()
            self.health -= damage
            self.invulnerable_time = 60  # 设置无敌时间为60帧（1秒）
            self.experience = 0  # 经验值清零
            if self.level > 1:  # 如果等级大于1，则减少等级
                self.level -= 1

    def gain_experience(self, amount):
        prev_level = self.level
        self.experience += amount
        
        if self.level == 1 and self.experience >= 50:
            self.level = 2
            self.experience -= 50
            ui_effects.add_message("LEVEL UP!", (0,255,0))
            ui_effects.level_up_effect()
            if sound_level_up:
                sound_level_up.play()
            
        if self.level == 2 and self.experience >= 100:
            self.level = 3
            self.experience = 0
            ui_effects.add_message("MAX LEVEL!", (255,215,0))
            ui_effects.level_up_effect()
            self.experience_locked = True  # 添加缺失的属性
            if sound_level_up:
                sound_level_up.play()
    
    def draw_ui(self, screen):
        # 绘制玩家血条
        pygame.draw.rect(screen, (50,50,50), (20, 20, HP_BAR_WIDTH, HP_BAR_HEIGHT))
        current_hp_width = (self.health / 100) * HP_BAR_WIDTH
        pygame.draw.rect(screen, (255,40,40), (20, 20, current_hp_width, HP_BAR_HEIGHT))
        
        # 动态血条效果
        if self.invulnerable_time > 0:
            flash_width = HP_BAR_WIDTH * (self.invulnerable_time / 60)
            pygame.draw.rect(screen, (255,255,255,100), (20, 20, flash_width, HP_BAR_HEIGHT))

        # 经验条
        pygame.draw.rect(screen, (50,50,50), (20, 55, HP_BAR_WIDTH, EXP_BAR_HEIGHT))
        exp_percent = self.experience / (50 if self.level < 2 else 100)
        pygame.draw.rect(screen, (0,200,255), (20, 55, HP_BAR_WIDTH*exp_percent, EXP_BAR_HEIGHT))

        # 等级徽章
        badge_rect = pygame.Rect(HP_BAR_WIDTH + 40, 20, 40, 40)
        pygame.draw.ellipse(screen, UI_ACCENT_COLOR, badge_rect)
        level_text = font.render(str(self.level), True, (0,0,0))
        screen.blit(level_text, (badge_rect.centerx-5, badge_rect.centery-10))


# 新增：小球类
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y, width=20, height=20, color=(255, 255, 255)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.start_time = pygame.time.get_ticks()  # 记录小球出现的时间
        self.duration = 10000  # 小球持续时间（毫秒）

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # 碰到屏幕边缘反弹
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1

        # 检查小球是否超过持续时间
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()

# Boss 类
class Boss(pygame.sprite.Sprite):
    def __init__(self, health_multiplier=1, image_folder="Image\\Characters\\aobing\\", frame_count=10, skill = [1,2,3,4]):
        super().__init__()
        self.frames = []  # 存储动画帧
        for i in range(1, frame_count + 1):  # 根据frame_count加载相应数量的动画图像
            frame = pygame.image.load(f"{image_folder}{i}.png").convert_alpha()
            frame = pygame.transform.scale(frame, (BOSS_WIDTH, BOSS_HEIGHT))  # 缩小图像
            self.frames.append(frame)
        self.current_frame = 0  # 当前显示的帧索引
        self.image = self.frames[self.current_frame]  # 初始图像
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        # 新增：缩小20%的碰撞箱
        self.hitbox = self.rect.inflate(-int(BOSS_WIDTH*0.4), -int(BOSS_HEIGHT*0.4))
        self.hitbox.center = self.rect.center
        self.health = 2000 * health_multiplier  # Boss血量
        self.max_health = self.health  # 记录初始血量
        self.speed = BOSS_SPEED  # Boss移动速度
        self.attack_cooldown = 60  # 攻击冷却时间（帧数）
        self.current_cooldown = 0  # 当前冷却时间
        self.chase_distance = 150  # 追踪距离阈值
        self.move_towards_player_distance = 1  # 移动朝向玩家的距离阈值
        self.is_aiming = False  # 是否正在瞄准
        self.aim_timer = 0  # 瞄准计时器
        self.skill_cooldown = int(BOSS_SKILL_COOLDOWN * 0.8)  # 技能冷却时间
        self.current_skill_cooldown = 0  # 当前技能冷却时间
        # 新增技能子弹属性
        self.skill1_bullet_speed = 10  # 技能1子弹速度
        self.skill1_bullet_size = (10, 20)  # 技能1子弹大小
        self.skill2_bullet_speed = 3  # 技能2子弹速度
        self.skill2_bullet_size = (15, 30)  # 技能2子弹大小
        # 新增停止计时器
        self.stop_timer = 0  # 初始化停止计时器为0
        # 新增激光技能属性
        self.laser_timer = 0  # 激光技能计时器
        self.laser_duration = 120  # 激光持续时间（帧数）
        self.laser_flash_timer = 0  # 激光闪烁计时器
        self.laser_flash_duration = 60  # 激光闪烁持续时间（帧数）
        self.animation_timer = 0  # 动画计时器
        self.health_multiplier = health_multiplier  # 血量倍数
        self.flash_count = 0  # 闪烁次数
        self.max_flash_count = 5  # 最大闪烁次数
        self.skill = skill
        self.skill_states = {}  # 技能执行状态跟踪
        self.laser_segments = []  # 存储每条激光的碰撞多边形
        self.is_alive = True  # 新增存活状态
    def use_skill(self):
        skill_choice = random.choice(self.skill)
        if skill_choice == 1:
            angle = math.atan2(player.rect.centery - self.rect.centery, player.rect.centerx - self.rect.centerx)
            bullet = Bullet(self.rect.centerx, self.rect.centery, angle, shooter=self, width=self.skill1_bullet_size[0], height=self.skill1_bullet_size[1], speed=self.skill1_bullet_speed)
            all_sprites.add(bullet)
            bullets.add(bullet)
        elif skill_choice == 2:
            self.stop_timer = 60
            for i in range(12):
                angle = i * (2 * math.pi / 12)
                bullet = Bullet(self.rect.centerx, self.rect.centery, angle, shooter=self, width=self.skill2_bullet_size[0], height=self.skill2_bullet_size[1], speed=self.skill2_bullet_speed)
                all_sprites.add(bullet)
                bullets.add(bullet)
        elif skill_choice == 3:
            speed_x = random.uniform(-5, 5)  # 随机水平速度
            speed_y = random.uniform(-5, 5)  # 随机垂直速度
            ball = Ball(self.rect.centerx, self.rect.centery, speed_x, speed_y)
            all_sprites.add(ball)
            balls.add(ball)
        elif skill_choice == 4:  # 第四个技能
            self.stop_timer = 60  # 停止移动
            self.laser_flash_timer = self.laser_flash_duration  # 开始闪烁
            self.laser_timer = self.laser_duration  # 开始激光
            self.laser_preaim_timer = self.laser_flash_duration  # 预瞄计时器
        elif skill_choice == 5:
            # 初始化技能5状态（12波子弹，每波12发）
            self.skill_states['skill5'] = {'wave': 0, 'delay': 0, 'total_waves': 12}
        elif skill_choice == 6:
            # 初始化技能6状态（生成3波小球，每波2个）
            self.skill_states['skill6'] = {'wave': 0, 'delay': 0, 'total_waves': 3}
        elif skill_choice == 7:
            # 初始化技能7状态（3发子弹，间隔30帧）
            self.skill_states['skill7'] = {'shot': 0, 'delay': 0, 'total_shots': 3}

    def draw_health_bar(self, screen):
        if self.health <= 0 or not self.is_alive:
            return

        # 修正血量比率计算，限制在0-1之间
        health_ratio = max(0.0, min(1.0, self.health / self.max_health))
        red = int(255 * (1 - health_ratio))
        green = int(255 * health_ratio)
        
        # 确保颜色值在有效范围内
        red = max(0, min(red, 255))
        green = max(0, min(green, 255))
        health_color = (red, green, 40)

        # 保持其他绘制逻辑不变
        bar_bg = pygame.Rect(SCREEN_WIDTH//2 - 150, 10, 300, 25)
        pygame.draw.rect(screen, (50,50,50), bar_bg)
        health_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, 10, 300*health_ratio, 25)
        pygame.draw.rect(screen, health_color, health_rect)
        pygame.draw.rect(screen, UI_COLOR, bar_bg, 3)
        
        health_text = font.render(f"{int(self.health)}/{self.max_health}", True, UI_COLOR)
        screen.blit(health_text, (bar_bg.centerx - health_text.get_width()//2, bar_bg.centery - 8))
    def aim_at_player(self):
        if self.aim_timer > 0:
            self.aim_timer -= 1

    def move_towards_player(self):
        # 计算Boss与玩家之间的距离
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果Boss与玩家的距离大于移动朝向玩家的距离阈值，则移动朝向玩家
        if distance > self.move_towards_player_distance:
            dx /= distance
            dy /= distance
            self.rect.x += dx * self.speed / 2
            self.rect.y += dy * self.speed / 2

    def update(self):

        self.process_skill_states()

        if self.current_cooldown > 0:
            self.current_cooldown -= 1

        if self.current_skill_cooldown > 0:
            self.current_skill_cooldown -= 1
        else:
            self.use_skill()  # 使用技能
            self.current_skill_cooldown = self.skill_cooldown  # 重置技能冷却时间

        # 如果Boss在停止移动计时器内，则不移动
        if self.stop_timer > 0:
            self.stop_timer -= 1
        else:
            if self.is_aiming:
                self.aim_at_player()
            else:
                self.move_towards_player()  # 确保在不冲刺且不瞄准时移动朝向玩家

        # 激光技能逻辑
        if self.laser_timer > 0:
            self.laser_timer -= 1
            # 生成激光碰撞区域（每帧更新）
            self.laser_segments = []
            if self.laser_preaim_timer <= 0:
                laser_width = 20
                for i in range(10):
                    angle = i * (math.pi / 5)
                    end_x = self.rect.centerx + math.cos(angle) * SCREEN_WIDTH
                    end_y = self.rect.centery + math.sin(angle) * SCREEN_HEIGHT
                    dx = end_x - self.rect.centerx
                    dy = end_y - self.rect.centery
                    offset_x = -dy * (laser_width / 2) / math.sqrt(dx**2 + dy**2)
                    offset_y = dx * (laser_width / 2) / math.sqrt(dx**2 + dy**2)
                    p1 = (self.rect.centerx + offset_x, self.rect.centery + offset_y)
                    p2 = (self.rect.centerx - offset_x, self.rect.centery - offset_y)
                    p3 = (end_x - offset_x, end_y - offset_y)
                    p4 = (end_x + offset_x, end_y + offset_y)
                    self.laser_segments.append([p1, p2, p3, p4])

        # 新增：Boss死亡时立即终止所有技能状态
        if self.health <= 0:
            self.laser_flash_timer = 0
            self.laser_timer = 0
            self.laser_preaim_timer = 0
            self.laser_segments = []
            return  # 关键！立即退出update方法

        # 修复计时器更新顺序（关键修改↓↓↓）
        if self.laser_flash_timer > 0:
            self.laser_flash_timer -= 1
            # 新增：闪烁期间同步减少预瞄计时器
            self.laser_preaim_timer = self.laser_flash_timer 

        # 更新动画帧
        self.animation_timer += 1
        if self.animation_timer >= 10:  # 每10帧切换一次动画帧
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.animation_timer = 0

        self.hitbox.center = self.rect.center
    def process_skill_states(self):
        # 处理技能5：环形弹幕
        if 'skill5' in self.skill_states:
            state = self.skill_states['skill5']
            if state['delay'] <= 0:
                # 发射一波子弹（12方向）
                for i in range(12):
                    angle = i * (2 * math.pi / 12)
                    bullet = Bullet(self.rect.centerx, self.rect.centery, angle, shooter=self, 
                                   width=self.skill2_bullet_size[0], height=self.skill2_bullet_size[1], 
                                   speed=self.skill2_bullet_speed)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                state['wave'] += 1
                state['delay'] = 10  # 10帧后发射下一波
                if state['wave'] >= state['total_waves']:
                    del self.skill_states['skill5']
            else:
                state['delay'] -= 1

        # 处理技能6：多重小球
        if 'skill6' in self.skill_states:
            state = self.skill_states['skill6']
            if state['delay'] <= 0:
                # 生成一波小球
                for _ in range(2):
                    speed_x = random.uniform(-5, 5)
                    speed_y = random.uniform(-5, 5)
                    ball = Ball(self.rect.centerx, self.rect.centery, speed_x, speed_y)
                    all_sprites.add(ball)
                    balls.add(ball)
                state['wave'] += 1
                state['delay'] = 30  # 30帧后生成下一波
                if state['wave'] >= state['total_waves']:
                    del self.skill_states['skill6']
            else:
                state['delay'] -= 1

        # 处理技能7：连续射击
        if 'skill7' in self.skill_states:
            state = self.skill_states['skill7']
            if state['delay'] <= 0:
                # 发射一发追踪弹
                angle = math.atan2(player.rect.centery - self.rect.centery, 
                                  player.rect.centerx - self.rect.centerx)
                bullet = Bullet(self.rect.centerx, self.rect.centery, angle, shooter=self,
                               width=self.skill1_bullet_size[0], height=self.skill1_bullet_size[1],
                               speed=self.skill1_bullet_speed)
                all_sprites.add(bullet)
                bullets.add(bullet)
                state['shot'] += 1
                state['delay'] = 30  # 30帧后发射下一发（约0.5秒）
                if state['shot'] >= state['total_shots']:
                    del self.skill_states['skill7']
            else:
                state['delay'] -= 1

# 新增UI特效管理类
class UIEffects:
    def __init__(self):
        self.messages = []
        self.screen_shake = 0
        
    def add_message(self, text, color=UI_ACCENT_COLOR, duration=2):
        self.messages.append({
            "text": text,
            "color": color,
            "duration": duration * FPS,
            "timer": 0
        })
        
    def level_up_effect(self):
        self.screen_shake = 10
        
    def update(self):
        # 消息更新
        for msg in self.messages[:]:
            msg["timer"] += 1
            if msg["timer"] >= msg["duration"]:
                self.messages.remove(msg)
        
        # 屏幕震动衰减
        if self.screen_shake > 0:
            self.screen_shake -= 1

    def draw(self, screen):
        # 绘制浮动消息
        y_offset = 100
        for msg in self.messages:
            alpha = 255 * (1 - msg["timer"]/msg["duration"])
            text_surf = font.render(msg["text"], True, msg["color"])
            text_surf.set_alpha(alpha)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 40

        # 屏幕震动效果
        if self.screen_shake > 0:
            shake_offset = (
                random.randint(-self.screen_shake, self.screen_shake),
                random.randint(-self.screen_shake, self.screen_shake)
            )
            screen.blit(screen.copy(), shake_offset)


def reset_game():

    pygame.mixer.music.play(-1)

    global game_over_sound_played, victory_sound_played
    global player, boss1, boss2, all_sprites, bullets, balls
    global boss1_survived, boss2_survived, game_over, game_won

    # 清空所有精灵组
    all_sprites.empty()
    bullets.empty()
    balls.empty()

    # 重新初始化玩家
    player = Player()
    
    # 重新初始化Boss（带死亡动画重置）
    boss1 = Boss(frame_count=10)
    boss2 = Boss(frame_count=10, image_folder=BOSS2_IMAGE_FOLDER, skill=[5,6,7])
    
    # 重置游戏状态
    all_sprites.add(player, boss1)
    boss1_survived = True
    boss2_survived = False
    game_over = False
    game_won = False
    game_over_sound_played = False
    victory_sound_played = False

# 修改为精确多边形检测：
def is_point_in_polygon(point, polygon):
    # 使用射线法进行精确碰撞检测
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n+1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# 优化后的游戏结束界面
def draw_game_over(screen):

    global game_over_sound_played, victory_sound_played
    
    # 只在第一次进入时播放音效
    if game_over and not game_over_sound_played:
        pygame.mixer.music.stop()
        if sound_game_over:
            sound_game_over.play()
        game_over_sound_played = True  # 标记已播放
        
    elif game_won and not victory_sound_played:
        pygame.mixer.music.stop()
        if sound_victory:
            sound_victory.play()
        victory_sound_played = True  # 标记已播放
            
    # 半透明遮罩
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0,0,0))
    screen.blit(overlay, (0,0))
    
    # 结果文字
    result_font = pygame.font.Font(UI_FONT, 72)
    result_text = "胜利!" if game_won else "败北"
    text_surf = result_font.render(result_text, True, (0,255,0) if game_won else (255,0,0))
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
    
    # 添加文字描边
    border_surf = result_font.render(result_text, True, (0,0,0))
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        screen.blit(border_surf, text_rect.move(dx, dy))
    screen.blit(text_surf, text_rect)
    
    # 重新开始按钮
    button_rect = pygame.Rect(0,0,300,60)
    button_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3)
    
    # 修改按钮点击区域检测
    mouse_pos = pygame.mouse.get_pos()
    is_hover = button_rect.collidepoint(mouse_pos)
    
    # 按钮背景
    pygame.draw.rect(screen, (30,30,30), button_rect, border_radius=10)
    if is_hover:
        pygame.draw.rect(screen, (255,215,0), button_rect, 3, border_radius=10)
    else:
        pygame.draw.rect(screen, UI_COLOR, button_rect, 3, border_radius=10)
        
    # 按钮文字
    btn_text = font.render("点击重生", True, (255,215,0) if is_hover else UI_COLOR)
    screen.blit(btn_text, btn_text.get_rect(center=button_rect.center))

    # 统一按钮定义（居中显示）
    button_rect = pygame.Rect(0,0,300,60)
    button_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT*2//3)
    
    # 绘制代码...
    return button_rect  # 返回当前帧的按钮区域

# 设置游戏元素
player = Player()
boss1 = Boss(frame_count=10)
boss2 = Boss(frame_count=10, image_folder="Image\\Characters\\aoguang\\", skill = [5, 6, 7])  # 指定第二个Boss的动画帧数为10

# 初始化UI
ui_effects = UIEffects()
font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

# 初始化音效
pygame.mixer.music.play(-1)  # -1表示循环播放
game_over_sound_played = False
victory_sound_played = False

all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(boss1)

bullets = pygame.sprite.Group()
balls = pygame.sprite.Group()  # 小球组

# 控制是否绘制碰撞箱的变量
draw_collision_boxes = False

# boss1和boss2是否复活
boss1_survived = True
boss2_survived = False

# 游戏主循环
running = True
game_over = False
game_won = False  # 新增：跟踪游戏是否胜利
first_boss = None  # 初始化first_boss为None

# 定义restart_button
restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)

while running:
    clock.tick(FPS)

    current_restart_button = None
    
    # 在绘制阶段获取当前按钮区域
    if game_over or game_won:
        current_restart_button = draw_game_over(screen)

    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_restart_button and current_restart_button.collidepoint(event.pos):
                reset_game()

        # 处理b键按下事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                draw_collision_boxes = not draw_collision_boxes

    # 只在游戏进行时更新游戏逻辑
    if not game_over and not game_won:
        # 获取按键输入
        keys = pygame.key.get_pressed()
        
        # 更新玩家状态（仅在游戏进行时）
        player.update(keys)
        
        # 更新Boss状态
        if boss1_survived:
            boss1.update()
        if boss2_survived:
            boss2.update()
        
        # 更新弹幕状态
        bullets.update()
        balls.update()

        # 如果空格键被按下且冷却时间已过，则发射子弹
        if keys[pygame.K_SPACE] and player.current_cooldown <= 0:  # 检测空格键是否被按下且冷却时间已过
            
            
            # 找到最近的Boss
            nearest_boss = min([boss1] if boss1_survived else [] + ([boss2] if boss2_survived else []), key=lambda b: math.sqrt((b.rect.centerx - player.rect.centerx)**2 + (b.rect.centery - player.rect.centery)**2))
            bullet_list = player.shoot(nearest_boss)  # 传递最近的Boss作为目标
            for bullet in bullet_list:
                all_sprites.add(bullet)
                bullets.add(bullet)
            player.current_cooldown = player.shoot_cooldown  # 重置冷却时间

        # 更新冷却时间
        if player.current_cooldown > 0:
            player.current_cooldown -= 1

        # 子弹与 Boss 碰撞检测
        for bullet in bullets:
            if boss1_survived and bullet.rect.colliderect(boss1.hitbox) and bullet.shooter != boss1:  # 忽略Boss对自己发射的子弹
                boss1.health -= 10  # 伤害
                player.gain_experience(1)  # 玩家获得经验值
                bullet.kill()  # 销毁子弹
                if boss1.health <= 0:
                    # 从all_sprites组中移除第一个Boss
                    all_sprites.remove(boss1)
                    boss1_survived = False
                    boss1.kill()
                    boss1.laser_timer = 0
                    boss1.laser_flash_timer = 0
                    boss1.laser_preaim_timer = 0
                    boss2_survived = True
                    boss2 = Boss(
                        health_multiplier=2,  # 将血量倍数设为2
                        frame_count=10,
                        image_folder="Image\\Characters\\aoguang\\",
                        skill=[5, 6, 7]
                    )
                    boss2.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)  # 初始化第二个Boss的位置
                    all_sprites.add(boss2)  # 添加第二个Boss到all_sprites组
            if boss2_survived and bullet.rect.colliderect(boss2.hitbox) and bullet.shooter != boss2:
                boss2.health -= 10 
                player.gain_experience(1)  # 玩家获得经验值
                bullet.kill()
                if boss2.health <= 0:
                    # 从all_sprites组中移除第二个Boss
                    all_sprites.remove(boss2)
                    boss2_survived = False

        # 子弹与 玩家 碰撞检测
        for bullet in bullets:
            if bullet.rect.colliderect(player.hitbox) and (bullet.shooter == boss1 or bullet.shooter == boss2): # 只处理Boss发射的子弹
                player.take_damage(10)
                bullet.kill()

        # 玩家与 Boss 碰撞检测
        if player.hitbox.colliderect(boss1.hitbox):
            player.take_damage(10)  # 玩家碰撞Boss时掉血
        if player.hitbox.colliderect(boss2.hitbox):
            player.take_damage(10)  # 玩家碰撞第一个Boss时掉血

        # 检查玩家血量是否小于等于0
        if player.health <= 0:
            print("游戏失败!")  # 游戏失败提示
            game_over = True

        # 检查所有Boss是否死亡
        if boss1.health <= 0 and boss2.health <= 0:
            print("游戏胜利!")  # 游戏胜利提示
            game_won = True

    # 绘制所有元素
    screen.fill((0, 0, 0))  # 清空屏幕
    screen.blit(background, (0, 0))  # 先绘制背景
    all_sprites.draw(screen)  # 绘制所有精灵

    # 新增：绘制玩家UI
    player.draw_ui(screen)
    
    # 新增：绘制Boss血条
    if boss1_survived:
        boss1.draw_health_bar(screen)
    if boss2_survived:
        boss2.draw_health_bar(screen)
    
    # 新增：绘制UI特效
    ui_effects.update()
    ui_effects.draw(screen)

    # 绘制碰撞箱
    if draw_collision_boxes:
        # 玩家碰撞箱
        pygame.draw.rect(screen, (255, 0, 0), player.hitbox, 2)
        
        # Boss碰撞箱
        if boss1_survived:
            pygame.draw.rect(screen, (0, 0, 255), boss1.hitbox, 2)
        if boss2_survived:
            pygame.draw.rect(screen, (0, 0, 255), boss2.hitbox, 2)
    
        # 子弹和小球保持原有碰撞箱
        for bullet in bullets:
            pygame.draw.rect(screen, (0, 255, 0), bullet.rect, 2)
        for ball in balls:
            pygame.draw.rect(screen, (255, 255, 0), ball.rect, 2)

    # 绘制激光技能闪烁射线
    if boss1_survived and boss1.laser_flash_timer > 0:
        for i in range(10):
            angle = i * (math.pi / 5)
            end_x = boss1.rect.centerx + math.cos(angle) * SCREEN_WIDTH
            end_y = boss1.rect.centery + math.sin(angle) * SCREEN_HEIGHT
            pygame.draw.line(screen, (255, 255, 0), boss1.rect.center, (end_x, end_y), 2)


    # 绘制激光束
    if boss1.laser_timer > 0:
        if boss1.laser_preaim_timer > 0:  # 检查预瞄计时器
            boss1.laser_preaim_timer -= 1  # 减少预瞄计时器
        else:  # 预瞄结束后发射激光
            laser_width = 20  # 激光宽度
            for i in range(10):
                angle = i * (math.pi / 5)
                end_x = boss1.rect.centerx + math.cos(angle) * SCREEN_WIDTH
                end_y = boss1.rect.centery + math.sin(angle) * SCREEN_HEIGHT
                # 计算激光的两个端点
                dx = end_x - boss1.rect.centerx
                dy = end_y - boss1.rect.centery
                # 计算激光宽度方向的偏移量
                offset_x = -dy * (laser_width / 2) / math.sqrt(dx**2 + dy**2)
                offset_y = dx * (laser_width / 2) / math.sqrt(dx**2 + dy**2)
                # 计算激光的四个顶点
                p1 = (boss1.rect.centerx + offset_x, boss1.rect.centery + offset_y)
                p2 = (boss1.rect.centerx - offset_x, boss1.rect.centery - offset_y)
                p3 = (end_x - offset_x, end_y - offset_y)
                p4 = (end_x + offset_x, end_y + offset_y)
                # 绘制激光矩形
                pygame.draw.polygon(screen, (255, 255, 0), [p1, p2, p3, p4])
            boss1.laser_timer -= 1
            if boss1.laser_timer == 0:
                boss1.stop_timer = 0  # 激光结束后恢复移动

    # 激光伤害检测
    if boss1_survived and boss1.laser_timer > 0 and boss1.laser_preaim_timer <= 0:
        current_time = pygame.time.get_ticks()
        if (current_time - player.last_laser_damage) > 500:
            player_center = player.hitbox.center
            for segment in boss1.laser_segments:
                if is_point_in_polygon(player_center, segment):
                    player.take_damage(20)
                    player.last_laser_damage = current_time
                    break

    # 显示玩家血量和 Boss 血量
    font = pygame.font.Font('fusion-pixel-12px-monospaced-zh_hans.ttf', 20)
    player_health_text = font.render(f"哪吒: {player.health}", True, (255, 255, 255))
    boss_health_text = font.render(f"敖丙: {boss1.health}", True, (255, 255, 255))
    if boss1_survived:
        boss_health_text = font.render(f"敖丙: {boss1.health}", True, (255, 255, 255))
    if boss2_survived: 
        boss_health_text = font.render(f"敖光: {boss1.health}", True, (255, 255, 255))
    screen.blit(player_health_text, (10, 10))
    screen.blit(boss_health_text, (SCREEN_WIDTH - boss_health_text.get_width() - 10, 10))

    # 显示玩家经验值和等级
    player_experience_text = font.render(f"经验值: {player.experience}", True, (255, 255, 255))
    player_level_text = font.render(f"等级: {player.level}", True, (255, 255, 255))
    screen.blit(player_experience_text, (10, 70))
    screen.blit(player_level_text, (10, 100))

    # 绘制 Boss 血条
    if boss1_survived:
        boss1.draw_health_bar(screen)
    if boss2_survived:
        boss2.draw_health_bar(screen)

        # 修改后的游戏结束界面
    if game_over or game_won:
        draw_game_over(screen)
    
    # 刷新屏幕
    pygame.display.flip()

# 退出 Pygame
pygame.quit()

