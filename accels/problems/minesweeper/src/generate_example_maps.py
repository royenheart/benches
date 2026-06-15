#encoding: utf-8
import argparse
import os
import shutil
import subprocess


def parse_args():
	parser = argparse.ArgumentParser(description="Generate reproducible minesweeper maps.")
	parser.add_argument("--min-log-n", type=int, default=4, help="smallest N as log2(N)")
	parser.add_argument("--max-log-n", type=int, default=12, help="largest N as log2(N); use 16 for full-size handout maps")
	parser.add_argument("--seed", type=int, default=0)
	parser.add_argument("--output-dir", default="map")
	return parser.parse_args()


args = parse_args()

if args.min_log_n < 4 or args.max_log_n < args.min_log_n or args.max_log_n > 16:
	raise SystemExit("--min-log-n/--max-log-n must select a range within [4, 16]")

# Check whether "map_generator" is present
if not os.path.exists('map_generator'):
	raise SystemExit('Error: `map_generator` does not exists. Maybe you should run `make` first?')

# Create the directory
if os.path.exists(args.output_dir):
	shutil.rmtree(args.output_dir, ignore_errors=True)
os.mkdir(args.output_dir)

sizes = [2**N for N in range(args.min_log_n, args.max_log_n + 1)]

for N in sizes:
	K = N*N//8
	print(f"Generating map with N={N}, K={K}, seed={args.seed}")
	filename = "%d_%d_%d.map" % (N, K, args.seed)
	path = os.path.join(args.output_dir, filename)
	with open(path, "wb") as output:
		subprocess.run(["./map_generator", str(N), str(K), str(args.seed)], stdout=output, check=True)
