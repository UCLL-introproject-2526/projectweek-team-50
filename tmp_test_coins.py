from coins import CoinManager, handle_death
from world.tilemap import TileMap
from entities.enemy import Enemy
from settings import TILE_SIZE

# setup
tilemap = TileMap()
cm = CoinManager()
# enemy at tile (5,5)
path = [(5*TILE_SIZE,5*TILE_SIZE),(6*TILE_SIZE,5*TILE_SIZE)]
en = Enemy(path_points=path, health=0, speed=1.0, reward=30)
# simulate death
handle_death(en, cm, tilemap)
print('coins:', cm.coins)
