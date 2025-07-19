import pygame
import math
import random

# 初期化
pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("遊園地スピードラン")
clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
YELLOW = (255, 215, 0)
PURPLE = (138, 43, 226)
ORANGE = (255, 140, 0)
PINK = (255, 182, 193)
DARK_BLUE = (0, 0, 139)
SKY_BLUE = (135, 206, 235)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.width = 30
        self.height = 40
        self.on_ground = False
        self.jump_power = -36  # 2倍のジャンプ力
        self.speed = 16  # 2倍のスピード
        self.max_speed = 30  # 2倍の最高速度
        self.acceleration = 3.0  # 加速度を大幅に上げる
        self.friction = 0.85
        self.gravity = 0.6
        self.trail = []  # スピードトレイル用
        
    def update(self):
        # 重力の適用
        if not self.on_ground:
            self.vel_y += self.gravity
            
        # 速度制限
        self.vel_y = min(self.vel_y, 20)
        
        # 位置の更新
        self.x += self.vel_x
        self.y += self.vel_y
        
        # トレイルの更新
        if abs(self.vel_x) > 5:
            self.trail.append((self.x + self.width//2, self.y + self.height//2))
            if len(self.trail) > 10:
                self.trail.pop(0)
                
    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            
    def move_left(self):
        self.vel_x = max(self.vel_x - self.acceleration, -self.max_speed)
        
    def move_right(self):
        self.vel_x = min(self.vel_x + self.acceleration, self.max_speed)
        
    def apply_friction(self):
        if self.on_ground:
            self.vel_x *= self.friction
            
    def draw(self, screen, camera_x, camera_y):
        # トレイルの描画
        for i, pos in enumerate(self.trail):
            alpha = i * 25
            color = (100, 149, 237, alpha) if alpha < 255 else BLUE
            pygame.draw.circle(screen, color, 
                             (int(pos[0] - camera_x), int(pos[1] - camera_y)), 
                             max(2, i//2))
        
        # プレイヤーの描画（ソニック風のキャラクター）
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
        
        # 体
        pygame.draw.ellipse(screen, BLUE, (x, y + 10, self.width, self.height - 10))
        # 頭
        pygame.draw.circle(screen, BLUE, (x + self.width//2, y + 15), 15)
        # 目
        pygame.draw.circle(screen, WHITE, (x + self.width//2 + 5, y + 12), 5)
        pygame.draw.circle(screen, BLACK, (x + self.width//2 + 7, y + 12), 2)
        # スピード線
        if abs(self.vel_x) > 8:
            for i in range(3):
                start_x = x - 10 if self.vel_x > 0 else x + self.width + 10
                pygame.draw.line(screen, WHITE, 
                               (start_x, y + 10 + i*10), 
                               (start_x - self.vel_x*2, y + 10 + i*10), 2)

class Attraction:
    def __init__(self, x, y, width, height, color, name):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.name = name
        self.animation_offset = 0
        
    def update(self):
        # アトラクションごとのアニメーション
        self.animation_offset = (self.animation_offset + 1) % 360
        
    def draw(self, screen, camera_x, camera_y):
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
        
        if self.name == "ジェットコースター":
            # レールの描画
            for i in range(0, self.width, 20):
                rail_y = y + math.sin((i + self.animation_offset) * 0.05) * 30
                pygame.draw.rect(screen, self.color, (x + i, rail_y, 15, 10))
                pygame.draw.rect(screen, BLACK, (x + i, rail_y + 10, 15, 5))
        elif self.name == "観覧車":
            # 観覧車の描画
            center_x = x + self.width // 2
            center_y = y + self.height // 2
            pygame.draw.circle(screen, self.color, (center_x, center_y), self.width//2, 5)
            # ゴンドラ
            for i in range(8):
                angle = (i * 45 + self.animation_offset) * math.pi / 180
                gx = center_x + math.cos(angle) * (self.width//2 - 10)
                gy = center_y + math.sin(angle) * (self.width//2 - 10)
                pygame.draw.rect(screen, YELLOW, (gx-10, gy-10, 20, 20))
        elif self.name == "メリーゴーランド":
            # メリーゴーランドの描画
            center_x = x + self.width // 2
            center_y = y + self.height - 30
            pygame.draw.ellipse(screen, self.color, (x, y + self.height - 60, self.width, 60))
            # 馬
            for i in range(6):
                angle = (i * 60 + self.animation_offset * 2) * math.pi / 180
                hx = center_x + math.cos(angle) * 40
                hy = center_y + math.sin(angle * 0.5) * 10 - 20
                pygame.draw.rect(screen, PINK, (hx-10, hy-20, 20, 30))
        else:
            # 通常のアトラクション
            pygame.draw.rect(screen, self.color, (x, y, self.width, self.height))
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def draw(self, screen, camera_x, camera_y):
        pygame.draw.rect(screen, GREEN, 
                        (int(self.x - camera_x), int(self.y - camera_y), 
                         self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.collected = False
        self.animation_offset = random.uniform(0, 360)
        
    def update(self):
        self.animation_offset = (self.animation_offset + 5) % 360
        
    def draw(self, screen, camera_x, camera_y):
        if not self.collected:
            x = int(self.x - camera_x)
            y = int(self.y - camera_y + math.sin(self.animation_offset * 0.05) * 5)
            
            # コインの本体
            pygame.draw.circle(screen, YELLOW, (x, y), self.radius)
            pygame.draw.circle(screen, ORANGE, (x, y), self.radius, 3)
            
            # コインの「C」マーク
            font = pygame.font.Font(None, 24)
            text = font.render("C", True, ORANGE)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)
            
    def collect(self):
        self.collected = True

class RollerCoaster:
    def __init__(self, start_x, start_y, track_points):
        self.track_points = track_points  # レールのポイント[(x, y), ...]
        self.carts = []  # トロッコのリスト
        self.cart_spacing = 150  # トロッコ間の間隔
        
        # トロッコを3台作成
        for i in range(3):
            self.carts.append({
                'progress': i * self.cart_spacing,  # トラック上の位置
                'x': start_x,
                'y': start_y,
                'width': 60,
                'height': 40,
                'passenger': None  # 乗客（プレイヤー）
            })
            
    def get_track_position(self, progress):
        # プログレス値からトラック上の位置を計算
        total_length = 0
        segments = []
        
        # 各セグメントの長さを計算
        for i in range(len(self.track_points) - 1):
            x1, y1 = self.track_points[i]
            x2, y2 = self.track_points[i + 1]
            length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            segments.append(length)
            total_length += length
            
        # 循環するプログレス
        progress = progress % total_length
        
        # どのセグメントにいるか特定
        current_length = 0
        for i, seg_length in enumerate(segments):
            if current_length + seg_length > progress:
                # このセグメント内での割合
                t = (progress - current_length) / seg_length
                x1, y1 = self.track_points[i]
                x2, y2 = self.track_points[i + 1]
                
                # 線形補間で位置を計算
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                
                # 進行方向（角度）も計算
                angle = math.atan2(y2 - y1, x2 - x1)
                
                return x, y, angle
            current_length += seg_length
            
        return self.track_points[0][0], self.track_points[0][1], 0
        
    def update(self):
        # 各トロッコを更新
        for cart in self.carts:
            # トロッコを前進（3倍速）
            cart['progress'] += 9  # スピード3倍
            
            # 位置と角度を更新
            x, y, angle = self.get_track_position(cart['progress'])
            cart['x'] = x
            cart['y'] = y
            cart['angle'] = angle
            
            # 乗客がいる場合、位置を同期
            if cart['passenger']:
                cart['passenger'].x = x - cart['passenger'].width // 2
                cart['passenger'].y = y - cart['height'] - cart['passenger'].height + 10
                cart['passenger'].vel_x = math.cos(angle) * 9  # 速度も3倍
                cart['passenger'].vel_y = math.sin(angle) * 9
                
    def draw(self, screen, camera_x, camera_y):
        # レールを描画
        for i in range(len(self.track_points) - 1):
            x1, y1 = self.track_points[i]
            x2, y2 = self.track_points[i + 1]
            
            # レール
            pygame.draw.line(screen, BLACK, 
                           (x1 - camera_x, y1 - camera_y),
                           (x2 - camera_x, y2 - camera_y), 12)  # より太いレール
            pygame.draw.line(screen, (50, 50, 50), 
                           (x1 - camera_x, y1 - camera_y - 2),
                           (x2 - camera_x, y2 - camera_y - 2), 8)  # レールの光沢
            # 枕木
            if i % 3 == 0:
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                angle = math.atan2(y2 - y1, x2 - x1) + math.pi / 2
                dx = math.cos(angle) * 20
                dy = math.sin(angle) * 20
                pygame.draw.line(screen, (139, 69, 19),
                               (mid_x - dx - camera_x, mid_y - dy - camera_y),
                               (mid_x + dx - camera_x, mid_y + dy - camera_y), 6)
        
        # トロッコを描画
        for cart in self.carts:
            x = int(cart['x'] - camera_x)
            y = int(cart['y'] - camera_y)
            
            # トロッコ本体（より大きく）
            cart_width = 80
            cart_height = 50
            pygame.draw.rect(screen, RED, 
                           (x - cart_width//2, y - cart_height//2,
                            cart_width, cart_height))
            # 座席
            pygame.draw.rect(screen, (100, 0, 0),
                           (x - cart_width//2 + 5, y - cart_height//2 + 5,
                            cart_width - 10, cart_height - 10))
            # 車輪
            pygame.draw.circle(screen, BLACK, (x - 25, y + cart_height//2), 8)
            pygame.draw.circle(screen, BLACK, (x + 25, y + cart_height//2), 8)
            
            # 乗車可能な場合は緑の枠と矢印
            if not cart['passenger']:
                pygame.draw.rect(screen, GREEN,
                               (x - cart_width//2 - 3, y - cart_height//2 - 3,
                                cart_width + 6, cart_height + 6), 3)
                # 下向き矢印
                pygame.draw.polygon(screen, GREEN,
                                  [(x, y - cart_height//2 - 20),
                                   (x - 10, y - cart_height//2 - 30),
                                   (x + 10, y - cart_height//2 - 30)])
                
    def try_board(self, player):
        # プレイヤーが乗車を試みる
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        for cart in self.carts:
            if not cart['passenger']:  # 空いているトロッコ
                cart_rect = pygame.Rect(cart['x'] - cart['width']//2,
                                       cart['y'] - cart['height']//2,
                                       cart['width'], cart['height'])
                
                # 近くにいて、上から降りてきた場合
                if player_rect.colliderect(cart_rect) and player.vel_y >= 0:
                    cart['passenger'] = player
                    return True
        return False
        
    def try_disembark(self, player):
        # プレイヤーが降車を試みる
        for cart in self.carts:
            if cart['passenger'] == player:
                cart['passenger'] = None
                player.vel_y = -15  # ジャンプして降りる
                return True
        return False

class Game:
    def __init__(self):
        self.player = Player(100, 300)
        self.camera_x = 0
        self.camera_y = 0
        self.platforms = []
        self.attractions = []
        self.particles = []
        self.roller_coasters = []
        self.coins = []
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.create_level()
        self.player_on_coaster = False
        
    def create_level(self):
        # 超ロングフィールド（隙間なし）
        for i in range(-1000, 50000, 100):
            self.platforms.append(Platform(i, 600, 100, 100))
            
        # 空中プラットフォーム
        self.platforms.extend([
            Platform(300, 500, 150, 20),
            Platform(600, 450, 200, 20),
            Platform(900, 400, 150, 20),
            Platform(1200, 350, 180, 20),
            Platform(1500, 450, 200, 20),
            Platform(1900, 300, 150, 20),
            Platform(2200, 400, 200, 20),
            Platform(2600, 250, 180, 20),
            Platform(3000, 350, 200, 20),
            Platform(3400, 200, 150, 20),
            Platform(3700, 300, 200, 20),
        ])
        
        # ジェットコースターのレール配置（より大きく、高低差を強調）
        coaster_tracks = [
            # ジェットコースター1（大きな山型）
            [(800, 550), (900, 540), (1000, 520), (1100, 490), (1200, 450), 
             (1300, 400), (1400, 340), (1500, 280), (1600, 220), (1700, 180),
             (1800, 150), (1900, 140), (2000, 150), (2100, 180), (2200, 220),
             (2300, 280), (2400, 340), (2500, 400), (2600, 450), (2700, 490),
             (2800, 520), (2900, 540), (3000, 550), (2900, 560), (2800, 565),
             (2700, 568), (2600, 570), (2500, 570), (2400, 568), (2300, 565),
             (2200, 560), (2100, 555), (2000, 550), (1900, 545), (1800, 542),
             (1700, 540), (1600, 538), (1500, 537), (1400, 538), (1300, 540),
             (1200, 542), (1100, 545), (1000, 548), (900, 550), (800, 550)],
            
            # ジェットコースター2（ループ型）
            [(5000, 500), (5100, 480), (5200, 450), (5300, 400), (5400, 340),
             (5500, 270), (5600, 200), (5700, 130), (5800, 80), (5900, 50),
             (6000, 40), (6100, 50), (6200, 80), (6300, 130), (6400, 200),
             (6500, 270), (6600, 340), (6700, 400), (6800, 450), (6900, 480),
             (7000, 500), (7100, 510), (7200, 515), (7100, 520), (7000, 525),
             (6900, 530), (6800, 532), (6700, 534), (6600, 535), (6500, 534),
             (6400, 532), (6300, 530), (6200, 525), (6100, 520), (6000, 515),
             (5900, 510), (5800, 505), (5700, 502), (5600, 500), (5500, 498),
             (5400, 497), (5300, 498), (5200, 499), (5100, 500), (5000, 500)],
             
            # ジェットコースター3（波型）
            [(10000, 450), (10200, 400), (10400, 350), (10600, 320), (10800, 350),
             (11000, 400), (11200, 450), (11400, 400), (11600, 350), (11800, 320),
             (12000, 350), (12200, 400), (12400, 450), (12600, 400), (12800, 350),
             (13000, 320), (13200, 350), (13400, 400), (13600, 450), (13400, 480),
             (13200, 490), (13000, 495), (12800, 498), (12600, 500), (12400, 500),
             (12200, 498), (12000, 495), (11800, 490), (11600, 485), (11400, 480),
             (11200, 475), (11000, 472), (10800, 470), (10600, 468), (10400, 465),
             (10200, 460), (10000, 450)],
        ]
        
        # ジェットコースターを作成
        for i, track in enumerate(coaster_tracks):
            self.roller_coasters.append(RollerCoaster(track[0][0], track[0][1], track))
        attractions_data = [
            (400, 300, 300, 200, RED, "ジェットコースター"),
            (1000, 200, 200, 200, PURPLE, "観覧車"),
            (1600, 420, 150, 100, ORANGE, "メリーゴーランド"),
            (2300, 150, 250, 250, DARK_BLUE, "観覧車"),
            (2800, 300, 300, 150, RED, "ジェットコースター"),
            (3500, 400, 180, 120, PINK, "ティーカップ"),
            (4000, 200, 200, 200, PURPLE, "観覧車"),
            (4600, 350, 250, 150, ORANGE, "メリーゴーランド"),
            (5200, 250, 300, 200, RED, "ジェットコースター"),
            (5900, 180, 220, 220, PURPLE, "観覧車"),
        ]
        
        # 基本パターンを繰り返して配置
        for base_x in range(0, 45000, 6000):
            for x, y, w, h, color, name in attractions_data:
                self.attractions.append(Attraction(base_x + x, y, w, h, color, name))
        
    def handle_coin_collection(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, 
                                 self.player.width, self.player.height)
        
        for coin in self.coins:
            if not coin.collected:
                coin_rect = pygame.Rect(coin.x - coin.radius, coin.y - coin.radius,
                                      coin.radius * 2, coin.radius * 2)
                if player_rect.colliderect(coin_rect):
                    coin.collect()
                    self.score += 10
                    # コイン取得エフェクト
                    for i in range(10):
                        self.particles.append({
                            'x': coin.x,
                            'y': coin.y,
                            'vel_x': random.uniform(-5, 5),
                            'vel_y': random.uniform(-8, -2),
                            'lifetime': 30,
                            'color': YELLOW
                        })
    
    def handle_collisions(self):
        self.player.on_ground = False
        player_rect = pygame.Rect(self.player.x, self.player.y, 
                                 self.player.width, self.player.height)
        
        # プラットフォームとの衝突判定
        for platform in self.platforms:
            plat_rect = platform.get_rect()
            if player_rect.colliderect(plat_rect):
                # 上から落下
                if self.player.vel_y > 0 and player_rect.bottom > plat_rect.top:
                    if player_rect.bottom - plat_rect.top < 20:
                        self.player.y = plat_rect.top - self.player.height
                        self.player.vel_y = 0
                        self.player.on_ground = True
                        # 着地パーティクル
                        self.create_landing_particles()
                        
        # アトラクションとの衝突判定（バネのように跳ね返る）
        for attraction in self.attractions:
            attr_rect = attraction.get_rect()
            if player_rect.colliderect(attr_rect):
                # 衝突の方向を判定
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                attr_center_x = attr_rect.centerx
                attr_center_y = attr_rect.centery
                
                # 相対位置を計算
                dx = player_center_x - attr_center_x
                dy = player_center_y - attr_center_y
                
                # 横方向の衝突
                if abs(dx) > abs(dy):
                    if dx > 0:  # プレイヤーが右側
                        self.player.x = attr_rect.right + 5
                        self.player.vel_x = abs(self.player.vel_x) * 1.5  # 右に跳ね返る
                    else:  # プレイヤーが左側
                        self.player.x = attr_rect.left - self.player.width - 5
                        self.player.vel_x = -abs(self.player.vel_x) * 1.5  # 左に跳ね返る
                    # 跳ね返りエフェクト
                    self.create_bounce_particles(attraction)
                    
                # 縦方向の衝突
                else:
                    if dy > 0:  # プレイヤーが下側
                        self.player.y = attr_rect.bottom + 5
                        self.player.vel_y = abs(self.player.vel_y) * 0.8
                    else:  # プレイヤーが上側
                        self.player.y = attr_rect.top - self.player.height - 5
                        self.player.vel_y = -20  # 上に大きく跳ね返る
                        self.player.on_ground = True
                    # 跳ね返りエフェクト
                    self.create_bounce_particles(attraction)
                    
    def get_time_of_day(self):
        # 5分(300秒)で1日
        elapsed_ms = pygame.time.get_ticks() - self.start_time
        elapsed_seconds = elapsed_ms / 1000
        day_progress = (elapsed_seconds % 300) / 300  # 0.0～1.0
        
        # 時間帯を返す（0-1の値と時間帯名）
        if day_progress < 0.25:  # 朝（0:00-6:00）
            return day_progress * 4, "朝"
        elif day_progress < 0.5:  # 昼（6:00-12:00）
            return (day_progress - 0.25) * 4, "昼"
        elif day_progress < 0.75:  # 夕方（12:00-18:00）
            return (day_progress - 0.5) * 4, "夕方"
        else:  # 夜（18:00-24:00）
            return (day_progress - 0.75) * 4, "夜"
            
    def get_sky_color(self):
        progress, time_name = self.get_time_of_day()
        
        if time_name == "朝":
            # 朝焼け（紫→オレンジ→水色）
            if progress < 0.5:
                r = int(100 + progress * 300)
                g = int(50 + progress * 150)
                b = int(139 + progress * 50)
            else:
                r = int(250 - (progress - 0.5) * 230)
                g = int(125 + (progress - 0.5) * 162)
                b = int(189 + (progress - 0.5) * 92)
        elif time_name == "昼":
            # 青空
            r, g, b = 135, 206, 235
        elif time_name == "夕方":
            # 夕焼け（水色→オレンジ→紫）
            if progress < 0.5:
                r = int(135 + progress * 240)
                g = int(206 - progress * 140)
                b = int(235 - progress * 200)
            else:
                r = int(255 - (progress - 0.5) * 200)
                g = int(136 - (progress - 0.5) * 100)
                b = int(35 + (progress - 0.5) * 180)
        else:  # 夜
            # 夜空（紫→暗い青）
            r = int(55 - progress * 30)
            g = int(36 - progress * 20)
            b = int(115 - progress * 40)
            
        return (r, g, b)
    
    def create_landing_particles(self):
        for i in range(5):
            self.particles.append({
                'x': self.player.x + self.player.width // 2,
                'y': self.player.y + self.player.height,
                'vel_x': random.uniform(-3, 3),
                'vel_y': random.uniform(-5, -2),
                'lifetime': 20,
                'color': YELLOW
            })
            
    def create_bounce_particles(self, attraction):
        # 跳ね返りエフェクト
        for i in range(8):
            self.particles.append({
                'x': self.player.x + self.player.width // 2,
                'y': self.player.y + self.player.height // 2,
                'vel_x': random.uniform(-8, 8),
                'vel_y': random.uniform(-8, 8),
                'lifetime': 30,
                'color': attraction.color
            })
            
    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['vel_y'] += 0.5
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                
    def update_camera(self):
        # カメラの滑らかな追従
        target_x = self.player.x - WIDTH // 2
        target_y = self.player.y - HEIGHT // 2
        
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # カメラの制限（横方向のみ、縦は自由に）
        self.camera_x = max(0, self.camera_x)
        
    def draw(self, screen):
        # 時間に応じた背景色
        sky_color = self.get_sky_color()
        screen.fill(sky_color)
        
        # 時間帯の取得
        progress, time_name = self.get_time_of_day()
        
        # 太陽/月の描画
        if time_name in ["朝", "昼", "夕方"]:
            # 太陽
            sun_x = int(WIDTH * (0.1 + progress * 0.8))
            if time_name == "朝":
                sun_y = int(HEIGHT * 0.3 - progress * HEIGHT * 0.2)
            elif time_name == "昼":
                sun_y = int(HEIGHT * 0.1)
            else:  # 夕方
                sun_y = int(HEIGHT * 0.1 + progress * HEIGHT * 0.2)
            pygame.draw.circle(screen, YELLOW if time_name == "昼" else ORANGE, 
                             (sun_x, sun_y), 40)
        else:
            # 月
            moon_x = int(WIDTH * (0.1 + progress * 0.8))
            moon_y = int(HEIGHT * 0.2)
            pygame.draw.circle(screen, WHITE, (moon_x, moon_y), 30)
            # 星
            for i in range(50):
                star_x = (i * 73 + int(self.camera_x * 0.1)) % WIDTH
                star_y = (i * 37) % (HEIGHT // 2)
                pygame.draw.circle(screen, WHITE, (star_x, star_y), 1)
        
        # 雲の描画（時間帯に応じた色）
        cloud_color = WHITE if time_name == "昼" else (200, 200, 200) if time_name in ["朝", "夕方"] else (100, 100, 100)
        for i in range(5):
            cloud_x = (i * 400 - self.camera_x * 0.3) % (WIDTH + 200) - 100
            cloud_y = 50 + i * 30
            pygame.draw.ellipse(screen, cloud_color, (cloud_x, cloud_y, 120, 60))
            pygame.draw.ellipse(screen, cloud_color, (cloud_x + 30, cloud_y - 20, 100, 70))
            pygame.draw.ellipse(screen, cloud_color, (cloud_x + 60, cloud_y, 80, 50))
        
        # プラットフォームの描画
        for platform in self.platforms:
            platform.draw(screen, self.camera_x, self.camera_y)
            
        # ジェットコースターの描画
        for coaster in self.roller_coasters:
            coaster.draw(screen, self.camera_x, self.camera_y)
            
        # アトラクションの描画
        for attraction in self.attractions:
            attraction.draw(screen, self.camera_x, self.camera_y)
            
        # コインの描画
        for coin in self.coins:
            coin.draw(screen, self.camera_x, self.camera_y)
            
        # パーティクルの描画
        for particle in self.particles:
            color = particle.get('color', YELLOW)
            size = max(2, particle['lifetime'] // 5)
            pygame.draw.circle(screen, color, 
                             (int(particle['x'] - self.camera_x), 
                              int(particle['y'] - self.camera_y)), size)
            
        # プレイヤーの描画
        self.player.draw(screen, self.camera_x, self.camera_y)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        # スコア表示
        score_text = f"スコア: {self.score}"
        text = font.render(score_text, True, BLACK if time_name in ["昼", "朝"] else WHITE)
        screen.blit(text, (WIDTH - 200, 10))
        
        # スピード表示
        speed_text = f"スピード: {abs(int(self.player.vel_x * 10))}"
        text = font.render(speed_text, True, BLACK if time_name in ["昼", "朝"] else WHITE)
        screen.blit(text, (10, 10))
        
        # 時間表示
        _, time_name = self.get_time_of_day()
        time_text = f"時間帯: {time_name}"
        text = font.render(time_text, True, BLACK if time_name in ["昼", "朝"] else WHITE)
        screen.blit(text, (10, 50))
        
        # 操作説明
        controls = [
            "操作方法:",
            "← → : 移動",
            "SPACE : ジャンプ / 降車",
            "↓ : ジェットコースターに乗る",
            "アトラクションを飛び越えて走り回ろう！"
        ]
        small_font = pygame.font.Font(None, 24)
        text_color = BLACK if time_name in ["昼", "朝"] else WHITE
        for i, control in enumerate(controls):
            text = small_font.render(control, True, text_color)
            screen.blit(text, (10, 90 + i * 25))
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            keys = pygame.key.get_pressed()
            
            # プレイヤーの操作
            if not self.player_on_coaster:
                if keys[pygame.K_LEFT]:
                    self.player.move_left()
                if keys[pygame.K_RIGHT]:
                    self.player.move_right()
                if keys[pygame.K_SPACE]:
                    self.player.jump()
                    
                # 摩擦の適用
                if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                    self.player.apply_friction()
            else:
                # ジェットコースターに乗っている時
                if keys[pygame.K_SPACE]:
                    # 降車
                    for coaster in self.roller_coasters:
                        if coaster.try_disembark(self.player):
                            self.player_on_coaster = False
                            break
                            
            # 乗車判定（下キーで乗車）
            if keys[pygame.K_DOWN] and not self.player_on_coaster:
                for coaster in self.roller_coasters:
                    if coaster.try_board(self.player):
                        self.player_on_coaster = True
                        break
                
            # 落下時のリスポーン（念のため）
            if self.player.y > 1000:
                self.player.x = 100
                self.player.y = 300
                self.player.vel_x = 0
                self.player.vel_y = 0
                
            # 摩擦の適用
            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                self.player.apply_friction()
                
            # 更新
            if not self.player_on_coaster:
                self.player.update()
                self.handle_collisions()
                self.handle_coin_collection()
                
            self.update_camera()
            self.update_particles()
            
            # アトラクションの更新
            for attraction in self.attractions:
                attraction.update()
                
            # ジェットコースターの更新
            for coaster in self.roller_coasters:
                coaster.update()
                
            # コインの更新
            for coin in self.coins:
                coin.update()
                
            # 描画
            self.draw(screen)
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()

# ゲームの実行
if __name__ == "__main__":
    game = Game()
    game.run()