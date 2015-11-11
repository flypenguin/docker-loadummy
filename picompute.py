# from:
# http://en.literateprograms.org/Pi_with_Machin's_formula_%28Python%29

def arccot(x, unity):
    sum = xpower = unity // x
    n = 3
    sign = -1
    while 1:
        xpower = xpower // (x*x)
        term = xpower // n
        if not term:
            break
        sum += sign * term
        sign = -sign
        n += 2
    return sum

def pi(digits):
    unity = 10**(digits + 10)
    pi = 4 * (4*arccot(5, unity) - arccot(239, unity))
    return pi // 10**10


# for command line testing convenience.
# real load starts kicking in between 10.000 and 100.000 digits

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Compute pi to the nth digit')
    parser.add_argument('digits', metavar='N', type=int,
                       help='how many digits to compute')
    args = parser.parse_args()
    print(str(pi(args.digits))[-10:])
