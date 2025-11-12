import argparse
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ods_input', type=str, help="ODS sheet of input data")
    parser.add_argument('export_dir', type=str, help="Directory to export json and images to")
    return parser.parse_args()


def main():
    args = get_args()

if __name__ == '__main__':
    main()
