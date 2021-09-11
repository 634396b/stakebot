import stake_http
from main import Bot
import util
import time
import re
providers = {
    'playngo': 'e10817ab-b047-4506-a033-935706baf568',
    'pragmatic': '64520ffb-021a-44a8-9e01-cbbd17b4eecf'
}
if __name__ == '__main__':
    number_map = {0: 'Zero', 1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
                  6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine'}
    bot = Bot()
    user = bot.users[0]
    offset = 0
    limit = 21
    total_game_count = 100000
    all_games = []
    while offset < total_game_count:
        time.sleep(1)
        # Pragmatic
        r = stake_http.slug_kurator_group(key=user.key, limit=limit, offset=offset, filter_ids=[
                                          providers['playngo']])
        util.check_response(r)
        r = r.json()
        slug_kurator_group = r['data']['slugKuratorGroup']
        total_game_count = slug_kurator_group['gameCount']
        games_list = slug_kurator_group['groupGamesList']
        for game in games_list:
            all_games.append(game['game'])
        offset += limit
        print(len(games_list), offset)
    f_gen = 'from providers.PlayNGo import PlayNGo\n\n'
    for i, game in enumerate(all_games):
        active = game['active'] if 'active' in game else ''
        edge = game['edge']
        name = re.sub("[^0-9a-zA-Z]+", "", game['name'])
        for i in range(10):
            name = name.replace(str(i), number_map[i])
        slug = game['slug']
        game_type = game['type'] if 'type' in game else ''
        game_categories = []
        if 'groupGames' in game:
            for group in game['groupGames']:
                group_slug = group['group']['slug']
                group_id = group['group']['id']
                group_type = group['group']['type']
                group_text = group['group']['translation']
                game_categories.append(
                    {'slug': group_slug, 'text': group_text, 'type': group_type})
        all_games[i] = {'slug': slug, 'name': name, 'game_type': game_type,
                        'edge': edge, 'game_categories': game_categories}
        class_str = f"""
        class {name}(PlayNGo):\n    slug= \"{slug}\"\n    categories=[{','.join([f'"{gc["slug"]}"' for gc in game_categories])}]\n    edge={edge * 100:.2f}
        """.strip() + '\n'*3
        f_gen += class_str
    with open('providers/PlayNGoSlots.py', 'w') as f:
        f.write(f_gen)
