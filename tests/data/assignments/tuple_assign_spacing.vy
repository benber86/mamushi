@internal
def foo():
    a,b,c=self.bar()
    (a,b,c)=self.bar()
    a    ,     b     ,      c  =  self.bar()
    (  a  ,  b  ,  c  )   =   self.bar()
    _,_,a=self.bar()
    _,a,_=self.bar()
    (_,_,a)=self.bar()
    (_,a,_)=self.bar()
    _   ,    a   , _   =   self.bar()
    a   ,  _  ,  a  = self.bar()
    (  _   ,    a   , _  )  =   self.bar()
    (   a   ,  _  ,  a     )  = self.bar()
# output
@internal
def foo():
    a, b, c = self.bar()
    (a, b, c) = self.bar()
    a, b, c = self.bar()
    (a, b, c) = self.bar()
    _, _, a = self.bar()
    _, a, _ = self.bar()
    (_, _, a) = self.bar()
    (_, a, _) = self.bar()
    _, a, _ = self.bar()
    a, _, a = self.bar()
    (_, a, _) = self.bar()
    (a, _, a) = self.bar()
