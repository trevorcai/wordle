"""1-step wordle.

Call as:
    python wordle.py <truth> [<first guess>]
"""

import copy
import dataclasses
import sys
from typing import Dict, Optional, Sequence, Set

import valid_words

@dataclasses.dataclass(frozen=True)
class Hint:
    """State of received information."""
    # Sequence of length 5, Optional if not confirmed.
    green: Sequence[Optional[str]]
    # Characters present but not at the specified index.
    yellow: Dict[str, Set[int]]
    # Characters not present.
    black: Set[str]

EMPTY_HINT = Hint([None] * 5, dict(), set())


def score_word(truth: str, attempt: str, hint: Hint):
    """For a given attempt at guessing truth, generate the next hint."""
    # Mutable copies of previous hint.
    green = list(hint.green)
    yellow = copy.deepcopy(hint.yellow)
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

    # In case of ties, prefer words that could be correct
    best_in_possible = best_guess in possible_keys

    for v in vocab:
        # Partition possible answers by resulting hint pattern
        partitions = {}
        for k in possible_keys:
            is_correct, next_hint = score_word(k, v, curr_hint)

            # Convert hint to hashable representation
            hint_key = (
                tuple(next_hint.green),
                frozenset((c, frozenset(idx)) for c, idx in next_hint.yellow.items()),
                frozenset(next_hint.black)
            )

            if hint_key not in partitions:
                partitions[hint_key] = []
            partitions[hint_key].append(k)

        # Find worst case (largest remaining group)
        worst_case_remaining = max(len(group) for group in partitions.values()) if partitions else len(possible_keys)
        min_eliminated = len(possible_keys) - worst_case_remaining

        # Current word is in possible answers
        v_in_possible = v in possible_keys

        # Update best if:
        # 1. This word eliminates more words than previous best, OR
        # 2. It eliminates the same number but this word is a possible answer and previous best is not
        if (min_eliminated > best_min_eliminated) or \
           (min_eliminated == best_min_eliminated and v_in_possible and not best_in_possible):
            best_guess = v
            best_min_eliminated = min_eliminated
            best_in_possible = v_in_possible

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
        first_guess = 'aesir'  # precomputed

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
