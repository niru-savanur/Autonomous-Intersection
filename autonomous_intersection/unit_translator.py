def kmh_to_pixel_per_step(value: int, pixels_per_meter: int, steps_per_seconds: int) -> int:
    steps = 60 * 60 * steps_per_seconds
    pixels = 1000 * pixels_per_meter
    return round(value * pixels / steps)
