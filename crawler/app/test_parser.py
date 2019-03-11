import logging
from pathlib import Path

from pyquery import PyQuery as pq

from config import config
from lian_jia import Community
from util.orm import Session

DATA_DIR = Path(__file__).parent.joinpath('../data/').resolve()


def parse_all(community_id):
    save_file = DATA_DIR.joinpath(f'{community_id}.html')

    if save_file.exists():
        d = pq(save_file.read_text(encoding='utf-8'))

        keys = [e.text.rstrip('：') for e in d('span.hdic_key')]
        # values = [type(e.text) for e in d('span.hdic_value')]
        # print(values)
        # values = []
        # for e in d('span.hdic_value'):
        #     if e 
        values = [e.text for e in d('span.hdic_value') if e.text is not None]
        detail = dict(zip(keys, values))

        # print(keys)
        # print(values)
        print(detail)

    else:
        logging.error(f'# 详情页面不存在, community_id={community_id}')


def main():
    id = '5011000000245'
    parse_all(id)


if __name__ == '__main__':
    main()
