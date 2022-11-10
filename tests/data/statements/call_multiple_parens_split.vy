@external
def test():
    return xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx((((((((((((((((((((((((((((a))))))))))))))))))))))))))))((b(c)))(d)((((((((((((((((((((((((e))))))))))))))))))))))))()
    return xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx((((((((((((((((((((((((((((a,))))))))))))))))))))))))))))((b(c,)))(d,)((((((((((((((((((((((((e,))))))))))))))))))))))))()
# output
@external
def test():
    return xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
        (((((((((((((((((((((((((((a)))))))))))))))))))))))))))
    )(
        (b(c))
    )(
        d
    )(
        (((((((((((((((((((((((e)))))))))))))))))))))))
    )()
    return xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(
        (((((((((((((((((((((((((((a,)))))))))))))))))))))))))))
    )(
        (
            b(
                c,
            )
        )
    )(
        d,
    )(
        (((((((((((((((((((((((e,)))))))))))))))))))))))
    )()
