from hackthetrack.timetablenetwork import TimeTableNetwork


def main() -> None:
    network = TimeTableNetwork.create_empty()
    print(network)


if __name__ == '__main__':
    main()
