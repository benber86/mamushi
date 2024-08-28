struct          MyStruct        :
        value1      :         int128
        value2       :        decimal

def foo():
    exampleStruct       : MyStruct  =    MyStruct (   {     value1  :  1    , value2  : 2.0 })
    exampleStruct:MyStruct=MyStruct({value1:1,value2:2.0})
# output
struct MyStruct:
    value1: int128
    value2: decimal


def foo():
    exampleStruct: MyStruct = MyStruct({value1: 1, value2: 2.0})
    exampleStruct: MyStruct = MyStruct({value1: 1, value2: 2.0})
