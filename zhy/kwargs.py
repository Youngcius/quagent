def inner(**kwargs):
    print(kwargs)


def func(**kwargs):
    print(type(kwargs))
    # print(kwargs)
    inner(**kwargs)


class CCC:
    a = 10
    b = 100


if __name__ == '__main__':
    func(a=10, b=123, c=[1, 2, 3])
    print(CCC.a, CCC.b)
    print(CCC().a, CCC().b)
