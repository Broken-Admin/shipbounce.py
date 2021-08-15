def lerp(a, b, t):
    return (1 - t) * a + t * b

def inverse_lerp(a, b, v):
    return (v - a) / (b - a)