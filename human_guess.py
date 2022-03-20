"""Find best first guess as a human.

While computer strategies can use minmax, as a human green has much greater
utility than yellow, which has much greater utility than black.

Search for a word that optimizes green, then yellow information.
"""

import valid_words

def compare(truth: str, attempt: str):
    """Score a single word."""
    remaining_truth = [t for t, a in zip(truth, attempt) if t != a]
    green = 5 - len(remaining_truth)

    # Yellow handling.
    remaining_attempt = [a for t, a in zip(truth, attempt) if t != a]
    yellow = 0
    for a in remaining_attempt:
        if a in remaining_truth:
            remaining_truth.remove(a)
            yellow += 1

    return green, yellow


def main():
    best_total_gy = (0, 0)
    words = []
    for v in valid_words.POSSIBLE_KEYS:
        if len(set([c for c in v])) < 5:
            # Don't allow words with repeat letters.
            continue

        total_g = 0
        total_y = 0
        for k in valid_words.POSSIBLE_KEYS:
            g, y = compare(k, v)
            total_g += g
            total_y += y

        total_gy = (total_g, total_y)
        if total_gy > best_total_gy:
            best_total_gy = total_gy
            words = [v]
        elif total_gy == best_total_gy:
            words.append(v)

    print(words)


if __name__ == "__main__":
    main()
