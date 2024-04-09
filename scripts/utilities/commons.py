def str_to_i(input: str) -> int:
    if input.startswith("0x"):
        return int(input, base=16)
    elif input.startswith("0X"):
        return int(input, base=16)
    elif input.startswith("0b"):
        return int(input, base=0)
    elif input.startswith("0B"):
        return int(input, base=0)
    else:
        return int(input)
