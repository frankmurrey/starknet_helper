import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-ncr", "--no-check-req", help="Skip checking requirements", action="store_true"
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    print(get_args())