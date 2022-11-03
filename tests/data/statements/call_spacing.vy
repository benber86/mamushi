@internal
def foo():
    self.test(0,value=10,gas=10+10,skip_contract_check=(a and b)or d)
    self.test  (0   ,   0   ,   0  ,  value = 10000 , gas = 100 + 1000)
    _response: Bytes[32] = raw_call(    in_coin,
    concat(
        method_id("transferFrom(address,address,uint256)"),
        convert(msg.sender,bytes32),
        convert(        self,bytes32),
        convert(amounts[i],bytes32),
    ),max_outsize=32,)
# output
@internal
def foo():
    self.test(0, value=10, gas=10 + 10, skip_contract_check=(a and b) or d)
    self.test(0, 0, 0, value=10000, gas=100 + 1000)
    _response: Bytes[32] = raw_call(
        in_coin,
        concat(
            method_id("transferFrom(address,address,uint256)"),
            convert(msg.sender, bytes32),
            convert(self, bytes32),
            convert(amounts[i], bytes32),
        ),
        max_outsize=32,
    )
