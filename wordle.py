"""1-step wordle."""

import copy
import dataclasses
import sys
from typing import Mapping, Optional, Sequence, Set

import valid_words

@dataclasses.dataclass(frozen=True)
class Hint:
    """State of received information."""
    # Sequence of length 5, Optional if not confirmed.
    green: Sequence[Optional[str]]
    # Characters present but not at the specified index.
    yellow: Mapping[str, Set[int]]
    # Characters not present.
    black: Set[str]

EMPTY_HINT = Hint([None] * 5, dict(), set())


def score_word(truth: str, attempt: str, hint: Hint):
    """For a given attempt at guessing truth, generate the next hint."""
    # Mutable copies of previous hint.
    green = list(hint.green)
    yellow = dict(**copy.deepcopy(hint.yellow))
    black = set(hint.black)

    # Update hint with new information.
    for i, c, t in zip(range(5), attempt, truth):
        if c == t:
            green[i] = c
        elif c in truth:
            # Not clear if these yellow semantics match wordle source.
            # However, they are self-consistent.
            if c not in yellow:
                yellow[c] = set()
            yellow[c].add(i)
        else:
            black.add(c)

    is_correct = truth == attempt
    return is_correct, Hint(green, yellow, black)


def matches_hint(word: str, hint: Hint) -> bool:
    """Whether the given word is consistent with the hint."""
    for c, g in zip(word, hint.green):
        if g is not None and c != g:
            return False
    for b in hint.black:
        if b in word:
            return False
    for y, idxs in hint.yellow.items():
        if y not in word:
            return False
        for idx in idxs:
            if word[idx] == y:
                return False

    return True


def minmax_step(possible_keys, vocab, curr_hint):
    """Find the guess that has best 1-step worst-case information."""
    best_guess, best_min_eliminated = vocab[0], 0
    for v in vocab:
        min_eliminated = len(possible_keys)
        for k in possible_keys:
            is_correct, next_hint = score_word(k, v, curr_hint)
            if is_correct:
                # If correct, all eliminated.
                remaining = 0
            else:
                remaining = sum(1 for w in possible_keys if matches_hint(w, next_hint))
            min_eliminated = min(min_eliminated, len(possible_keys) - remaining)

        if min_eliminated > best_min_eliminated:
            best_guess, best_min_eliminated = v, min_eliminated

    return best_guess


def main():
    # Game settings.
    HARD_MODE = True
    TRUTH = sys.argv[1]
    if TRUTH not in valid_words.POSSIBLE_KEYS:
        raise ValueError(f"{TRUTH} not a valid possible key.")

    if len(sys.argv) > 2:
        first_guess = sys.argv[2]
    else:
        first_guess = 'slate'  # cached.

    possible_keys = valid_words.POSSIBLE_KEYS
    vocab = valid_words.VALID_GUESSES

    hint = EMPTY_HINT
    for attempt in range(6):
        if attempt:
            guess = minmax_step(possible_keys, vocab, hint)
        else:
            guess = first_guess

        print(f'Guessing', guess)
        is_correct, hint = score_word(TRUTH, guess, hint)
        if is_correct:
            print(f'Done in {attempt + 1} attempts.')
            return

        possible_keys = [w for w in possible_keys if matches_hint(w, hint)]
        if len(possible_keys) > 5:
            print('Remaining possible_keys:', len(possible_keys))
        else:
            print('Remaining possible_keys:', ', '.join(possible_keys))
        if HARD_MODE:
            vocab = [w for w in vocab if matches_hint(w, hint)]

    print('Could not guess the TRUTH within 6 attempts.')


if __name__ == "__main__":
    main()
