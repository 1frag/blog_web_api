"""Run to generate secure information about enviroment variables"""
import pathlib


def bold(word):
    return word.join(("__", "__"))


def main():
    result = dict()
    for file in pathlib.Path(__file__).cwd().iterdir():
        if not str(file).endswith(".env"):
            continue

        result[file.name] = list(map(
            lambda x: x.split("=", 1)[0],
            file.read_text().split(),
        ))

    with open("README.md", "w") as fp:
        fp.write("## Для работы сервиса необходимо установить следующие переменные:\n\n")
        for key, names in result.items():
            fp.write(bold(key) + "\n")
            for name in names:
                fp.write("* " + name + "\n")
            fp.write("\n")


if __name__ == '__main__':
    main()
