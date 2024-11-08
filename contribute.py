#!/usr/bin/env python
import argparse
import os
from datetime import datetime, timedelta
from random import randint, normalvariate
from subprocess import Popen
import sys


def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime(2024, 11, 8)  # Zaktualizowana data końcowa
    start_date = datetime(2018, 1, 1)  # Początek aktywności w 2018 roku
    days_range = (curr_date - start_date).days  # Liczba dni od 2018 do 2024

    # Tworzenie katalogu repozytorium
    if args.repository:
        start = args.repository.rfind('/') + 1
        end = args.repository.rfind('.')
        base_directory = args.repository[start:end] if start < end else f'repository-{curr_date.strftime("%Y-%m-%d-%H-%M-%S")}'
    else:
        base_directory = f'repository-{curr_date.strftime("%Y-%m-%d-%H-%M-%S")}'

    # Upewnij się, że katalog ma unikalną nazwę
    directory = base_directory
    counter = 1

    while os.path.exists(directory):
        directory = f"{base_directory}_{counter}"
        counter += 1

    os.mkdir(directory)
    os.chdir(directory)
    run(['git', 'init', '-b', 'main'])

    # Konfiguracja użytkownika (nazwa i email) dla commitów
    if args.user_name:
        run(['git', 'config', 'user.name', args.user_name])

    if args.user_email:
        run(['git', 'config', 'user.email', args.user_email])

    # Generowanie narastającej aktywności
    for day_offset in range(days_range):
        day = start_date + timedelta(days=day_offset)

        # Prawdopodobieństwo commitu w dni robocze vs weekend
        if day.weekday() < 5:  # Poniedziałek do piątku
            probability = normalvariate(10, 5)  # Normalna dystrybucja dla dni roboczych
        else:  # Weekend
            probability = normalvariate(3, 2)  # Mniejsza aktywność w weekend

        probability = max(0, min(probability, 100))  # Ograniczenie do przedziału [0, 100]

        if randint(1, 100) <= probability:
            # Losowa liczba commitów dziennie
            commits_today = randint(1, 3)  # Można zwiększyć lub dostosować
            for _ in range(commits_today):
                commit_time = day + timedelta(minutes=randint(0, 1440))
                contribute(commit_time)

    # Wypychanie do zdalnego repozytorium
    if args.repository:
        run(['git', 'remote', 'add', 'origin', args.repository])
        run(['git', 'branch', '-M', 'main'])
        run(['git', 'push', '-u', 'origin', 'main'])

    print('\nGenerowanie narastającej aktywności zakończone sukcesem!')


def contribute(date):
    # Tworzenie pliku README i commitowanie
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-m', '"%s"' % message(date), '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])


def run(commands):
    Popen(commands).wait()


def message(date):
    return f"Contribution on {date.strftime('%Y-%m-%d')} at {date.strftime('%H:%M:%S')}"


def arguments(argsval):
    # Parser argumentów do konfiguracji skryptu
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repository', type=str, help="Adres repozytorium zdalnego (HTTPS lub SSH)")
    parser.add_argument('-un', '--user_name', type=str, help="Nazwa użytkownika dla commitów")
    parser.add_argument('-ue', '--user_email', type=str, help="Email użytkownika dla commitów")
    parser.add_argument('-mc', '--max_commits', type=int, default=5, help="Maksymalna liczba commitów dziennie")
    return parser.parse_args(argsval)


if __name__ == "__main__":
    main()
