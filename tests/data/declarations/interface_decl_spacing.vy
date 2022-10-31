interface              ERC20      :
    def       transfer( _to     : address   , _amount  : uint256)   :    nonpayable
    def transferFrom(_from:address,_to:address,_amount:uint256):nonpayable
    def balanceOf(_user:address)->uint256:view
    def a(b: uint256,        d: uint256[2], e: uint256, f: uint256)     ->        uint256    :      view
# output
interface ERC20:
    def transfer(_to: address, _amount: uint256): nonpayable
    def transferFrom(_from: address, _to: address, _amount: uint256): nonpayable
    def balanceOf(_user: address) -> uint256: view
    def a(b: uint256, d: uint256[2], e: uint256, f: uint256) -> uint256: view
