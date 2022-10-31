@external
def foo(a:uint256 ,
 b: address    ,
        c    :  address[3],
  e  : address[3][2], f: ERC20,
  g:bool= True, h      : bool =    False, i: uint256 =  1000
     )->        uint256 :
   pass
# output
@external
def foo(
    a: uint256,
    b: address,
    c: address[3],
    e: address[3][2],
    f: ERC20,
    g: bool = True,
    h: bool = False,
    i: uint256 = 1000,
) -> uint256:
    pass
