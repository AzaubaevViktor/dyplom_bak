from typing import List, Iterator, Iterable, Tuple, Dict

import pymystem3

from lemmatize.models import Lemma
from vkontakte.models import VkPost

print("Init MyStem...", end='')
_mystem = pymystem3.Mystem()
print("OK")


def _to_alnum(s: str) -> List[str]:
    res = ""
    for ch in s:
        if ch.isalnum():
            res += ch
        else:
            if res:
                yield res
            res = ""

    if res:
        yield res


def _filter_text(text: str) -> Iterator[str]:
    for line in text.split("\n"):
        if not line:
            continue
        for word in _to_alnum(line):
            if word:
                yield word.lower()


_white_list = (
    'нгу',
    'фит',
    'фен',
    'ггф',
    'фия',
    'егэ'
)


def _divide(posts: List[VkPost], max_length: int = 5000, divider_char='\1') \
        -> Iterable[Tuple[List[str], List[VkPost], Dict[VkPost, List[str]]]]:
    text_to_send = []
    post_list = []
    white_list_tokens = {}

    for post in posts:
        post_list.append(post)

        for token in _filter_text(post.text):
            if token in _white_list:
                white_list_tokens.setdefault(post, [])
                white_list_tokens[post].append(token)
            else:
                text_to_send.append(token)
        # Какая-то хуйня, плохо работает
        text_to_send.append("\1")

        if len(text_to_send) >= max_length:
            yield text_to_send, post_list, white_list_tokens
            text_to_send = []
            post_list = []
            white_list_tokens = {}

    yield text_to_send, post_list, white_list_tokens


def _get_lemmas(text: str):
    for lemma in _mystem.lemmatize(text):
        lemma = lemma.strip()
        yield from [x.strip() for x in lemma.split(" ") if x.strip()]


def _lemmatize(word_list: List[str]) -> Iterable[Tuple[str, str]]:
    for initial, source in zip(_get_lemmas(" ".join(word_list)),
                               word_list):
        yield initial, source


def handle_posts(posts: List[VkPost], max_length: int = 100) \
        -> Iterable[Tuple[Lemma, VkPost, str]]:
    posts_list = []  # type: List[VkPost]
    text_to_send = []  # type: List[str]
    divider_char = '\1'

    def gen_answer(post: VkPost, token: str) -> Tuple[Lemma, VkPost, str] or None:
        if len(token) < 100:
            lemma, created = Lemma.objects.get_or_create(
                name=token)
            return lemma, post
        return None

    for text_to_send, posts_list, white_list_tokens in _divide(posts,
                                                               max_length,
                                                               divider_char):
        posts_iter = iter(posts_list)
        post = next(posts_iter)
        for initial, source in _lemmatize(text_to_send):
            if '\1' == initial:
                try:
                    post = next(posts_iter)
                    yield "new_post", post, None
                except StopIteration:
                    break
                # first send lemmas from from whitespaced
                for white_token in white_list_tokens.get(post, []):
                    ans = gen_answer(post, white_token)
                    yield ans

            else:
                ans = gen_answer(post, initial)
                yield ans
