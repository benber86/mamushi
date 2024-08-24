from ..abc import efg


implements: xyz







implements: jkl


uses: rst
uses: rst



uses: rst


initializes: xyz[abc := abc]
initializes: xyz[abc := abc]




initializes: xyz[abc := abc]

initializes: xyz[abc := abc]



exports: (



    # @notice comment


                    abc.gef,

xyz.stu,
)
# output
from ..abc import efg

implements: xyz

implements: jkl

uses: rst
uses: rst

uses: rst

initializes: xyz[abc := abc]
initializes: xyz[abc := abc]

initializes: xyz[abc := abc]

initializes: xyz[abc := abc]

exports: (
    # @notice comment


    abc.gef,
    xyz.stu,
)
