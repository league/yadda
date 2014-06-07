
def args(cmd):
    p = cmd(help='envhelp', description='envdesc')
    return p

def run(opts):
    print("ENV")
    print(opts)
