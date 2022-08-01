from exodus.exodus import MetadataMapping
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--csv', help='Specify CSV Path', default='temp/mark.csv')
parser.add_argument('-m', '--mapping', help='Specify Mapping', default='configs/utk_dc.yml')
parser.add_argument('-p', '--path_to_files', help='Specify Path to Run Mapping Against', default='fixtures')
args = parser.parse_args()

mapping = MetadataMapping(args.mapping, args.path_to_files)
mapping.write_csv(args.csv)

