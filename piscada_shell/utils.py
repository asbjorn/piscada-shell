
def convertToDegrees(v):
    """Convert to GPS degrees"""
    deg = v // 100
    min_ = v % 100
    deg = deg + min_ * 0.01 / 0.6
    return deg
