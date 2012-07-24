import argparse
import itertools
import random
import sys

CARDS = '2 3 4 5 6 7 8 9 10 JACK QUEEN KING ACE'.split()
VALUES = {card: value for value, card in enumerate(CARDS)}
VALUES[None] = -1 # None will always lose battles

def new_deck():
    """Get a new shuffled deck of cards"""
    deck = CARDS * 4
    random.shuffle(deck)
    return deck

def value(card):
    """Get the numeric value of a card"""
    return VALUES[card]

def draw_cards(decks, n=1):
    """Draw n sets of 1 card from each deck"""
    if n == 1:
        return [deck.pop(0) if len(deck) > 0 else None for deck in decks]
    else:
        return [[deck.pop(0) if len(deck) > 0 else None for deck in decks]
                for i in range(n)]

def conflict(decks, pot=None):
    """Enact a conflict, transferring the cards to the winning deck

    This works recursively, so if the first battle is a tie, it adds
    those cards and three more from each player to the pot and then
    calls itself. Once someone wins, all the cards from that battle
    and the pot are transferred to the winnig deck.

    """
    if pot is None:
        pot = []
    battle = draw_cards(decks)
    high_card = max(battle, key=value)
    if battle.count(high_card) > 1:
        #print("{}: This means war!".format(battle))
        face_down_cards = draw_cards(decks, 3)
        conflict(decks, pot+[battle]+face_down_cards)
    else:
        winner = battle.index(high_card)
        #print("{}: Player {} wins!".format(battle, winner + 1))
        # Give the winning player all the cards in the battle and the pot
        for card in itertools.chain(itertools.chain(*pot), battle):
            if card is not None:
                #print("Giving player {} card {}".format(winner + 1, repr(card)))
                decks[winner].append(card)

def graph(decks):
    output_width = 80
    max_deck_width = output_width // len(decks) - 3
    total_cards = len(decks) * len(new_deck())
    percentages = [len(deck) / total_cards for deck in decks]
    deck_widths = [round(p * max_deck_width) for p in percentages]
    return " ".join("[" + "#" * w + " " * (max_deck_width - w) + "]" for w in deck_widths)

def game(players):
    decks = [new_deck() for n in range(players)]
    rounds = 0
    while True:
        rounds += 1
        conflict(decks)
        if args.graph:
            print(graph(decks))
        cards_remaining = [len(deck) > 0 for deck in decks]
        if not cards_remaining.count(True) > 1:
            break
    return rounds, cards_remaining.index(True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', type=int, dest='games', default=1,
                        help="play GAMES games")
    parser.add_argument('-p', type=int, dest='players', default=2,
                        help="play games with PLAYERS players")
    parser.add_argument('--graph', action='store_true',
                        help="print graphs of the card distribution")
    args = parser.parse_args()

    rounds = [0 for g in range(args.games)]
    wins = [0 for p in range(args.players)]
    for i in range(args.games):
        print("> Starting game {} with {} players".format(i + 1, args.players))
        rounds[i], winner = game(args.players)
        wins[winner] += 1
        print("> Ending game {}. Took {} rounds. "
              "Player {} won!".format(i + 1, rounds[i], winner + 1))
    print("> Average rounds per game: {}".format(sum(rounds) / len(rounds)))
    print("> Total wins: " +
          ", ".join("Player {}: {}".format(p + 1, wins[p])
                    for p in range(args.players)))
