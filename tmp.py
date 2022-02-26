from Classes.Message import Message
import numpy as np
# DeprecationWarning: `np.str` is a deprecated alias for the builtin `str`. To silence this warning, use `str` by itself. Doing this will not modify 
# any behavior and is safe. If you specifically wanted the numpy scalar type, use `np.str_` here.
# Deprecated in NumPy 1.20; for more details and guidance: https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
#   ("name", np.str),
# c:\Users\USER\Desktop\Cyber\PRJ\tmp.py:12: DeprecationWarning: `np.int` is a deprecated alias for the builtin `int`. To silence this warning, use `int` by itself. Doing this will not modify 
# any behavior and is safe. When replacing `np.int`, you may wish to use e.g. `np.int64` or `np.int32` to specify the precision. If you wish to review your current use, check the release note 
# link for additional information.
# Deprecated in NumPy 1.20; for more details and guidance: https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
#   ("age", np.int)

arr = np.array(
    [
        ("ran", 17),
        ("david", 18)
    ], 
    dtype=[
        ("name", (str, 11)),
        ("age", int)
    ]
)
print(arr["name"])