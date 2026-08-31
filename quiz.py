#!/usr/bin/env python3
"""
Simple CLI quiz app for exam preparation.

Usage:
  python3 quiz.py questions.json

Features:
 - Loads multiple-choice questions from a JSON file.
 - Shuffles questions and choices.
 - Optional per-question timer (set QUESTION_TIME_SECONDS).
 - Shows score and which questions were wrong.
"""

import json
import random
import sys
import time

# Number of seconds allowed per question (set to None to disable timing)
QUESTION_TIME_SECONDS = None  # e.g., 20 for 20 seconds per question

def load_questions(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Validate basic shape
    questions = []
    for i, item in enumerate(data):
        q = {
            'question': item.get('question', f'Question {i+1}'),
            'choices': item.get('choices', []),
            'answer': item.get('answer')  # should be index (0-based) or the exact string
        }
        if not q['choices'] or q['answer'] is None:
            raise ValueError(f'Invalid question format at index {i}: {item}')
        questions.append(q)
    return questions

def ask_question(qobj, qnum, total):
    q_text = qobj['question']
    choices = qobj['choices'][:]
    correct = qobj['answer']

    # If answer was given as index, translate to value for comparison later
    if isinstance(correct, int):
        correct_value = choices[correct]
    else:
        correct_value = correct

    # Shuffle choices but keep track of correct index
    indexed = list(enumerate(choices))
    random.shuffle(indexed)
    shuffled_choices = [c for _, c in indexed]
    # find new index of correct_value
    try:
        new_index = shuffled_choices.index(correct_value)
    except ValueError:
        # fall back: if correct value not in choices, assume given as index before shuffle
        new_index = 0

    print(f'\nQuestion {qnum}/{total}:')
    print(q_text)
    for i, choice in enumerate(shuffled_choices):
        print(f'  {i+1}. {choice}')

    start = time.time()
    answer = None
    try:
        if QUESTION_TIME_SECONDS:
            print(f'You have {QUESTION_TIME_SECONDS} seconds to answer.')
        raw = input('Your answer (enter choice number): ').strip()
        if QUESTION_TIME_SECONDS and (time.time() - start) > QUESTION_TIME_SECONDS:
            print('Time is up!')
            return False, correct_value
        if not raw:
            return False, correct_value
        idx = int(raw) - 1
        answer = shuffled_choices[idx] if 0 <= idx < len(shuffled_choices) else None
    except (ValueError, IndexError):
        answer = None

    is_correct = (answer == correct_value)
    return is_correct, correct_value

def run_quiz(questions):
    random.shuffle(questions)
    total = len(questions)
    score = 0
    wrong = []

    for i, q in enumerate(questions, start=1):
        is_correct, correct_value = ask_question(q, i, total)
        if is_correct:
            print('Correct!')
            score += 1
        else:
            print(f'Wrong — correct answer: {correct_value}')
            wrong.append({'question': q['question'], 'correct': correct_value})

    print('\n--- Results ---')
    print(f'Score: {score}/{total} ({score/total*100:.1f}%)')
    if wrong:
        print('\nQuestions to review:')
        for w in wrong:
            print(f' - {w["question"]} -> {w["correct"]}')

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 quiz.py questions.json')
        sys.exit(1)
    path = sys.argv[1]
    questions = load_questions(path)
    run_quiz(questions)

if __name__ == '__main__':
    main()