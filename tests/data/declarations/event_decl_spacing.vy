event             Event :
    a    : indexed ( address  )
    b:indexed(uint256)
    c: uint256
    d   : uint256[ 2 ]
    e: (uint256)
# output
event Event:
    a: indexed(address)
    b: indexed(uint256)
    c: uint256
    d: uint256[2]
    e: (uint256)
