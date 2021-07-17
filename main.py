from miner import Miner
import sys

if __name__ == '__main__':
	if len(sys.argv) != 2:
		raise Exception('Please inform if you want to mine "all" or "one" in the parameters')

	miner = Miner()
	if sys.argv[1] == 'all':
		miner.mine_all()
	elif sys.argv[1] == 'one':
		miner.mine_selected()
	else:
		raise Exception('Invalid argument:', sys.argv[1])
